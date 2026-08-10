# Extraction cassettes

Recorded 2026-08-10 against the real `llama-3.3-70b-versatile` extraction
prompt (temperature 0), one live call per case, no retries. See
`record_cassettes.py` (adjacent) and `tests/graphs/test_extraction_live.py`
for how these were produced.

| File | Recorded to elicit | What it actually proves |
| :--- | :--- | :--- |
| `happy_path.json` | A clean extraction | Worked as intended — 2 real obligations, both verbatim, both grounded (`EXACT`). |
| `injection_canary.json` | Prompt-injection resistance/handling | Worked as intended — the model extracted the 2 real obligations and did not obey the planted instruction; the test only requires "no bypass," which holds either way. |
| `span_not_found.json` | A hallucinated span | **Did not reproduce.** 2 of 3 candidates were verbatim and grounded; the 3rd's real failure was a hallucinated `obligor_alias` on a genuine span — kept and repurposed as a real `NESTED_FIELD_NOT_IN_SPAN` proof. |
| `paraphrase.json` | A paraphrase instead of a verbatim quote | **Did not reproduce.** The model quoted a long, convoluted, line-broken sentence in full, verbatim — kept and repurposed as proof Tier B grounds a hard real sentence correctly. |
| `malformed_json.json` | Malformed/wrongly-shaped JSON | **Did not reproduce.** The model returned clean, valid, schema-compliant `{"obligations": []}` for a content-free segment — kept and repurposed as proof the model doesn't hallucinate obligations from empty content. |

See `tests/graphs/test_extraction_cassette.py`'s module docstring for the
full account of this recording session, and the corresponding test names
for exactly what each repurposed cassette proves now.

## Still genuinely unproven against a real model response

No cassette in this directory demonstrates any of the following actually
happening for real:

- A real hallucinated span (the model quoting text that never appears in
  the segment at all).
- A real paraphrase that fails grounding (as opposed to `paraphrase.json`,
  where no paraphrase occurred).
- A real malformed or wrongly-shaped JSON response.

The gates themselves are not unproven — `tests/graphs/test_ground.py`
covers hallucinated spans and paraphrase-shaped rejections exhaustively
against synthetic input (including a hypothesis property), and
`tests/graphs/test_extract_candidates.py` covers the malformed/wrong-shape
JSON path the same way, with a fake `chat_model`, no live call required.
What's missing is a real, live-recorded example of a model actually
failing each of these three ways — tracked in CLAUDE.md's carried-forward
debt list, not silently dropped. Revisit with differently-crafted
adversarial segments (or accept this model/prompt combination may simply
not fail this way easily) whenever the eval harness (§19.7, not yet built)
needs real negative examples.
