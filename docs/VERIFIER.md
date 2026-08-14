# The Z3 verifier

Blueprint §6.7, §0.2 gap 5, §7.2's `verify_constraints` tool. Implements
half of Phase 4's stated thesis ("the differentiator is the compiler...
and the verifier" -- CLAUDE.md). This document is the narrative account of
`apps/brain/src/obligo_brain/verifier/`'s design; the module docstrings are
the implementation-level detail, and this file doesn't repeat them line by
line -- it's the "why," they're the "how."

Design was scoped in a dedicated conversation before any code was written,
per CLAUDE.md's own discipline for this phase. Every non-obvious decision
below traces back to that conversation and was explicitly approved before
implementation started, not decided unilaterally mid-build.

## Scope, precisely

Everything here operates on already-**typechecked** `ast.Obligation`
objects, in memory. `verify()` takes no `org_id`, opens no `tenant_scope()`,
makes no LLM call, writes nothing to any table (`findings`/
`verification_runs` from blueprint §8.2 don't exist -- there's no
`obligations` table for their `obligation_ids uuid[]` to cite, same
boundary as the obligations-persistence investigation in CLAUDE.md). It is
not wired into `run_pipeline()` -- verification is naturally per-org-corpus,
while the pipeline is per-segment.

Coverage is deliberately partial, and the partiality is load-bearing, not
a gap papered over. `symbols.resolve_trigger()` and `resolve_date()`
(compiler/symbols.py) always return `None` in this codebase today, so
`WITHIN`, `RELATIVE_TO_TRIGGER`, `EVERY`, and any `bd`-unit duration can
never lower to a concrete window -- they **abstain**. Only `BY` (with a
resolved date) and `DURING` (with two resolved dates) carry a usable
window. This shrinks as `sources.effective_date`, a jurisdiction/calendar,
and the defined-terms/event registry get built (all three already tracked
as debt in CLAUDE.md with named owning checkpoints) -- nothing in the
verifier needs to change when they do; more obligations will simply stop
abstaining.

## The conflict-candidate set

Blueprint's own words: "verify the affected sub-graph" was hand-waving
(§0.2 gap 5). The rule (`verifier/candidates.py`): two obligations are
candidates iff **all four** hold:

1. **Object class** -- exact match on the normalized class string.
2. **Party overlap** -- at least one of `{obligor, obligee}` overlaps, in
   either role. Deliberately *not* obligor-identity -- that requirement
   lives in the act key (§below), not here. A `ResolvedParty` matches by
   `party_id`; an `UnresolvedParty` matches by casefolded alias, tagged
   `party_match_basis` so a false positive from alias-collision is
   distinguishable in the run record from a `party_id`-certain one.
3. **Temporal overlap** -- windows overlap; an obligation whose temporal
   form can't be lowered (see "Scope" above) is treated as overlapping
   everything. Unknown must never collapse to "doesn't overlap," which
   would silently shrink the set.
4. **Verifiability** -- not both sides unlowerable (a pair of two
   abstentions can never produce a finding).

**The candidate set never decides a conflict -- it only decides what gets
solved.** This was checked concretely, not just argued: deleting clause 1
entirely and re-running the confidentiality/payment worked pair still
produces the correct SAT verdict, because object class is *also* part of
the act key the solver itself uses. The real discriminator lives in the
lowering, not the prefilter. The known cost of exact-string matching on an
open object-class taxonomy runs in **both** directions and both are
accepted, not hidden: a real conflict can be missed if two obligations use
different class strings for the same real-world thing (`confidential_information`
vs `confidential_info`), and a false positive can be admitted if two
obligations share a class string for genuinely unrelated subject matter
(`personal_data` covering both an EU customer DPA and a US employee
retention schedule). `ObjectRef.raw_text` is carried through to every
finding specifically so a human can tell the second case apart at a
glance. Closing the object-class taxonomy (packages/ir-spec/SPEC.md §12)
is real future work that improves both directions at once, since the same
string also feeds the act key.

