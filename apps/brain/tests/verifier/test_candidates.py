"""verifier/candidates.py -- the conflict-candidate set (blueprint §6.7,
§0.2 gap 5; scoping conversation §1-§2). No DB, no Z3 -- pure function
tests only.
"""

from __future__ import annotations

from obligo_brain.compiler import ast
from obligo_brain.verifier import candidates
from obligo_brain.verifier.candidates import (
    BOTH_ABSTAIN,
    NO_PARTY_OVERLAP,
    NO_TEMPORAL_OVERLAP,
    OBJECT_CLASS_MISMATCH,
    select_candidates,
)
from tests.verifier.helpers import (
    CUSTOMER,
    OTHER_VENDOR,
    VENDOR,
    by,
    during,
    obligation,
    relative,
    within,
)


# -- clause (a): object class -----------------------------------------------


def test_object_class_mismatch_excludes_confidentiality_from_payment():
    # Revision 2 §2.1's worked exclusion: reciprocal parties, overlapping
    # temporal scope, different object class -- (a) is the only clause that
    # separates them.
    confidentiality = obligation(
        modality="MUST_NOT", action="DISCLOSE", object_class="confidential_information",
        object_text="Confidential Information", obligor=VENDOR, obligee=CUSTOMER, temporal=None,
    )
    payment = obligation(
        modality="MUST", action="PAY", object_class="fees", object_text="the Fees",
        obligor=CUSTOMER, obligee=VENDOR, temporal=by("2027-03-01"),
    )
    selection = select_candidates(confidentiality, [payment])
    assert selection.candidates == ()
    assert selection.excluded[0].reason == OBJECT_CLASS_MISMATCH


def test_object_class_match_is_case_and_whitespace_insensitive():
    a = obligation(modality="MUST", action="DELETE", object_class="Customer_Data", temporal=None)
    b = obligation(modality="MUST_NOT", action="DELETE", object_class=" customer_data ", temporal=None)
    selection = select_candidates(a, [b])
    assert len(selection.candidates) == 1


def test_object_class_over_broad_admits_unrelated_subject_matter():
    # Revision 2 §2.4's named residual risk, confirmed rather than assumed:
    # identical class string, genuinely unrelated real-world subject matter
    # (EU customer records vs US employee records) is still admitted as a
    # candidate -- this is the documented cost of an open, string-matched
    # taxonomy, not a bug.
    eu_customers = obligation(
        modality="MUST", action="DELETE", object_class="personal_data",
        object_text="EU Customer Personal Data", temporal=None,
    )
    us_employees = obligation(
        modality="MUST_NOT", action="DELETE", object_class="personal_data",
        object_text="US Employee Records", temporal=None,
    )
    selection = select_candidates(eu_customers, [us_employees])
    assert len(selection.candidates) == 1
    # raw_text is preserved so a human can disambiguate downstream, per
    # ObjectRef's own traceability purpose (SPEC.md §5).
    assert selection.candidates[0].obligation.object.raw_text == "US Employee Records"


# -- clause (b): party overlap -------------------------------------------


def test_party_overlap_in_reversed_roles_is_admitted():
    # Deliberately *not* obligor-identity -- {obligor, obligee} overlap in
    # either role, per scoping conversation §1.3.
    a = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="x", obligor=VENDOR, obligee=CUSTOMER, temporal=None)
    b = obligation(modality="MUST", action="PAY", object_class="x", obligor=CUSTOMER, obligee=VENDOR, temporal=None)
    selection = select_candidates(a, [b])
    assert len(selection.candidates) == 1
    assert selection.candidates[0].party_match_basis == "PARTY_ID"


def test_no_party_overlap_excludes():
    a = obligation(modality="MUST", action="DELETE", object_class="x", obligor=VENDOR, obligee=CUSTOMER, temporal=None)
    b = obligation(modality="MUST_NOT", action="DELETE", object_class="x", obligor=OTHER_VENDOR, obligee=CUSTOMER, temporal=None)
    # obligee overlaps (CUSTOMER) but that's still an overlap under (b) --
    # construct a genuinely disjoint pair instead.
    b2 = obligation(
        modality="MUST_NOT", action="DELETE", object_class="x",
        obligor=OTHER_VENDOR, obligee=ast.UnresolvedParty(alias="Nobody"), temporal=None,
    )
    selection = select_candidates(a, [b2])
    assert selection.candidates == ()
    assert selection.excluded[0].reason == NO_PARTY_OVERLAP


