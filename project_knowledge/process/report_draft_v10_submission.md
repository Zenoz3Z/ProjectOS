# ProjectOS: Supporting Re-entry into Long-term Creative Projects through Source-visible and Correctable AI

Fuzhe Zhang · MSc Creative Computing · UAL Creative Computing Institute · 2026

Status: Submission version

Last updated: 17 November 2026

Body word count: 3,575 (including Abstract, in-text citations, table content and Ethical Considerations; excluding front matter, headings, References, Appendices and the separately reported AI Use Acknowledgement).

AI Use Acknowledgement: 225 words. Body plus acknowledgement: 3,800 words. Separate reporting does not imply an institutional word-count exemption for the acknowledgement.

## Abstract

Returning to a creative project requires reconstructing earlier intentions, decisions and unfinished work. ProjectOS presents six provisional AI summaries with visible supporting excerpts and persistent review choices. Four participants evaluated the prototype across two formative rounds. They reported assistance recalling goals and changes, but source inspection was limited, and completed-project contexts complicated judgments of applicability. Correction controls supported agreement, revision, rejection and, in Round 2, non-applicability. A separate post-study technical experiment tested record-level state metadata against a frozen retrieval baseline. Several broad retrieval measures improved, while current/superseded evidence pairing deteriorated; the experiment met neither the Phase 1 nor Phase 3 success criteria. Together, these findings distinguish documentary relevance from understanding a project's present state. The contribution is a source-visible, correctable re-entry workflow, observations from four practitioners, and a retrieval benchmark. ProjectOS supports reflective assessment while leaving current-state judgments open to practitioner review.

## 1. Introduction

Long-term creative projects leave uneven records. Goals, experiments, decisions and reflections describe different moments without consistently identifying what remains relevant. Returning after an interruption requires reconstructing why a direction changed, distinguishing an abandoned possibility from an active commitment, and deciding what deserves attention now.

ProjectOS addresses this problem through a six-section Project Re-entry Brief. It retrieves project records, generates provisional summaries and exposes supporting excerpts alongside review controls. Persistent judgments allow practitioners to accept, revise or contest a proposed narrative without changing the source archive.

The research question is: How can source visibility and user correction help creative practitioners assess AI-generated reconstructions of long-term project state? Assessment concerns perceived alignment, interpretability, control and checking effort, not independently measured reconstruction accuracy.

Two supervised rounds involving four participants provide the primary evaluation. Round 2 participants revisited completed or largely completed projects, making retrospective understanding more evident than preparation for renewed development. A subsequent technical investigation examined whether explicit document-state metadata could address retrieval problems identified during development.

## 2. Related Work

### 2.1 Creativity support and control

Shneiderman (2007) positions Creativity Support Tools (CSTs) as resources for exploration and discovery, emphasising history-keeping and revisiting alternatives. Frich et al. (2019) examine support across creative phases and difficulties comparing prototypes and evaluation approaches. These perspectives motivate attention to recovering process knowledge before producing new work. For ProjectOS, revisiting decisions and maintaining control over their interpretation are design concerns in their own right.

Evaluating a CST requires specifying which benefit is being assessed. Usable operation, perceived recall assistance and improved creative outcomes are different claims. Project context matters: completed and paused archives need not support the same questions. Cherry and Latulipe (2014) developed the Creativity Support Index through explicit validation. ProjectOS does not administer that instrument or estimate creativity gains; its exploratory ratings address clarity, control and checking effort alongside qualitative accounts.

### 2.2 Retrieval, grounding and applicability

Lewis et al. (2020) evaluated Retrieval-Augmented Generation (RAG), combining external passages with generation, on knowledge-intensive NLP tasks. Gao et al. (2024) reviewed retrieval, augmentation, generation and evaluation challenges, including context relevance and answer faithfulness. These contributions distinguish selecting suitable text from generating supported claims. Neither directly evaluated the interpretation of current, historical, superseded and conditional states in long-term creative project records.

Four distinctions guide this thesis. Semantic relevance concerns the relationship between a query and text. Source grounding concerns whether evidence supports a generated claim. Current-state applicability concerns whether that claim applies at the project's reference state. Statement-level temporal interpretation concerns whether a particular assertion is active, replaced, completed or conditional. A faithful summary of an earlier goal can still misrepresent a current commitment. Conversely, a retrieval miss can leave a section marked as having insufficient evidence despite relevant source material.