`group_candidate_sets()` takes the connected components of the candidate
graph over a whole corpus -- the sets that actually get solved together.
This is what catches an n-way conflict where no single pair is
unsatisfiable but the group together is (worked example B below):
component membership is transitive, so three obligations pairwise-linked
only through a shared hub still end up in one solve.

A component larger than `MAX_CANDIDATE_SET` (50) is reported as scope-
exceeded rather than solved -- a set that large is itself a signal, not a
cost to push through regardless.

## The conflict condition

**A conflict is an empty *residual* feasible set for some single act, not
an empty pairwise intersection and not a subset check in either
direction.** Both surface predicates get real, satisfiable configurations
wrong:

- **Empty intersection is not "conflict."** Two disjoint `MUST DELIVER`
  windows (January, then June) never intersect and are perfectly
  satisfiable -- two duties to perform the same kind of act are two
  separate acts, not a shared performance.
- **Nonempty intersection is not "conflict" either.** A `MUST_NOT`
  window can *contain* a `MUST` window (unsatisfiable -- the duty has no
  room to avoid the prohibition) or merely *overlap* it partially
  (satisfiable -- a lawful window survives outside the overlap). Both
  have nonempty intersection; only one is a real contradiction.

For each performance variable `t_i` belonging to a MUST/SHOULD obligation
on act key `k`:

```
required window:    W_i
forbidden windows:  P_1, P_2, ...   (every MUST_NOT and every implied
                                     antagonism-prohibition sharing k)
feasible set:        F_i = W_i \ (P_1 u P_2 u ...)
CONFLICT   iff   F_i = empty
```

For the two-obligation case this reduces to a clean, testable statement:
**`MUST(W)` / `MUST_NOT(P)` is unsat iff `W ⊆ P`.** Z3 never computes this
as a Python set operation -- it falls out of ordinary conjunction/
disjunction over `t_i ∈ W_i` and `t_i ∉ P_j` for every prohibiting `P_j`.
`tests/verifier/test_properties.py` proves this via an independent,
purely-Python set-containment oracle checked against the real solver
verdict across hundreds of generated interval pairs, plus the weaker
(but true) corollary that a disjoint pair is never flagged.

### Act keys: why two MUSTs never share a performance variable

`act_key(obligation) = (party_key(obligor), action, norm(object.class_))`
-- the identical two functions the candidate filter's clauses 1/2 use, so
the prefilter and the solver's own notion of "same act" can never silently
drift apart from each other.

Every MUST/SHOULD obligation gets its own fresh Z3 `Int`, even when
several share an act key. Unifying them would turn ordinary supersession
(a later amendment's new deadline superseding an earlier SOW's) into a
fabricated contradiction -- named in the scoping conversation as the
single largest false-positive hazard, and closed by construction here, not
by a runtime check that could be forgotten.

### Conditions

Condition atoms lower to plain Z3 `Bool`s keyed by normalized raw text, so
the same atom text in two different obligations' conditions is the same Z3
variable -- this is what lets `IF "X"` in one obligation and `IF NOT "X"`
in another actually contradict each other. They are asserted as bare
literals (never used to *guard* the modal/window facts): this directly
implements "condition literals are assumed true" with no extra machinery.
If two conditions are genuinely opposed, that alone is unsat, independent
of any temporal fact. Deletion-based minimization is what tells a
condition-only core apart from a modal one.

A real, accepted limitation: only literal `X` vs `NOT X` over matching raw
text is detectable. `"terminates for cause"` and `"terminates for
convenience"` are different, mutually-exclusive real-world conditions that
this encoding cannot relate -- both get asserted true and no contradiction
is ever found between them. `Finding.condition_sensitive` is set whenever
a condition fact was load-bearing in a core, so the rendered sentence can
hedge ("...if [condition A] and [condition B] both hold") rather than
overclaim certainty.

### Multi-way conflicts are solved as a set, not pairwise