def test_alias_basis_never_matches_resolved_party_by_text():
    # scoping conversation §1.3: an UnresolvedParty alias is never matched
    # against a ResolvedParty's canonical_name.
    resolved_vendor = VENDOR  # canonical_name == "Acme Vendor Corp."
    unresolved_same_text = ast.UnresolvedParty(alias="Acme Vendor Corp.")
    a = obligation(modality="MUST", action="DELETE", object_class="x", obligor=resolved_vendor, obligee=CUSTOMER, temporal=None)
    b = obligation(modality="MUST_NOT", action="DELETE", object_class="x", obligor=unresolved_same_text, obligee=CUSTOMER, temporal=None)
    selection = select_candidates(a, [b])
    # obligee=CUSTOMER on both sides still overlaps, so this pair IS a
    # candidate -- but via the obligee match, not an obligor alias/resolved
    # text collision.
    assert len(selection.candidates) == 1
    assert selection.candidates[0].party_match_basis == "PARTY_ID"


def test_alias_basis_reported_when_match_is_alias_only():
    alice = ast.UnresolvedParty(alias="Vendor")
    a = obligation(modality="MUST", action="DELETE", object_class="x", obligor=alice, obligee=CUSTOMER, temporal=None)
    b = obligation(modality="MUST_NOT", action="DELETE", object_class="x", obligor=ast.UnresolvedParty(alias="vendor"), obligee=ast.UnresolvedParty(alias="Nobody"), temporal=None)
    selection = select_candidates(a, [b])
    assert len(selection.candidates) == 1
    assert selection.candidates[0].party_match_basis == "ALIAS"


# -- clause (c): temporal overlap, ABSTAIN handling --------------------------


def test_no_temporal_overlap_excludes():
    a = obligation(modality="MUST", action="DELIVER", object_class="x", temporal=during("2027-01-01", "2027-01-31"))
    b = obligation(modality="MUST_NOT", action="DELIVER", object_class="x", temporal=during("2027-06-01", "2027-06-30"))
    selection = select_candidates(a, [b])
    assert selection.candidates == ()
    assert selection.excluded[0].reason == NO_TEMPORAL_OVERLAP


def test_one_side_abstaining_still_admits_if_other_clauses_pass():
    # Only ONE side abstains (WITHIN's trigger never resolves) -- treated as
    # overlapping, and clause (d) only excludes when BOTH abstain.
    a = obligation(modality="MUST", action="NOTIFY", object_class="x", temporal=within(5, "d", "a Security Incident"))
    b = obligation(modality="MUST_NOT", action="NOTIFY", object_class="x", temporal=during("2027-01-01", "2027-12-31"))
    selection = select_candidates(a, [b])
    assert len(selection.candidates) == 1


def test_both_sides_abstaining_excludes_via_clause_d():
    a = obligation(modality="MUST", action="NOTIFY", object_class="x", temporal=within(5, "d", "a Security Incident"))
    b = obligation(modality="MUST_NOT", action="NOTIFY", object_class="x", temporal=relative("BEFORE", "termination"))
    selection = select_candidates(a, [b])
    assert selection.candidates == ()
    assert selection.excluded[0].reason == BOTH_ABSTAIN


# -- group_candidate_sets: connected components -----------------------------


def test_group_candidate_sets_n_way_connects_through_shared_hub():
    # Example B's shape: Q pairs with R1 and with R2, but R1 and R2 don't
    # pair with each other directly (disjoint windows) -- all three must
    # still end up in one component, connected through Q.
    q = obligation(modality="MUST", action="DISCLOSE", object_class="ci", temporal=during("2027-01-01", "2027-12-31"))
    r1 = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="ci", temporal=during("2027-01-01", "2027-06-30"))
    r2 = obligation(modality="MUST_NOT", action="DISCLOSE", object_class="ci", temporal=during("2027-07-01", "2027-12-31"))

    groups = candidates.group_candidate_sets([q, r1, r2])
    assert len(groups) == 1
    assert set(id(o) for o in groups[0]) == {id(q), id(r1), id(r2)}


def test_group_candidate_sets_omits_singletons():
    lonely = obligation(modality="MUST", action="DELETE", object_class="only_this_one", temporal=None)
    unrelated = obligation(modality="MUST", action="PAY", object_class="fees", temporal=None)
    groups = candidates.group_candidate_sets([lonely, unrelated])
    assert groups == []


def test_group_candidate_sets_separates_unconnected_pairs_into_distinct_groups():
    a1 = obligation(modality="MUST", action="DELETE", object_class="x", temporal=None)
    a2 = obligation(modality="MUST_NOT", action="DELETE", object_class="x", temporal=None)
    b1 = obligation(modality="MUST", action="PAY", object_class="fees", temporal=None)
    b2 = obligation(modality="MUST_NOT", action="PAY", object_class="fees", temporal=None)
    groups = candidates.group_candidate_sets([a1, a2, b1, b2])
    assert len(groups) == 2
    group_ids = {frozenset(id(o) for o in g) for g in groups}
    assert group_ids == {frozenset({id(a1), id(a2)}), frozenset({id(b1), id(b2)})}
