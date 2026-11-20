# ProjectOS submission materials

Fuzhe Zhang (Zeno) · MSc Creative Computing · University of the Arts London

Assessment materials for 18 November 2026. The dissertation below is the final version selected by the author.

## Read and watch

1. [ProjectOS Dissertation (PDF)](documents/ProjectOS_Dissertation.pdf). The 13-page PDF reports 3,554 words for the body and 225 for the AI Use Acknowledgement, totalling 3,779.
2. [ProjectOS Demonstration (MP4)](demo/ProjectOS_Demonstration.mp4) and [English Subtitles (SRT)](demo/ProjectOS_Demonstration.en.srt), copied without alteration. The researcher reports viewing and accepting this video in full. It uses a tutorial and an explicitly fictional update. Subtitles are editorial, including the disclosed update-field wording, not a verbatim transcript.
3. [Try the public Echo Field tutorial](../demo/README.md). From the extracted project root, with the project dependencies installed, run `python -B demo/launch.py --port 8501`. It uses six pre-generated summaries without an API key and saves demonstration responses in a separate local session.

## Independent attachments and evidence

| Material | Status and entry |
| --- | --- |
| Information and consent | [Blank participant information and consent form used in the study (Version 1.0, 9 October 2026)](../project_knowledge/research/appendices/ProjectOS_Participant_Information_and_Consent_Form.pdf). The researcher confirmed it was the blank issued version and authorised public researcher details. It is a separate attachment, not embedded in the thesis. The PDF itself does not prove approval or completion of every consent procedure. |
| Questions and observation | [Questionnaire and interview/observation guide](../project_knowledge/feedback/user_testing/iteration_1/post_test_questionnaire_and_interview.md) and [blank R1–R7 ratings](../project_knowledge/feedback/user_testing/iteration_1/round_1_templates/post_test_ratings_template.md). Public masters retain historical draft wording; no claim is made that their files are the final issued copies. |
| Study summaries | [Round 2 final findings](../project_knowledge/feedback/user_testing/iteration_2/round_2_final_findings.md) and [cross-iteration findings](../project_knowledge/feedback/user_testing/iteration_2/cross_iteration_findings.md). Four formal participants, two per round; P00/P96 excluded; no P05 or third participant round. |
| Process | [Daily logs](../project_knowledge/process/daily_logs/README.md) identify original records and retrospective backfill. Dated plans, old chapter drafts and test reports retain their historical status and are not replaced by current claims. |
| Technical experiment | [Baseline report](../outputs/test_results/temporal_state_retrieval_baseline/baseline_report.md), [candidate report](../outputs/test_results/temporal_state_retrieval_state_aware/phase_3b_report.md), [verification](../outputs/test_results/temporal_state_retrieval_state_aware/verification.json) and [results log](../project_knowledge/process/experiments/temporal_state_retrieval/phase_3b_results_log.md). Separate post-study retrieval-only investigation; mixed/negative; neither success criterion set passed; not deployed into the participant prototype. |
| Historical preparation checks | [17 November validation record](validation.md) for the v10 materials and public tutorial. The test counts describe that preparation run. |

## Version and reproduction limits

The review branch is `temporal-state-retrieval-state-aware-v1`. The retained v10 PDF, Word document and Markdown record the 17 November draft. The 18 November dissertation is supplied as a PDF.

Python dependencies are supplied as a pinned requirements list, not a bundled environment. Installation may require network access. The prepared tutorial runs without an API key or embedding model; fresh summary preparation is a distinct workflow with local model and external API requirements. Frozen experiment reports are included without rerunning them. Complete experiment reproduction requires excluded researcher-owned private evidence and traces; participant source packs are deliberately unavailable.

The published materials exclude private research records, signed forms, participant assignments, credentials, private traces, model weights, raw recordings and complete AI chat histories. Tracked historical chapter drafts are retained for the process logs.