`unsat_explain.py` calls `solver.check()` once per candidate group, not
once per pair. Worked example B: `Q` (`MUST DISCLOSE` Jan-Dec), `R1`
(`MUST_NOT DISCLOSE` Jan-Jun), `R2` (`MUST_NOT DISCLOSE` Jul-Dec). `{Q,R1}`
alone is SAT (`R2` leaves the door open). `{Q,R2}` alone is SAT (`R1`
leaves the door open). Only `{Q,R1,R2}` together is UNSAT. A checker that
only ever examines pairs cannot find this; this is the concrete
justification for reaching for a solver at all rather than writing
pairwise rules in Python.

### Multiple independent conflicts, bounded

Every fact is asserted as `Implies(selector, constraint)`, with the
selector passed as a Z3 *assumption* per `check()` call rather than
permanently asserted -- this is what makes minimization and multi-core
enumeration both possible without `push`/`pop`: the same `Solver` is reused
for every call in a group, varying only which selectors are active. After
finding one minimal core, its labels are removed from the pool and the
remainder is re-checked; if that's unsat too, it's a genuinely independent
contradiction. Bounded at 5 cores total per group, split between two
passes (below) -- a candidate set producing more than that is itself a
signal worth a human look, not something to keep enumerating.

Deletion-based minimization processes labels in a fixed, deterministic
order (sorted by source span) so that when several minimal cores are
possible, the same one is found every time -- required for the
conflict-symmetry property and for reproducible eval numbers.

### Two severities, two passes

Pass 1 solves MUST/MUST_NOT facts only (severity `HIGH`). Pass 2 adds
SHOULD facts on top of whatever pass 1 left unresolved (severity
`ADVISORY`) -- `packages/ir-spec/SPEC.md` §2: SHOULD is "non-binding...
matters for risk scoring," so a SHOULD-involving conflict is real but
weaker, and must never be reported at the same severity as a MUST one.
`MAY` asserts nothing at all -- "a right you needn't exercise cannot be
breached" -- and is filtered out before candidate grouping even begins.

### Timeout

`Z3_TIMEOUT_MS = 120_000`, matching blueprint §4.2's own constant. Any
`check()` call returning `unknown` stops further core search in that
group and is surfaced as its own signal (`VerificationResult.
timed_out_groups`) -- never silently folded into a Finding that would read
as a confirmed conflict, and never silently claimed SAT (blueprint §4.2's
own degraded-mode rule for this failure).

## Conflict taxonomy

| Kind | Fires when | Notes |
| :--- | :--- | :--- |
| `MODAL_CONFLICT` | a MUST's feasible set is empty against one or more literal MUST_NOTs on the same act key | primary class |
| `ANTAGONISTIC_ACTION` | same, but at least one prohibiting window came from the antagonism table (below), not a literal MUST_NOT | the product's own headline example (retention vs. deletion) |
| `TEMPORAL_IMPOSSIBILITY` | an obligation's own `DURING` bounds are reversed (`end < start`) | detected in pure Python (`intervals.is_empty`), never through Z3 -- routing a self-contained defect through the solver risks misattributing it to whatever it happened to be grouped with |
| `CONDITION_CONTRADICTION` | a minimal core consists only of condition facts, no window/prohibition facts at all | weak by construction -- see the condition limitation above |
| *(numeric/cap mismatch)* | -- | **not representable in IR v1.** No amount/currency/cap field exists anywhere in the IR. Declared out of scope with the reason, not silently dropped. |

## The action-antagonism table

`DELETE` and `RETAIN` are different actions in the closed 34-verb
taxonomy, so a literal `MUST RETAIN` / `MUST DELETE` pair -- the product's
own headline "a retention policy contradicted a deletion promise" example
-- never shares an act key and a plain modal check never fires on it. The
antagonism table (`verifier/actions.py`) closes this gap with two
deliberately hand-authored, one-directional entries:

```
RETAIN   -> DELETE
WITHHOLD -> DISCLOSE
```

