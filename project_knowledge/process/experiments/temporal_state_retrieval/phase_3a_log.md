# Phase 3A — record-state metadata preparation and local freeze

Date: 26 October 2026.

Starting checkpoint: `e48acc6fc02840382b9d920621c88363f171028d`. Working branch: `temporal-state-retrieval-state-aware-v1`.

The frozen semantic baseline is retained as the control for a separate prospective record-state metadata experiment. The [preregistration candidate](phase_3_preregistration.md) limits the candidate to deterministic final evidence selection after unchanged semantic generation. It fixes the full eligible candidate pool, ties, six section rules, evaluation populations, success thresholds, negative-result handling and a payload boundary that keeps gold out of selection.

Direct reading of the permitted source records produced 18 document-level metadata candidates: four public demonstration records, seven synthetic records and seven private researcher-owned records. Six dates remain null; historical report function does not establish expiry, and final/current snapshot headings do not prove authoring chronology. No source text, frozen annotation, production component or baseline output was changed. Public schema, review checklist and checksum-manifest candidate accompany the metadata.

At the initial preparation stage, all metadata remained pending_researcher_review and the manifest was a review snapshot. The subsequent conditional confirmation and method audit are recorded below. The Phase 3 thresholds are explicitly distinguished from the unchanged legacy comparison-family criteria; no candidate execution or improvement is claimed.

No baseline, retrieval, embedding, LLM, OpenAI or summary work was performed. No participant study was reopened and no thesis was edited. Initial preparation stopped at review; the final audit below freezes only the documents and metadata, without implementation, commit or push.

## Static validation

All 32 new static validation tests passed. They cover the closed schema, pending status, prohibited target/result fields, missing/duplicate identities, categories, explicit dates, full corpus coverage, historical exclusion, fixed selection-contract declarations and checksum integrity. They do not run a retriever or test a selector implementation. The private seven-record candidate separately passed the same schema and direct source date/category/hash checks; its public checksum commitment matches and its file is ignored by Git.

All 75 pre-existing protected file fingerprints remained unchanged, including frozen gold, Phase 2 artifacts, production, existing tests/configuration, permitted source records and five thesis drafts. Real participant materials, caches, reviews and assignments were not opened or rehashed. New-test compilation, 11 local Markdown links, public privacy/credential/contact/path scans and whitespace checks passed. No private source-text overlap was found in the public candidate files. The validation process recorded zero network, forbidden runtime/model-import and protected-data-access attempts. No baseline or candidate performance was calculated; the latency threshold was derived only from the already frozen baseline median.

The initial public candidate consisted of eight new files, including its manifest, and one ignored private metadata file. These first-stage checks established a reviewable package rather than confirmation or permission to execute.

## Final method audit and conditional confirmation — 26 October 2026

Source inspection distinguished the retriever's default top_k=3 and helper's default limit=2 from the actual production call arguments: both are explicitly overridden with the full corpus chunk count. The outer two-item limit controls output only. All 24 saved request lists were reconciled by cardinality and identity without rerunning retrieval. The trace stores category-filtered query lists, whereas unfiltered counts are established from the source call chain and corpus manifest. Evaluation-only selected-first rankings are constructed afterwards and cannot substitute for those query lists. The original top_k=N is retained without expanding recall.

S3 Query 1 explicitly addresses current/still-in-use direction; Query 2 addresses superseded/replaced/non-current direction and also future work. The query-order rule is retained from that text, with no inference that a historical document proves supersession. S2/S4/S6 remain baseline. A closed selector_input schema and nested rejection tests enforce the minimal record_id-to-state mapping and exclude full metadata, rationale, dates, ordinals, target annotations and result fields. No selector algorithm was implemented.

All 73 static tests passed before the conditional freeze. Fuzhe Zhang's authorised confirmation is recorded with review date 2026-10-26 and version phase_3a_metadata_v1. The eight fields in every one of the 18 records remain identical to the reviewed candidate; only envelope version/status/review provenance changed. Public and private freeze manifests preserve predecessor commitments and current hashes. The public package still has eight files; private storage now also contains its freeze manifest.

Phase 3 and original Phase 1 success criteria are stored separately and both candidate outcomes remain not evaluated. Markdown uses 44.03 ms; JSON retains the exact double of the frozen production warm median. The audit changes no Phase 1/2 data, production, old tests/configuration or thesis bytes. Formal participant data was not accessed or rehashed. No retrieval, model, summary or API work occurred. At this audit checkpoint the local freeze was uncommitted; implementation and execution require separate authorisation.

## Publication preparation - 26 October 2026

The public [freeze manifest](../../../../tests/fixtures/temporal_state_metadata/freeze_manifest.json) now uses its final filename. Public references and the static manifest fixture have been updated, and the private manifest commits to the final public bytes. The 18 metadata records, researcher confirmation, selector rules and success criteria are unchanged. Publication is limited to the frozen design; implementation and candidate execution remain outside this phase.

Publication validation passed: 73 Phase 3A static tests in 0.16s, followed by one complete offline test run with 230 passed in 161.66s (0:02:41), with no failures or skipped tests. All 27 Python files compiled in memory, dependency consistency and whitespace checks passed, and all 16 local links in the public package resolved. Public privacy checks found no credentials, contact details, private paths or private source-text overlap. The 75 protected file hashes remained unchanged. The test process recorded zero external-network, model-artifact and real-participant-directory access attempts; its synthetic fixtures did not use real participant files. No baseline or candidate was run, no embedding model was loaded and no OpenAI request or new summary was generated.