### 2.3 Reflective interaction and judgment

Tankelevitch et al. (2024) identify metacognitive demands in evaluating generative outputs and deciding how to rely on them. Delegating summarisation leaves checking work with the user. Xu et al. (2025) examine how different AI workflows affect designers' cognitive activities and perceptions of control. These accounts motivate examining where assessment occurs, rather than treating AI availability as a uniform intervention.

Van der Burg et al. (2026) approach AI through deliberate reflection on data and interpretation. Their slow-technology approach places deliberate data work within the creative process. Read alongside CST research, this shifts the design question from producing more material to supporting how practitioners examine and revise it. RAG can supply a traceable documentary basis, but retrieval relevance leaves current applicability unresolved. Tankelevitch et al.'s (2024) account complicates this benefit: presenting sources also gives users more material to assess. Xu et al. (2025) show that pre-populated AI content can shift activity towards review and synthesis. ProjectOS adopts pre-generated briefs to make an archive quickly approachable, whereas slow AI deliberately makes time for engagement with data. The tension is not resolved by adding citations or more controls. A compact brief may help orientation while making it easy to accept a fluent account without checking. The design must therefore balance traceability, actionable information and verification burden, leaving room for selective inspection and a practitioner's alternative interpretation.

## 3. Methodology and Design

### 3.1 Prototype and interaction

Iterative design combined engineering checks with formative study. P00 was an informal pilot and P96 a researcher self-test; neither entered the formal sample. Early retrieval experiments did not establish consistent semantic improvement, so the participant prototype retained its existing retrieval pipeline.

ProjectOS is a local Python and Streamlit research prototype. The researcher imports screened Markdown, text or text-based PDF records and prepares summaries before supervised sessions. Records are divided into windows of up to 120 words with 30-word overlap. Local sentence embeddings, section queries and category filters select at most two excerpts per section. Selected material goes to the OpenAI API during preparation. The preparation caches for all four participants recorded `gpt-6-luna` as the OpenAI model identifier used for summary generation. Structured summaries contain support assessments, state classifications and source references. Semantic similarity is not factual confidence. Project-specific caches support reviewing, saving, navigation and refresh restoration without further API requests or embeddings.

After an Echo Field tutorial, participants review current intention, changes and reasons, current versus earlier directions, relevant feedback, unresolved tensions and a documented next step. Supporting records are optional and initially collapsed. Review proceeds sequentially, then permits direct navigation among completed sections with unsaved-input protection. User updates remain separate from original evidence and generated summaries.

Round 1 offered Confirm, Update and Reject. Iteration 2, implemented on 19 October 2026, added Not applicable as a distinct completed-review action. Section 3 became Current direction and replaced ideas; Section 6 became Documented next step, explicitly concerning recorded actions rather than invented recommendations. Tutorial and checking guidance were clarified without changing retrieval, prompts or rating items. Iteration 3 followed Round 2 but preceded the temporal-state experiment.

### 3.2 Participant procedure

Four adults were recruited through convenience sampling, two per round, each using their own creative project. The planned procedure requested four to eight screened records and an independent pre-exposure account, followed by tutorial, six-section review, ratings and a short interview. Round 1 independent pre-tests are missing; Round 2 includes pre-test accounts. The researcher organised materials, assisted importing and facilitated sessions on the researcher's computer. Researcher preparation and explanation could influence the experience.

### 3.3 Research safeguards

All four participants received information before participation and provided signed consent, with a seven-calendar-day withdrawal period. Supervisor confirmation on 9 October 2026 required no amendment to existing ethics approval, while requesting clearer storage wording. The protocol specified restricted UAL OneDrive storage, necessary temporary copies on a password-protected research computer, and deletion of source files, extracted text and working copies within seven days after each session. De-identified records and separately stored consent forms were scheduled for retention until 30 November 2027 and subsequent deletion.

