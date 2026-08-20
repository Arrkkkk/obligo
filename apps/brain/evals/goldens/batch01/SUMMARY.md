# Batch 1 — close-out

**Guideline version:** v0.17 · **Seed:** `20260817` (reviewer-held) · **Pool:** 1,547 segments (408 hard, 1,139 standard)

## Outcome

| | |
| :--- | ---: |
| Items locked | **10** |
| Exclusions logged | **17** |
| Candidates walked | **27** |
| **Acceptance rate** | **37%** |
| Stratum split | 3 hard / 7 standard (on target) |

## Items

| item_id | segment | modality | action | known_gap | conf. |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `C03-01` | C03-192 | MUST | PROVIDE | — | AMBIGUOUS |
| `C03-02` | C03-192 | MUST | PROVIDE | `compound_action` | AMBIGUOUS |
| `C03-03` | C03-192 | MUST | MAINTAIN | — | CONFIDENT |
| `C11-01` | C11-094 | MUST | TRANSFER | — | AMBIGUOUS |
| `C17-01` | C17-021 | MUST | ENSURE | `mutual_obligation` | AMBIGUOUS |
| `C17-02` | C17-066 | MUST | PROCURE | `within_preposition` | AMBIGUOUS |
| `C22-01` | C22-048 | MUST | NOTIFY | — | AMBIGUOUS |
| `E01-01` | E01-047 | MUST_NOT | WAIVE | `unless_unsupported` | AMBIGUOUS |
| `E03-01` | E03-005 | MUST | PROVIDE | `redacted_value` | AMBIGUOUS |
| `E07-01` | E07-010 | MUST | MAINTAIN | — | CONFIDENT |

## Six structural categories discovered

Every one came from a real drawn segment, with the motivating sentence recorded in the rule:

| Category | Rule | Motivating case |
| :--- | :--- | :--- |
| `unless_unsupported` | §8.2 | `E01-047` — meaning carried by an `unless` v1 cannot parse |
| `redacted_value` | §8.1 | `E03-005` — clause survives, value withheld |
| `redacted_clause` | §3.7.1 | whole clause withheld; ground truth **unknowable**, leaves both denominators |
| `compound_action` | §8.3 | `C03-192` — *provide … and keep current*, one indivisible object |
| `mutual_obligation` | §8.4 | `C17-021` — reciprocal duty, second direction unrepresentable |
| `within_preposition` | §8.6 | `C17-066` — bare numeral, rejected preposition (`following`/`after`/`from`) |

Plus §3.5.1 (joint obligors → `obligor_accept_set`, deliberately **not** a gap) and §2.3 (PII redaction).

## The finding that matters most

**5 of 10 items carry a gap tag.** Four of them — `unless_unsupported`, `redacted_value`,
`mutual_obligation`, `within_preposition` — **cannot compile to a fully-correct IR by
construction**, regardless of extraction quality: the IR has nowhere to put a carve-out, a
withheld value, a reciprocal duty, or a rejected preposition.

**If that ~40% rate holds, §21's criterion 2 (Tier-2 fully-correct ≥80%) is arithmetically
unreachable.** This is a Phase 4 *scope* finding, not an extraction-quality one. It needs
its own conversation once batch 2 either confirms or refutes the rate.

Supporting measurements, all pool-wide rather than extrapolated from the 10 items:
`within N <unit>` is followed by `of` 40× against `after`/`from`/`following` 59×; redactions
appear in 96 segments (155 embedded, 85 whole-clause); vague temporal qualifiers 12%;
efforts qualifiers 3%.

## Pace — and why the headline is misleading

**814 min wall-clock, ≈90 min/item.** Dominated by reviewer turnaround (20 round trips),
not annotation work. It measures this conversation, not the process.

The forecasting number is the **37% acceptance rate**: ~2.7 candidates assessed per item,
so ~243 candidates for the remaining 90 items.

**No revised total estimate is recorded here, deliberately.** Batch 1 was discovery-heavy —
most of its 11 reviewer rulings *created* rules (§8.1–§8.6, §3.5.1, §3.7.1, §2.3) that later
batches only apply. Batch 2 is the second calibration point; the schedule gets revised with
two real numbers, not one.

## Open before the §10 freeze (after batch 3)

- `C03-02` — compound-action clause count (`DRAFTER_JUDGMENT_PENDING_REVIEW`)
- `C11-01` — non-party human obligor (*"the executor, administrator, or personal representative"*); no rule covers this
- §8.3's **split branch is untested** — its only candidate (`E07-010` sentence 3) failed on the obligor first
- **Document concentration:** `C03` supplied 3 of 10 items, all from one segment. The draw was fair; the sample is still narrow
- **Corpus artifacts:** 7.0% of pool segments carry page headers, address blocks or divider runs — *not* difficulty-correlated (hard 1.2%, standard 9.1%), and 73 of 101 are CUAD's own `Source:` footers, present in the raw text
