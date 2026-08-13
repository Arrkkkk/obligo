"""check_migrations.py -- the migration-drift guard CLAUDE.md's debt list
names ("a startup or make step that fails loudly on pending migrations").

Two tiers: pure unit tests of the decision logic (parse_flyway_info_json,
find_drifted) against a recorded fixture shape, no Flyway binary, network,
or database required at all; and one real-Neon test that actually runs
main() end to end (downloads Flyway if needed, shells out to `flyway
info`) against the real dev branch, skipping cleanly if the required env
isn't set -- the same skip-if-unset discipline every other real-database
test in this repo already uses. That live test is the one that has to
pass for a real reason: it only asserts 0 if `flyway info` genuinely
reports every migration Success against whatever database DATABASE_URL
points at right now, not because the check was mocked or skipped.
"""

from __future__ import annotations

import json
import os

import pytest

from obligo_brain.scripts import check_migrations

_CLEAN_FIXTURE = json.dumps(
    {
        "migrations": [
            {"version": "1", "description": "create organizations", "state": "Success"},
            {"version": "2", "description": "create app role", "state": "Success"},
            {"version": "17", "description": "create agent runs", "state": "Success"},
            {"version": "18", "description": "create compile quarantine", "state": "Success"},
        ]
    }
)

# V17's real failure mode, reproduced as a fixture: merged into the repo,
# never applied. This is exactly the shape `flyway info` reported when the
# repair-loop checkpoint discovered it.
_PENDING_FIXTURE = json.dumps(
    {
        "migrations": [
            {"version": "1", "description": "create organizations", "state": "Success"},
            {"version": "16", "description": "create parties", "state": "Success"},
            {"version": "17", "description": "create agent runs", "state": "Pending"},
        ]
    }
)


def test_parse_flyway_info_json_extracts_the_migrations_list():
    migrations = check_migrations.parse_flyway_info_json(_CLEAN_FIXTURE)
    assert len(migrations) == 4
    assert migrations[0]["version"] == "1"


def test_parse_flyway_info_json_rejects_an_unexpected_shape():
    with pytest.raises(check_migrations.MigrationDriftError):
        check_migrations.parse_flyway_info_json(json.dumps({"not_migrations": []}))


def test_find_drifted_is_empty_when_every_migration_is_success():
    migrations = check_migrations.parse_flyway_info_json(_CLEAN_FIXTURE)
    assert check_migrations.find_drifted(migrations) == []


def test_find_drifted_catches_the_real_v17_failure_mode():
    migrations = check_migrations.parse_flyway_info_json(_PENDING_FIXTURE)
    drifted = check_migrations.find_drifted(migrations)
    assert [m["version"] for m in drifted] == ["17"]


def test_find_drifted_flags_every_non_success_state_not_only_pending():
    migrations = [
        {"version": "1", "description": "a", "state": "Success"},
        {"version": "2", "description": "b", "state": "Future"},
        {"version": "3", "description": "c", "state": "Ignored"},
        {"version": "4", "description": "d", "state": "Outdated"},
    ]
    drifted = check_migrations.find_drifted(migrations)
    assert [m["version"] for m in drifted] == ["2", "3", "4"]


@pytest.mark.skipif(
    not (
        os.environ.get("DATABASE_URL")
        and os.environ.get("APP_DB_PASSWORD")
        and os.environ.get("BRAIN_DB_PASSWORD")
    ),
    reason="DATABASE_URL/APP_DB_PASSWORD/BRAIN_DB_PASSWORD not set -- skipping real check",
)
def test_main_finds_no_drift_against_the_real_dev_branch():
    assert check_migrations.main() == 0