The separate identity link was scheduled for deletion after the withdrawal period; unlinking and aggregation could prevent later withdrawal. Completion of scheduled deletions was not verified for this thesis. External API handling included possible abuse-monitoring retention for up to 30 days: requesting non-storage did not guarantee zero provider retention. Written notes were used without audio, video or photographic recording. Public reporting contains aggregates and paraphrases, excluding participant quotations, identities, signed forms and private source excerpts.

### 3.4 Post-study technical experiment

Phase 1 froze a researcher-labelled benchmark of 34 cases: 18 production cases representing six canonical sections across Echo Field, the researcher-owned P96 archive and synthetic Signal Loom, plus 16 diagnostic cases. P01–P04 materials were excluded. One researcher created and confirmed the labels with assistant preparation; there was no independent second annotator or inter-rater agreement. Production and diagnostic results remained separate. For production cases, ‘current’ referred to the latest supplied project state, not activity on the experiment date. Historical diagnostic cases used their specified cutoff and excluded later or temporally unplaced records.

Both tiers used the unchanged pair of configured retrieval queries for each section; diagnostic cases assessed narrower evidence requirements and did not contribute to primary success criteria. Support and applicability were annotated separately. An explicit closure statement could support non-applicability, whereas absent records alone left applicability unclear. Labels were frozen before baseline measurement and retained alongside all cases after evaluation.

Phase 2 measured the unchanged semantic baseline. Phase 3 preregistered one record-level state-aware selector, changing final evidence selection only. Record states described document function, not each statement's truth or temporal status. Sections 1 and 5 preferred the snapshot family: current snapshots, final snapshots and closure records. Section 3 paired snapshot and historical records where available, otherwise retaining baseline selection. Sections 2, 4 and 6 remained unchanged. Candidate pools, queries, embeddings, chunking and category eligibility were fixed. The selector received record states and candidate identities/scores, without gold evidence or target roles.

Historical records described past events; current and final snapshots presented a supplied state or final version. Closure records described completion or archiving, without settling every limitation. Mixed, undated records lacked a clear snapshot, closure or retrospective function; unknown indicated that the document's function could not be established. A final snapshot did not establish ongoing development. Dates and catalogue order were excluded from ranking; catalogue order did not prove authoring chronology.

The formal candidate evaluation ran once across all 34 cases; no v2 was tuned afterwards. It assessed retrieval only, and the selector was not deployed into the participant prototype.

## 4. Evaluation

### 4.1 Participant assessment

Round 1 involved P01 and P02; Round 2 involved P03 and P04 and closed on 24 October 2026. There was no P05. Their 24 final section judgments exclude tutorial actions, P00, P96 and historical revisions.

The researcher compared saved review actions, ratings, observation notes and follow-up answers across participants and rounds, with AI assistance in organisation, descriptive statistics and suggested interpretations. The researcher checked the statistics and interpretations against the study records. Similarities, differences and contradictory cases informed the four participant findings. No formal codebook, independent coder, inter-rater reliability procedure or inferential statistical analysis was used. Evidence expansion was manually observed, not automatically logged; opening a panel did not establish reading.

The unchanged R1–R7 instrument, Round 1 v1, was frozen on 8 October 2026. Ratings ranged from 1 (Strongly disagree) to 7 (Strongly agree). These were custom exploratory items, not a validated scale. Negatively worded R6 concerns greater verification burden than expected. P03's explanation was ambiguous; no reverse scoring or composite score was calculated. Historical L1–L7 responses were not combined with these ratings.

Local automated validation passed 129 tests, followed by researcher interface inspection on 25 October 2026. The automated browser check remained blocked by its execution environment. These engineering checks were separate from participant validation; the appendix links the detailed Iteration 3 validation record.

### 4.2 Technical measures

Hit@k recorded whether at least one complete, role-appropriate acceptable gold passage appeared within the first k ranked items; it did not require coverage of every required role. Mean reciprocal rank (MRR) averaged the reciprocal rank of the first such match. The selected pair occupied positions one and two, followed by an evaluation-only semantic tail. Macro required-role coverage@2 averaged each case's fraction of required roles covered. All-required-role coverage and pair coverage were separate measures, requiring every role and both accepted current and superseded evidence respectively. Applicability coverage measured evidence establishing applicability or explicit non-applicability; closure recognition measured scoped closure evidence.

