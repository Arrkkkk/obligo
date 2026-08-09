"""Obligation IR grammar version.

Matches packages/ir-spec/schema/obligation-ir.schema.json's `grammar_version`
const. A grammar bump (new modality, new temporal form, the exception
construct) is a 2.0.0-class change, per packages/ir-spec/SPEC.md section 10
-- never bump this without also bumping the schema and re-running the
recompile job over affected obligations.
"""

GRAMMAR_VERSION = "1.0.0"
