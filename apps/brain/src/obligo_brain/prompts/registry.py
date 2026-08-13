"""Versioned prompt loading (CLAUDE.md's non-negotiable rule: "prompts are
versioned files, not inline strings... never edited in place -- bump the
version"; blueprint §13.5). Two of the blueprint's three stated shapes for
this (§6.1's `templates/*.jinja` + `versions.yaml`, §13.5's
`prompts/extraction/v1.yaml` + `registry.yaml`, §22.2's tree comment
"versioned YAML + registry.yaml") agree on YAML-embedded templates with a
registry.yaml -- that's what's built here. No jinja2 dependency: the only
templating this checkpoint needs is two placeholders in a user message
(`{nonce}`, `{segment_text}`), which `str.format` already does, and
CLAUDE.md's "ask first" rule on new dependencies plus Standing Principle 5
("prefer deleting a technology over adding one") both argue against
pulling in a templating engine for that.

registry.yaml maps task -> environment -> active version. Changing a
prompt is: add a new prompts/<task>/vN.yaml file (never edit an existing
one -- old versions stay for reproducibility, matching Flyway's "migrations
are immutable" discipline), then flip registry.yaml. Rollback = flip it
back. No redeploy, no code change (§13.5).
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from pathlib import Path

import yaml

_PROMPTS_DIR = Path(__file__).parent
_REGISTRY_PATH = _PROMPTS_DIR / "registry.yaml"


class PromptNotFoundError(Exception):
    """Raised when registry.yaml names a task/environment/version with no
    corresponding prompt file, or the task has no registry entry at all.
    """


@dataclass(frozen=True)
class Prompt:
    id: str
    version: str
    created: str
    system: str
    user_template: str
    model_constraints: dict
    expected_schema: str
    changelog: tuple[dict, ...]
    # SHA-256 of the raw, UNRENDERED template text (system + NUL +
    # user_template) -- identifies exactly which prompt bytes produced a
    # given agent_runs row, independent of which segment was substituted
    # into it. Per-call content variance is input_hash's job (extraction.py),
    # not this field's -- keeping the two separate is what lets
    # (prompt_hash, model_id) alone answer "did this call use the prompt
    # version we think it did," the reproducibility guarantee NFR-10 and
    # §13.5 both name.
    prompt_hash: str


def load(task: str, *, environment: str = "default") -> Prompt:
    registry = yaml.safe_load(_REGISTRY_PATH.read_text())
    try:
        version = registry[task]["environments"][environment]
    except (KeyError, TypeError) as exc:
        raise PromptNotFoundError(
            f"registry.yaml has no active version for task={task!r} environment={environment!r}"
        ) from exc

    prompt_path = _PROMPTS_DIR / task / f"{version}.yaml"
    if not prompt_path.exists():
        raise PromptNotFoundError(
            f"registry.yaml points task={task!r} environment={environment!r} at "
            f"version={version!r}, but {prompt_path} does not exist"
        )

    data = yaml.safe_load(prompt_path.read_text())
    system = data["system"]
    user_template = data["user_template"]
    prompt_hash = hashlib.sha256(f"{system}\x00{user_template}".encode()).hexdigest()

    return Prompt(
        id=data["id"],
        version=data["version"],
        created=data["created"],
        system=system,
        user_template=user_template,
        model_constraints=data["model_constraints"],
        expected_schema=data.get("expected_schema", ""),
        changelog=tuple(data.get("changelog", [])),
        prompt_hash=prompt_hash,
    )


def render(prompt: Prompt, *, segment_text: str) -> tuple[str, str]:
    """Returns (system, user). The structural enforcement of Standing
    Principle 4 ("never concatenate document text into a system prompt")
    lives entirely in this one line: `prompt.system` is returned completely
    unmodified, never passed through `.format()` or any other substitution
    -- so it is not merely policy that segment_text can't reach the system
    prompt, it's impossible by construction. Tests assert this directly
    (a canary string placed in segment_text never appears in the returned
    system value).

    The user message wraps segment_text in a nonce-delimited fence so a
    document cannot forge its own closing delimiter and make its content
    look like it ends before it does -- the system prompt (see
    extraction/v1.yaml) declares fenced content to be data, never
    instruction, per §17.5's defense-in-depth list. The fence is
    defense-in-depth, not the control; the real control is that nothing
    downstream of this call can mutate state without the grammar,
    typechecker, and grounder all agreeing first.
    """
    nonce = secrets.token_hex(8)
    user = prompt.user_template.format(nonce=nonce, segment_text=segment_text)
    return prompt.system, user


def render_repair(prompt: Prompt, *, segment_text: str, failures: str) -> tuple[str, str]:
    """The repair task's renderer (graphs/repair.py; blueprint §6.3 stage 3).

    A separate function rather than a generalized `render(prompt, **vars)`
    on purpose: render()'s guarantee above is a property of its *signature*
    as much as its body -- a caller physically cannot pass anything but
    segment_text, so the set of things that could ever reach a system prompt
    is enumerable by reading one line. Widening it to **kwargs would trade
    that for a convention. Each task gets its own explicitly-typed renderer;
    every one of them returns `prompt.system` completely unmodified, which
    is the invariant that actually matters (Standing Principle 4).

    `failures` is a JSON string this codebase builds from its own compiler
    diagnostics, but it embeds candidate fields that originated in the
    document, so it is treated as untrusted content and fenced with the same
    per-call nonce as segment_text. Note that str.format only scans the
    TEMPLATE for placeholders -- brace characters inside the substituted
    values are inert, so neither the document nor the diagnostic payload can
    introduce a new substitution point.
    """
    nonce = secrets.token_hex(8)
    user = prompt.user_template.format(
        nonce=nonce, segment_text=segment_text, failures=failures
    )
    return prompt.system, user