Known false-current exposure was a lower bound on selected misleading temporal evidence, not a complete error rate. Incomplete passage annotations prevented full temporal-mismatch and false-current measurement. Retrieval-only evaluation could not measure final summary accuracy or insufficient-evidence classification accuracy; unavailable metrics remained unmeasured, not zero. Positive-gold metrics used 15 supported production cases, with three insufficient cases analysed separately.

Warm latency included retrieval, selection and excerpts, with one warm-up and 30 repetitions per unique request on the same local environment. Phase 3 improvement criteria and original Phase 1 criteria were assessed separately. Saved traces verified results without another candidate evaluation; detailed reproducibility records are linked in the appendix.

Matching required complete source-located assertions and necessary context, not merely the correct filename. Applicability used fourteen cases with established applicability labels, excluding four unclear cases. Pair and closure measures each used three eligible cases. The false-current lower bound used nine current-claim cases. These differing denominators were fixed prospectively and are not alternative estimates of one overall accuracy rate.

## 5. Findings

### 5.1 Recall and perceived alignment

Participants reported help recalling goals, important changes and decisions. Changes and reasons was accepted in both Round 2 sessions, with one participant identifying it as most helpful. These were accounts of perceived assistance, not measured memory improvement. Round 2 projects were complete or largely complete, and no subsequent resumption of development was established. One participant associated limited usefulness with the small number of populated summaries despite no recorded interface-operation problem.

Participant-assessed alignment, R2, was rated 6 by both participants in each round. Re-entry, R5, ranged from 5–6 in Round 1 and was 5 for both Round 2 participants. These assessments coexisted with corrections and limited content coverage.

### 5.2 Review choices and control

Round 1 produced 12 reviews: 9 Confirm, 2 Update and 1 Reject. Not applicable was unavailable. Updates expressed a practitioner's different interpretation. One participant rejected an insufficient-feedback result while another confirmed it, although both reported no relevant external feedback.

Round 2 produced 12 reviews: 3 Confirm, 9 Not applicable, 0 Update and 0 Reject. Explanations referred to completed projects, absent feedback, unavailable next actions and issues no longer considered current. Some did not distinguish missing information from inapplicability. Both participants rated correction and control, R4, at 7, although neither performed an Update. Round 1 responses retained their original action labels and were not retrospectively reclassified after Not applicable was introduced.

### 5.3 Source visibility and checking

The researcher observed evidence panels being opened in 2/12 Round 2 sections. Combined session duration was approximately 36 minutes, averaging approximately 18 minutes. These are session estimates, not review-event intervals. Round 1 recorded three opened sections, eight not opened and one missing observation. P02's conflicting timing records prevent precise cross-round comparison. P02 rated source visibility highly despite no recorded opening; neither the reason for that valuation nor depth of reading was established.

### 5.4 Evidence absence and project state

Completed-project accounts accompanied frequent non-applicability judgments. P03 associated limited coverage with reduced usefulness and requested clearer information about materials that might help an insufficient section. This request was not documented from both Round 2 participants. Round 1 also included a request for clearer next-action support.

### 5.5 Post-study technical results

The production comparison yielded the following results; denominators follow the frozen eligibility rules.

| Metric | Baseline | State-aware candidate |
| --- | --- | --- |
| Hit@1 | 6/15 | 6/15 |
| Hit@3 | 10/15 | 12/15 |
| MRR | 0.5533 | 0.6168 |
| Macro required-role coverage@2 | 0.5667 | 0.7000 |
| All-required-role coverage@2 | 8/15 | 9/15 |
| Current/superseded pair coverage@2 | 2/3 | 1/3 |
| Applicability evidence coverage@2 | 8/14 | 8/14 |
| Closure recognition@2 | 2/3 | 2/3 |
| Known false-current exposure lower bound | 1/9 | 1/9 |

Two production cases newly met the all-required-role criterion, while one baseline pass became a failure. Warm median latency increased from approximately 22.01 ms to 25.26 ms, below the preregistered 44.03 ms limit. Separate diagnostic improvements included pair coverage rising from 1/5 to 3/5, but did not substitute for primary performance.

