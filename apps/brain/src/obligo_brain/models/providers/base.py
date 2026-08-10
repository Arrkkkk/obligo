"""The adapter interface every chat-completion provider implements
(blueprint §13.1 rule 2: "every model sits behind an adapter interface...
anything model-specific outside brain/models/ is a design defect").

Deliberately a `Protocol` over a bare callable signature, not an ABC with a
`.complete()` method -- providers/groq.py's `complete()` is a plain module
function (same style as platform/storage/supabase.py), and a Protocol lets
that function satisfy ChatModel structurally with no wrapper class. This
also makes test doubles trivial: any function with this signature (a
lambda, a cassette-backed stub) *is* a ChatModel, no fake class hierarchy
required.

Only one provider (Groq) is implemented at this checkpoint. Gemini/local
fallback (§6.10's router table) are model-router scope, not built here --
this Protocol is what makes adding them later a new module implementing
the same shape, not a refactor of every caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ChatCompletion:
    content: str
    model_id: str
    input_tokens: int
    output_tokens: int
    latency_ms: float


class ChatModel(Protocol):
    def __call__(
        self, *, system: str, user: str, model_id: str, temperature: float = 0.0
    ) -> ChatCompletion: ...
