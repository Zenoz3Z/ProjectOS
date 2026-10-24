# Cross-iteration findings

Status: Final descriptive comparison of the completed two-round study, 24 October 2026.

## Sample and comparability

Round 1 comprised P01 and P02; Round 2 comprised P03 and P04. The total formal sample is four, **n=2 per round**. P00 is an excluded informal pilot; P96 is an excluded researcher self-test. Tutorial and synthetic test events are excluded. Round 2 is closed with no P05 and no further recruitment planned.

These are different participants with different projects, source packs and return contexts. Round 1 records describe inactive/paused projects but lack independent pre-exposure baselines; their present completion/resumption status is not established by a comparable baseline. Round 2 projects were described as complete or largely complete. This is not a repeated-measures study, controlled experiment or statistical comparison of equivalent conditions.

## Review actions

Saved project-specific actions match the session records in all four cases. Update corresponds to the stored correct action.

| Measure | Round 1 | Round 2 |
|---|---|---|
| Formal sections reviewed | 12 | 12 |
| Confirm | 9 | 3 |
| Update | 2 | 0 |
| Reject | 1 | 0 |
| Not applicable | Unavailable in this interface version | 9 |

Not applicable changed the response set. Round 1's absence of this option must not be represented as a comparable zero-use category, and earlier responses must not be relabelled. The completed-project contexts also help explain why non-applicability was relevant. Action differences alone do not establish an interface effect or improved accuracy.

## Usability and the design response

Round 1 included difficulty interpreting Section 3 and requests for clearer guidance and next-action explanation. Some observations about tutorial/help needs differed from later follow-up answers; those differences remain unresolved rather than being converted into a uniform assistance claim.

[DD-005](../../../decisions/design_decisions/dd_005_round_1_usability_refinements.md) and [TD-004](../../../decisions/technical_decisions/td_004_iteration_2_review_semantics.md) document clearer section wording, Not applicable, concise tutorial instructions and guidance about when to inspect evidence. They retain retrieval, prompts, caches and rating wording.

Direct post-completion navigation already existed at the [7 October milestone](../../../process/daily_logs/2026-10-07_assigned_projects_and_navigation.md). Iteration 2 retained it; it was not newly introduced after Round 1. The [105-test validation record](../../../../outputs/test_results/iteration_2_usability_validation.md) concerns implementation behaviour and synthetic checks, not participant outcomes.

Round 2 reported no navigation, terminology or lag problems and almost no need for researcher explanation. This is consistent with improved usability, but the changed participants and projects, small sample and absence of a comparison condition prevent a causal conclusion.

## Verification behaviour

Round 2 records support evidence expansion in **2 of 12 sections**. Round 1 records explicitly establish three opened sections and eight not opened, with one observation missing. No complete Round 1 total or rate is calculated, and no change in checking rate is claimed.

Evidence opening was manually observed in both rounds, not captured in a complete interaction log. Opening does not prove thorough reading; visible evidence does not mean it was actively checked. High self-reported source-visibility ratings and limited observed opening can coexist because they describe different aspects of the experience.

## Project-state interpretation

A historical goal, limitation or possible future direction may remain semantically relevant while no longer being recognised as current. ProjectOS cannot reliably determine current project state from semantic relevance alone. Participant review supplies an additional interpretation layer, including updates and statements of non-applicability.

Confirm is acceptance, not independently verified truth. Not applicable does not prove that the supplied corpus lacked relevant records. A correct-looking output and a reliable retrieval or reasoning process must not be conflated. Existing saved reviews are also not durably tied to exact summary snapshots, limiting retrospective exposure claims.

## Evidence absence

| Situation | What the evidence supports | What must not be inferred |
|---|---|---|
| Genuine corpus absence | A lack of attributable feedback in supplied materials can make an insufficient result appropriate. Session records describe such absence. | An empty category or selected evidence alone proves that feedback never existed in the real project. |
| Retrieval/evidence-selection failure | An existing preparation diagnosis identifies relevant passages missed for some insufficient sections. | Every insufficient result is a retrieval failure, or a participant's response itself diagnoses the algorithm. |
| Historical information no longer applicable | Records may exist while participants consider the represented aim, issue or task no longer current. | Historical records are false, or the system performed reliable temporal reasoning. |
| Appropriate-looking outcome after incomplete selection | A completed-project judgement can fit an output whose evidence selection was incomplete. | Agreement establishes a trustworthy retrieval pathway. |

The original three-choice interaction led to different responses to absence. Not applicable provides a further expression, but some reasons still do not separate missing records, missed records and a state that no longer applies.

Explaining which kinds of material may be missing is **future work**. It is not implemented, and any such explanation would need to avoid claiming source absence when retrieval has simply missed existing evidence.

## Descriptive rating comparison

The [frozen R1-R7 wording](../iteration_1/round_1_templates/post_test_ratings_template.md) was retained. These are custom exploratory ratings, not a validated scale. **n=2 per round**; ranges describe the observed values only.

| Item | Round 1 range | Round 2 range |
|---|---|---|
| R1 | 7–7 | 5–7 |
| R2 | 6–6 | 6–6 |
| R3 | 7–7 | 5–6 |
| R4 | 4–7 | 7–7 |
| R5 | 5–6 | 5–5 |
| R6 | 3–5 | 2–6 |
| R7 | 6–7 | 5–6 |

R6 is negative-direction, and P03's interpretation remains ambiguous. No reverse scoring or composite score is used. No significance tests, inferential statistics or causal claims are made from rating differences. Participant-assessed alignment is not objective accuracy or ground truth. The study does not establish better memory, creativity or productivity.

## Timing and data-quality boundaries

Round 2's approximate combined duration was 36 minutes, averaging 18 minutes. One Round 1 session has unresolved disagreement between its session timing and saved review timestamps; that participant's date and duration are excluded from public aggregation. No round-to-round efficiency comparison is supported.

Both Round 1 independent baselines are missing. One Round 1 evidence-opening observation, some reasons and assistance details are missing or ambiguous. Retrospective follow-ups, researcher-organised packs, different project states and minimal source opening limit interpretation. Conflicts are retained in private audit materials, not resolved by selecting a convenient record.

## Implications for the research question

Source visibility and user correction can support assessment by making AI reconstruction provisional and reviewable. However, visibility alone did not ensure evidence checking, and user actions were also needed to express non-applicable or outdated project states. The study therefore supports correctability and explicit absence as useful design principles, while showing that semantic retrieval alone cannot determine current project state.

This is a small-sample design interpretation, not proof of causal benefit or generalisable performance. Separate interface usability, summary usefulness and verification behaviour when integrating these findings into the thesis.

Both rounds are complete and prototype feature development is frozen. Remaining work is final analysis review, thesis integration, final validation and submission preparation. The [Round 2 final findings](round_2_final_findings.md) provide its detailed descriptive account. Private participant records and exact source references remain outside Git.
