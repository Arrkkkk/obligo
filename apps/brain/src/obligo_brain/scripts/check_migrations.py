"""Fails loudly when a Flyway migration in apps/core's migration directory
has not actually been applied to the database DATABASE_URL points at.

CLAUDE.md's carried-forward debt list names the exact gap this closes:
`V17__create_agent_runs.sql` sat merged-but-unapplied for a whole Phase 4
checkpoint with nothing local catching it -- discovered only when the next
checkpoint's Flyway run reported "Current version: 16" and migrated 17 and
18 together. `ci-brain.yml` would always have applied it eventually (it
runs Flyway before its own tests on every push), so the gap was
specifically local: `make dev` never migrates and there was no other local
check. `make check-migrations` (and `make dev`'s own dependency on it) now
runs this.

Deliberately read-only: this NEVER calls Flyway's `migrate` command, only
`info`. Its job is to report drift, not fix it -- fixing it is
`flyway migrate` (the exact recipe `ci-brain.yml`'s "Apply apps/core
Flyway migrations" step already runs), not something this script does on
its own authority.

Reuses `ci-brain.yml`'s exact Flyway CLI version pin (10.10.0, see that
workflow's own comment on how to check apps/core's actually-resolved
Flyway version and update both together if it drifts) and its documented
reason for a standalone CLI rather than a Gradle build: apps/brain owns no
migrations itself, so no JDK/Gradle is needed just to check apps/core's
migration state -- a JRE is still required for the Flyway CLI jar itself,
same as that workflow already assumes. Downloads to the same conventional
path (`/tmp/flyway-cli/flyway-<version>`) `ci-brain.yml`'s own "Cache
Flyway CLI" step already primes, so a CI invocation of this script placed
after that workflow's "Apply apps/core Flyway migrations" step reuses the
already-downloaded binary rather than fetching a second copy; a fresh
local `make check-migrations` run downloads it on first use, the same as
that workflow's own cache-miss path.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

# Must track ci-brain.yml's own pin exactly -- see that workflow's comment
# on how to check apps/core's actual resolved Flyway version and update
# both together if it drifts.
FLYWAY_VERSION = "10.10.0"
FLYWAY_HOME = Path(f"/tmp/flyway-cli/flyway-{FLYWAY_VERSION}")
FLYWAY_URL = (
    "https://repo1.maven.org/maven2/org/flywaydb/flyway-commandline/"
    f"{FLYWAY_VERSION}/flyway-commandline-{FLYWAY_VERSION}.tar.gz"
)

# Relative to cwd, matching ci-brain.yml's own "-locations=filesystem:..."
# string exactly rather than computing an absolute path from __file__ --
# every caller of this script (the Makefile target, ci-brain.yml, pytest)
# already runs from the repo root, the same assumption that workflow's own
# recipe already makes.
MIGRATIONS_DIR = "apps/core/src/main/resources/db/migration"

# States Flyway's own `info` command can report for a migration that is
# NOT cleanly and currently applied. "Success" (and its baseline variant)
# is the only state that means "actually applied, matches what's in the
# repo." Everything else is drift of one kind or another: Pending (this
# repo's migration hasn't reached the database yet -- V17's exact failure
# mode), Future (the database has a migration this checkout doesn't, e.g.
# a stale checkout), Ignored/Outdated/Failed/Missing (a real problem
# Flyway itself is flagging).
_DRIFT_STATES = frozenset({"Pending", "Future", "Ignored", "Outdated", "Failed", "Missing"})

# Same format DatabaseConnectionDetails.parse() (Java side) and
# ci-brain.yml's own inline bash both assume: no URL-decoding of the
# password, `postgresql://user:password@host[:port]/db[?query]`.
_DATABASE_URL_RE = re.compile(
    r"^postgresql://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/([^?]+)(?:\?(.*))?$"
)


class MigrationDriftError(Exception):
    """Raised for a configuration/parse problem this script can't recover
    from on its own -- distinct from actual migration drift, which is
    reported via a nonzero exit rather than an exception (main() is the
    only caller that needs to distinguish "couldn't check" from "checked,
    found drift").
    """


def _download_flyway() -> Path:
    binary = FLYWAY_HOME / "flyway"
    if binary.is_file() and os.access(binary, os.X_OK):
        return binary

    FLYWAY_HOME.parent.mkdir(parents=True, exist_ok=True)
    archive_path = FLYWAY_HOME.parent / "flyway.tar.gz"
    urllib.request.urlretrieve(FLYWAY_URL, archive_path)  # noqa: S310 -- trusted, pinned Maven Central URL
    with tarfile.open(archive_path) as tf:
        tf.extractall(FLYWAY_HOME.parent)  # noqa: S202 -- trusted, pinned archive from the URL above

    if not binary.is_file():
        raise MigrationDriftError(f"Flyway CLI download did not produce {binary}")
    binary.chmod(0o755)
    return binary


def _owner_flyway_args() -> list[str]:
    """Parses DATABASE_URL the same way ci-brain.yml's inline bash recipe
    does -- same format assumption, no URL-decoding of the password.
    Reads directly from the process environment rather than from `.env`:
    the Makefile target sources `.env` before invoking this script for
    local dev, and ci-brain.yml exports these as real workflow env vars,
    so this script stays agnostic to which one supplied them.
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise MigrationDriftError("DATABASE_URL is not set")

    match = _DATABASE_URL_RE.match(database_url)
    if not match:
        raise MigrationDriftError(f"could not parse DATABASE_URL: {database_url!r}")
    user, password, host, port, dbname, query = match.groups()

    jdbc_url = f"jdbc:postgresql://{host}"
    if port:
        jdbc_url += f":{port}"
    jdbc_url += f"/{dbname}"
    if query:
        jdbc_url += f"?{query}"

    # Referenced by migration placeholders (V2 onward) the same way
    # ci-brain.yml's own `migrate` invocation supplies them -- `info` still
    # needs them to compute correct checksums against the migration files,
    # same args as that workflow's `migrate` step, different final command.
    app_db_password = os.environ.get("APP_DB_PASSWORD", "")
    brain_db_password = os.environ.get("BRAIN_DB_PASSWORD", "")

    return [
        f"-url={jdbc_url}",
        f"-user={user}",
        f"-password={password}",
        f"-locations=filesystem:{MIGRATIONS_DIR}",
        f"-placeholders.app_db_password={app_db_password}",
        f"-placeholders.brain_db_password={brain_db_password}",
    ]


def parse_flyway_info_json(raw: str) -> list[dict]:
    """Verified against a real `flyway info -outputType=json` run against
    the dev Neon branch before being trusted here (not guessed at): the
    top-level payload has a `migrations` key, a list of dicts each
    carrying at least `version`/`description`/`state`.
    """
    payload = json.loads(raw)
    migrations = payload.get("migrations")
    if not isinstance(migrations, list):
        raise MigrationDriftError(f"unexpected `flyway info -outputType=json` shape: {raw!r}")
    return migrations


def find_drifted(migrations: list[dict]) -> list[dict]:
    """Pure decision logic, kept separate from everything above it so it's
    testable against a recorded fixture with no Flyway binary, no
    network, and no database required at all.
    """
    return [m for m in migrations if m.get("state") in _DRIFT_STATES]


def main() -> int:
    try:
        binary = _download_flyway()
        args = _owner_flyway_args()
    except MigrationDriftError as exc:
        print(f"check-migrations: {exc}", file=sys.stderr)
        return 1

    proc = subprocess.run(
        [str(binary), *args, "-outputType=json", "info"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print("check-migrations: `flyway info` itself failed:", file=sys.stderr)
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        return 1

    try:
        migrations = parse_flyway_info_json(proc.stdout)
    except MigrationDriftError as exc:
        print(f"check-migrations: {exc}", file=sys.stderr)
        return 1

    drifted = find_drifted(migrations)
    if drifted:
        print("check-migrations: migration drift detected -- not every migration is applied:")
        for m in drifted:
            print(f"  V{m.get('version')} {m.get('description')}: {m.get('state')}")
        print(
            "Run the Flyway migrate recipe (ci-brain.yml's \"Apply apps/core Flyway "
            "migrations\" step) against this database before continuing."
        )
        return 1

    print(f"check-migrations: {len(migrations)} migrations, all applied cleanly. No drift.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