The result was mixed/negative. Phase 3 criteria were not met: all-required-role coverage was 9/15 against a 10/15 minimum, a baseline pass was lost, and pair coverage fell below its 2/3 minimum. The original Phase 1 criteria were also not met, including strict pair improvement, cross-project role improvement and complete closure coverage.

## 6. Discussion

### 6.1 Traceability and practitioner authority

Source visibility made the reconstruction traceable and created an opportunity for verification. Actual checking depended on whether participants opened and interpreted the evidence. Following Tankelevitch et al.'s (2024) concern with evaluation demands, the design kept evidence optional so practitioners could inspect surprising, uncertain or incomplete summaries selectively. Optional inspection was a trade-off intended to limit verification burden, not an established best approach.

Confirm records assessed agreement; Update supplies a different interpretation; Reject contests a reconstruction; Not applicable allows current irrelevance to be expressed. Storing review events separately preserved the source archive while allowing practitioners to record a competing interpretation without overwriting the original evidence. This design applies Shneiderman's (2007) history-keeping principle and Frich et al.'s (2019) attention to creative context. Confirmation is a participant judgment, not objective ground truth. High control ratings without actual updates distinguish an available capability from observed use. Because the response set changed between rounds, action totals cannot establish performance improvement.

The nine Round 2 Not applicable choices may reflect completed work, a section's irrelevance, missing explicit state information or missed evidence; they cannot all be attributed to failed retrieval. Allowing an insufficient result exposes uncertainty that a fluent answer could conceal. This was a design choice to make limitations in the selected evidence visible, while leaving practitioners to assess their meaning for the project. The retrieval experiment did not measure whether abstention decisions were accurate.

The researcher's separate post-session retrieval diagnosis identified relevant information omitted from selected evidence in three P03 sections. A cached future-oriented next-action assessment also coexisted with a participant account of no current next step. Without durable links between reviews and displayed-summary snapshots, this cannot prove the exact output seen.

### 6.2 Relevance without dependable state interpretation

Record-level metadata improved several broad retrieval measures but did not reliably preserve or improve current/superseded evidence pairing. The loss of one baseline pass and lower pair coverage explain why MRR and partial role gains alone were inadequate success measures.

A likely limitation is granularity: documents can mix historical, current, completed and speculative statements. Promoting a final overview or pairing it with a historical record does not establish which assertion replaced which. The experiment supports this concern through pairing regression, without isolating granularity as its sole cause.

Lewis et al. (2020) and Gao et al. (2024) explain documentary grounding; this comparison shows the additional difficulty of interpreting changing commitments. Xu et al.'s (2025) attention to cognitive work helps explain the remaining design task: retrieved text still requires interpretation. ProjectOS uses source inspection and correction to support that work, complementing van der Burg et al.'s (2026) emphasis on reflection.

### 6.3 Design response and limitations

Iteration 3 introduced clearer insufficient-evidence messages, section-specific record guidance, unified action definitions and an optional-evidence reminder as a post-study design response. Its guidance was intended to help users distinguish insufficient evidence from current inapplicability. No third participant round was conducted, so its effect remains untested with new participants. It suggests potentially useful record types without diagnosing missing files or inventing actions.

Four convenience-sampled participants cannot represent creative practitioners generally. Project types and completion states differed; Round 2 mainly involved completed projects. Response options changed, there was no control group, and researcher-assisted preparation and explanation limit causal and independent-use claims. Round 1 lacks uniform independent pre-tests and complete evidence-opening records. P02's timing conflict, P03's R6 ambiguity, manual observations and missing summary-snapshot links constrain comparison.

The technical benchmark contains only 18 production cases across three corpora, including one synthetic and one researcher-owned archive. Cases share project contexts and are not independent project samples. The same researcher confirmed gold labels and saw baseline outcomes before candidate design, so this was not a held-out evaluation. Retrieval-only results establish neither summary accuracy nor participant benefit, and no new participant evaluation followed the experiment. No statistical inference is warranted. Production remains a local supervised prototype with frozen features.

### 6.4 Ethical Considerations

Creative project records can contain distinctive ideas, unpublished work and contextual details. Removing names and contact details reduces direct identification but cannot prevent recognition through project content or settle intellectual-property concerns. Restricted access and screened records therefore remain partial safeguards, not guarantees of anonymity or permission to reuse material.