**One-directional, not a symmetric pair set, and that's a real semantic
distinction.** `RETAIN`/`WITHHOLD` describe a continuous state held
throughout a window ("retain during 2027" is true at every instant of
2027) -- the same shape as a `MUST_NOT`'s own forbidding window, so a
`MUST` on the continuous side genuinely forbids its antagonist for the
whole window it covers. `DELETE`/`DISCLOSE` describe a point-in-time act
performed once within a window ("delete by March 1" happens at some
instant). The reverse doesn't hold: "must delete by March 1" does not
forbid retaining right up until the deletion. Only the continuous side
generates an implied prohibition.

Seeded strictly, matching `ir_compile.py`'s own "strict over loose"
posture: only pairs unambiguous by the dictionary meaning of the verbs are
included. Plausible-but-arguable pairs (`TERMINATE`/`MAINTAIN`,
`TRANSFER`/`RETAIN`) are deliberately left out. Adding a pair is a real
judgment call and belongs in this document with its own reasoning, never
an LLM call (Standing Principle 2 -- it determines a finding's
correctness, not a draft) and never a silent addition.

## Explanation: deterministic, never an LLM call

Approved as proposed, without qualification: rendering is template-based
per finding kind, with every fact in the sentence drawn directly from the
minimal core's own labels (obligor name, action, object phrase, dates).
Blueprint §6.7 itself: "an LLM may *polish* the prose but the *claim*
comes from the core. Never let the model invent the reason." Standing
Principle 2 settles it independently -- the sentence is the system's
assertion about a customer's real contracts, so it's correctness-
determining output, not a draft, and a model asked to reword "must not
disclose" has exactly the same failure mode the span-grounding Tier-C
decision rejected fuzzy matching over (`"shall"` -> `"shall not"` is a ~2%
edit that inverts a clause's meaning) -- one layer downstream, with no
grounding gate behind it to catch the result.

If a polish step is ever added, the design should be: render
deterministically, optionally polish, then verify the polished sentence
still contains the same party names, dates, and modality tokens or discard
it and ship the template -- the same "make disobeying the instruction
inert" pattern `graphs/repair.py` already uses for span text. Not built;
the prompt registry's `conflict_explain/v1.yaml` slot (blueprint §13.5)
stays empty.

## Known, accepted limitations

- **`WITHIN`, `RELATIVE_TO_TRIGGER`, `EVERY`, and every `bd`-unit duration
  always abstain** -- their trigger or calendar dependency never resolves
  in this codebase today (see "Scope" above). A real conflict expressed
  only in these forms is currently invisible to the verifier. Closes as
  the trigger registry and business-day calendar get built.
- **Object-class matching is exact-string, open-vocabulary** -- both a
  recall hazard (synonymous classes never connect) and a precision hazard
  (same string, unrelated subject matter). See "The conflict-candidate
  set" above.
- **Condition contradiction detection is limited to literal negation over
  matching raw text** -- semantically opposed but differently-worded
  conditions are invisible to it.
- **No numeric/cap conflict class** -- IR v1 has no amount/currency field.
- **The action-antagonism table is two pairs**, not a general theory of
  which verbs oppose which. Extending it is a real, individually-justified
  decision, not automatic.
- **`ir_hash`-keyed verdict caching (blueprint §6.7) is not built** --
  blocked on `ir_hash` itself, which needs the normalizer (also not
  built). `verify()` takes no cache key and computes everything fresh
  every call.
- **Not persisted anywhere.** `findings`/`verification_runs` don't exist;
  `verify()`'s result lives in memory only, for the same reason
  `PipelineResult.typechecked` does (CLAUDE.md's obligations-persistence
  investigation). Building the review-workflow write path (`findings`
  rows, "mark false positive" -> a `corrections` row) is Phase 5 scope.

## Files

```
apps/brain/src/obligo_brain/verifier/
  intervals.py       Temporal -> Window | ABSTAIN
  actions.py         antagonism table + verb-gloss function
  candidates.py       the conflict-candidate set + connected-component grouping
  z3_lowering.py      obligation set -> tracked Z3 assertions
  unsat_explain.py    core minimization, multi-core enumeration, classification, rendering
  verify.py           entry point: verify(obligations) -> VerificationResult
```