ProjectOS sends selected text to an external API during preparation. A local interface and reusable caches do not make that processing wholly local or remove provider-retention risks. The storage arrangements in Section 3.3 describe safeguards and planned deletion, not proof that deletion occurred.

Outdated, incomplete or plausible reconstructions could influence practitioners' understanding of their own projects. Visible sources and separate corrections offer opportunities to check and contest an account, without guaranteeing accuracy or removing verification effort. This limits the authority the interface should claim.

Translation and summary compression may also lose creative context or nuances of intent. Researcher or participant checking provides a chance to identify such losses; the study did not measure their extent. Finally, cache reuse avoids repeated generation during review, but energy use and carbon emissions were not measured. It would therefore be inappropriate to claim a demonstrated environmental benefit.

## 7. Conclusion

ProjectOS addresses project re-entry by making reconstructed accounts traceable and open to practitioner revision. In the four-person study, participants reported help recalling goals and changes, while limited evidence opening showed that access to sources and verification were distinct. Source visibility offered a documentary basis to inspect. Review choices let practitioners agree, propose an alternative, reject an account or express non-applicability, with their interpretations stored separately from the original evidence.

These mechanisms leave temporal and current-state judgments unresolved. The post-study experiment reinforced this limitation: record-level metadata improved some retrieval measures, weakened current/superseded pairing and met neither the Phase 1 nor Phase 3 success criteria. The design contribution is a transparent, correctable reflective interface that makes room for disagreement about a project's state. Its value lies in exposing the basis and limits of a reconstruction while allowing the practitioner to record another interpretation.

## AI Use Acknowledgement

I used ChatGPT and Codex to support the development and documentation of ProjectOS. Their contributions included design discussions, code and test generation, debugging, preparation of research materials, and assistance with organising and interpreting research records. ChatGPT also supported literature translation and explanation. I read most papers in their original form, developed my own reading reflections, and used AI assistance to refine their expression.

The thesis draws on my project materials, reading reflections and research records. AI tools assisted with structuring the thesis, drafting some passages, integrating results and revising English expression. I reviewed the final text using both English and Chinese to check meaning and completeness, and checked the research facts and analytical conclusions against my records.

I personally organised, observed and recorded the user-testing sessions. AI assisted with descriptive statistics and suggested interpretations, which I checked against the study records. My technical checks included running tests, inspecting the interface and examining key functions; I do not claim to have independently written or reviewed every line of code. AI-assisted research materials and translations were subsequently checked by me or the relevant participants. Names, contact details and other direct identifiers were removed from materials shared with the assistants.

I take responsibility for the submitted work and its interpretations. This development and writing assistance is distinct from the model-based summary generation within ProjectOS, described in the methodology.

## References

Cherry, E. and Latulipe, C. (2014) ‘Quantifying the creativity support of digital tools through the Creativity Support Index’, *ACM Transactions on Computer-Human Interaction*, 21(4), Article 21, pp. 1–25. Available at: [https://doi.org/10.1145/2617588](https://doi.org/10.1145/2617588).

Frich, J., MacDonald Vermeulen, L., Remy, C., Biskjaer, M.M. and Dalsgaard, P. (2019) ‘Mapping the landscape of creativity support tools in HCI’, *Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems*, Paper 389, pp. 1–18. Available at: [https://doi.org/10.1145/3290605.3300619](https://doi.org/10.1145/3290605.3300619).

Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J., Wang, M. and Wang, H. (2024) ‘Retrieval-augmented generation for large language models: A survey’, *arXiv*, 2312.10997, version 5, revised 27 March 2024; first submitted 2023. Available at: [https://doi.org/10.48550/arXiv.2312.10997](https://doi.org/10.48550/arXiv.2312.10997) and [the cited version](https://arxiv.org/abs/2312.10997v5).

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S. and Kiela, D. (2020) ‘Retrieval-augmented generation for knowledge-intensive NLP tasks’, *Advances in Neural Information Processing Systems*, 33, pp. 9459–9474. Available at: [the NeurIPS proceedings](https://papers.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html).

Shneiderman, B. (2007) ‘Creativity support tools: Accelerating discovery and innovation’, *Communications of the ACM*, 50(12), pp. 20–32. Available at: [https://doi.org/10.1145/1323688.1323689](https://doi.org/10.1145/1323688.1323689).

Tankelevitch, L., Kewenig, V., Simkute, A., Scott, A.E., Sarkar, A., Sellen, A. and Rintel, S. (2024) ‘The metacognitive demands and opportunities of generative AI’, *Proceedings of the 2024 CHI Conference on Human Factors in Computing Systems*, Article 680, pp. 1–24. Available at: [https://doi.org/10.1145/3613904.3642902](https://doi.org/10.1145/3613904.3642902).

van der Burg, V., de Boer, G., Benjamin, J.J., Halperin, B.A., Akdag, A.A., Chandrasegaran, S. and Lloyd, P. (2026) ‘Reflective AI: A slow technology approach for design education’, *Proceedings of the 2026 CHI Conference on Human Factors in Computing Systems*, Article 89, pp. 1–19. Available at: [https://doi.org/10.1145/3772318.3791691](https://doi.org/10.1145/3772318.3791691).

Xu, X., Konnova, A., Gao, B., Peng, C., Vo, D. and Dow, S.P. (2025) ‘Productive vs. reflective: How different ways of integrating AI into design workflows affect cognition and motivation’, *Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems*, Article 24, pp. 1–15. Available at: [https://doi.org/10.1145/3706598.3713649](https://doi.org/10.1145/3706598.3713649).

## Appendix: Existing supporting materials

This inventory links existing materials; forms, images and research records are not embedded in this draft. The argument and substantive findings appear in the main text. Historical documents retain their original status and terminology.

- **Participant information and consent:** [Blank participant information and consent form used in the study (Version 1.0, 9 October 2026).](../research/appendices/ProjectOS_Participant_Information_and_Consent_Form.pdf) The researcher confirmed that this blank version was provided to participants. It is linked as a supporting document, not embedded here; the PDF alone does not establish ethics approval or completion of every consent procedure. The earlier [Participant Information Sheet](../feedback/user_testing/iteration_1/participant_information_sheet.md) and [Consent Form review draft](../feedback/user_testing/iteration_1/participant_consent_form.md) remain available as historical drafts. Signed or completed forms are not included.
- **Questions and ratings:** the [question and observation guide](../feedback/user_testing/iteration_1/post_test_questionnaire_and_interview.md) preserves the original Round 1 prompts. The unchanged [R1–R7 instrument, Round 1 v1](../feedback/user_testing/iteration_1/round_1_templates/post_test_ratings_template.md) was also used in Round 2, as documented in the [final findings](../feedback/user_testing/iteration_2/round_2_final_findings.md). Its public master retains historical draft-status wording. L1–L7 remains historical and was not combined with the formal instrument.
- **Interface image:** an [existing early command-line prototype screenshot](../../outputs/screenshots/day_04_corrected_reentry_brief.png.png) shows the Echo Field demonstration only. It is not a final Streamlit interface screenshot or participant-session evidence.
- **Development and testing:** the [development-log index](daily_logs/README.md), [Iteration 2 validation](../../outputs/test_results/iteration_2_usability_validation.md), [Iteration 3 validation](../../outputs/test_results/iteration_3_evidence_guidance_validation.md) and [final design decision](../decisions/design_decisions/dd_006_iteration_3_actionable_evidence_absence.md) distinguish implementation evidence from participant evaluation. Private source packs, summaries, reviews and interview records are not appended.
- **Post-study technical evidence:** the [Phase 1 protocol](experiments/temporal_state_retrieval/experiment_protocol.md), [Phase 3 preregistration](experiments/temporal_state_retrieval/phase_3_preregistration.md), [baseline report](../../outputs/test_results/temporal_state_retrieval_baseline/baseline_report.md), [candidate report](../../outputs/test_results/temporal_state_retrieval_state_aware/phase_3b_report.md), [results log](experiments/temporal_state_retrieval/phase_3b_results_log.md) and [public verification](../../outputs/test_results/temporal_state_retrieval_state_aware/verification.json) preserve the frozen comparison and its mixed/negative outcome. Private traces, source records and case-level analyses are not appended.
