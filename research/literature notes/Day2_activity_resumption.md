# Day 2 — Activity Resumption and Personal Information Management

## Paper 1

### Citation

Czerwinski, M., Horvitz, E. and Wilhite, S. (2004). *A Diary Study of Task Switching and Interruptions*. Proceedings of CHI 2004, 175–182. https://doi.org/10.1145/985692.985715

### Research context

The paper reports a week-long diary study of experienced computer users working across multiple projects. Eleven participants were recruited, although one outlier was excluded from the main analysis. Their occupations included software development, web design, education, sales and administration. Participants recorded task switches, interruptions, documents used, forgotten information and the perceived difficulty of returning to tasks.

### Key findings and effective points

1. **Returning to a task was more difficult than beginning or switching to other tasks.** Participants rated returned-to tasks as significantly harder to resume, suggesting that project re-entry requires the reconstruction of context rather than simply reopening an application.

2. **Returned-to tasks were usually longer and more complex.** They lasted approximately 120 minutes on average, compared with 45 minutes for other tasks. This suggests that long-running work is particularly vulnerable to interruption and loss of context.

3. **Returned-to tasks involved more documents.** These tasks used an average of 2.5 documents, compared with 1.6 for other tasks. For ProjectOS, this supports treating project context as distributed across multiple records rather than contained in one file.

4. **Returned-to tasks experienced more interruptions.** They received an average of 1.5 interruptions, compared with 0.7 for other tasks. Repeated interruption therefore creates a cumulative continuity problem.

5. **Participants used different levels of detail when defining tasks.** Some described broad projects, while others recorded individual activities. A support tool should therefore avoid imposing a single fixed definition of a project, task or working session.

6. **Task tracking created additional work.** Participants used calendars, to-do lists, personal devices and file-copying practices to maintain awareness of their activities. Thirteen percent of recorded task switches were related to task tracking itself.

7. **The authors proposed restoring project-specific states and resources.** Suggested support included grouping related documents and applications, preserving window layouts, providing reminders and displaying project histories over time.

### Limitation for ProjectOS

The study focuses on office productivity and desktop task management. It shows that returning to complex work is difficult, but it does not examine creative intentions, design alternatives, feedback or reflection. Its proposed solutions mainly restore applications and documents rather than reconstructing the meaning of earlier decisions.

### ProjectOS implication

I should design ProjectOS to reconstruct a project-level context rather than only retrieve individual files. The system should identify relevant goals, decisions, feedback and unresolved questions across multiple records. However, users must remain able to decide how their project and working sessions are organised.

---

## Paper 2

### Citation

Iqbal, S. T. and Horvitz, E. (2007). *Disruption and Recovery of Computing Tasks: Field Study, Analysis, and Directions*. Proceedings of CHI 2007, 677–686. https://doi.org/10.1145/1240624.1240730

### Research context

The authors conducted a two-week field study with 27 computer users. Their monitoring tool, DART, recorded application use, windows, file actions, email notifications and instant-message alerts. The dataset contained 2,267 hours of activity. Fourteen participants were subsequently interviewed to help interpret the recorded behaviour.

### Key findings and effective points

1. **Task recovery consists of several stages.** The paper separates interruption into preparation, diversion and resumption phases. Returning to an application is therefore not the same as recovering the mental context required to continue the task.

2. **Users often stabilised their work before switching.** Before responding to an alert, participants sometimes completed a sentence, finished a small action or externalised a pending copy-and-paste operation. This suggests that people naturally create resumption cues before leaving a task.

3. **Small interruptions frequently became chains of diversion.** After checking an email or message, users often visited additional peripheral applications before returning. The original task could therefore become increasingly distant from the user’s attention.

4. **Recovery required substantial time.** Participants spent approximately ten minutes responding to an alert and moving through other applications, followed by another ten to fifteen minutes before returning to focused activity on the interrupted task.

5. **Some tasks were not resumed for a long time.** Twenty-seven percent of task suspensions resulted in more than two hours before the previously active window was resumed. This shows that the cost of an interruption can extend far beyond the interruption itself.

6. **Visible cues supported faster recovery.** Suspended windows that remained highly visible were resumed sooner than windows that were mostly hidden. This suggests that relevant project context should remain visible and accessible.

7. **Users felt more in control than the behavioural data suggested.** Participants often believed that they chose when to respond to alerts, but the logs showed that alerts frequently influenced their actions and produced longer diversions than they realised.

8. **The authors proposed preserving the broader task context.** Their recommendations included automatically saving related application states, giving easy access to suspended contexts, displaying visual reminders and replaying recent actions.

### Limitation for ProjectOS

The study mainly investigates short-term, alert-driven interruptions and application-window behaviour. It does not address returning to a creative project after several days, interpreting earlier design reasoning or deciding whether a previous intention remains appropriate. Its monitoring approach also captures activity traces more easily than the meaning behind creative decisions.

### ProjectOS implication

ProjectOS should distinguish between retrieving a document and restoring a meaningful project context. It should present a concise reconstruction of earlier goals and decisions while keeping supporting records visible. Reflective prompts should remain optional because an intrusive prompt could itself become another interruption.

---

## Cross-paper reflection: task resumption

Reading these two papers changed how I frame project re-entry in ProjectOS. Czerwinski et al. establish that returned-to work is not simply another task switch: it tends to involve longer activities, more documents, more interruptions and greater perceived difficulty. Iqbal and Horvitz then show that recovery is a process rather than a single return event. Users may prepare to leave, follow a chain of diversion, reopen an application and still require additional time to recover their mental state. Together, the studies give me stronger evidence that continuity support should reconstruct context rather than merely reopen files.

However, both papers mainly examine office computing, productivity and application windows. They do not investigate how creators recover evolving intentions, interpret earlier feedback, compare abandoned alternatives or decide whether a previous choice should still guide the project. Their proposed support also relies largely on saved layouts, reminders and visual cues. ProjectOS therefore should not claim to discover task-resumption difficulty. Its research opportunity is narrower: testing whether a source-grounded AI account can help a creative student reconstruct and reassess prior design decisions while preserving control over interpretation. The papers also warn me that additional prompts can become new interruptions. ProjectOS should keep reflection optional, show the evidence behind summaries and let users correct or reject the reconstructed account.

---

## Paper 3 — Supporting Context

### Citation

Jones, W., Dinneen, J. D., Capra, R., Diekema, A. R. and Pérez-Quiñones, M. A. (2017). *Personal Information Management*. In M. Levine-Clark and J. McDonald (eds.), *Encyclopedia of Library and Information Science*, Fourth Edition, 3584–3605. New York: Taylor & Francis.

### Research context

This paper reviews Personal Information Management (PIM), which concerns how people acquire or create, keep, organise, maintain, retrieve, use and distribute information in support of everyday and long-term goals. It presents PIM as an effort to maintain a relationship between information and the needs it may serve.

### Key findings and effective points

1. **PIM involves more than information retrieval.** It includes finding and re-finding, keeping information for anticipated needs, and meta-level activities such as maintenance, organisation, evaluation and sense-making.

2. **Information fragmentation increases the cost of project work.** Relevant material may be distributed across files, messages, web pages, applications and devices, making it harder to identify current versions and reconstruct a complete information set.

3. **Re-finding is a multi-step and failure-prone process.** Users must remember to look, recall possible locations or cues, recognise the correct information, and sometimes repeat the process to assemble everything required.

4. **Saving information does not guarantee later use.** People may forget that an item exists, fail to notice an available reminder or no longer understand why the information was originally retained.

5. **Keeping information creates cognitive and organisational costs.** Decisions about whether, where and how to retain information are difficult, while automatic “keep everything” approaches can produce clutter rather than a useful external memory.

6. **Meta-level activities are important but easily neglected.** Maintenance, evaluation and sense-making support long-term goals, but they rarely feel urgent and can therefore become afterthoughts.

7. **New tools should reduce rather than increase clerical tax.** A useful system must provide enough value to justify the time and attention required to maintain it, especially as a personal information collection grows.

### Limitation for ProjectOS

PIM explains why information becomes fragmented and difficult to reuse, but it does not specifically examine reflective creative practice or the reconstruction of evolving design rationales. It also does not evaluate source-grounded generative AI as a mediator between a creator’s current question and their earlier project records.

### ProjectOS implication

ProjectOS should work with existing project records instead of requiring users to maintain perfect folders, tags or constant manual documentation. Its retrieval interface should help users reconnect information with the current creative need, while making the supporting sources visible and allowing users to correct the reconstructed account.

---

## Updated synthesis and ProjectOS direction

Reading Czerwinski et al. (2004), Iqbal and Horvitz (2007), and Jones et al. (2017) together has changed how I define the problem that ProjectOS should address. Interruptions do not simply delay work; they create a resumption cost because people must reconstruct their goals, resources and partially completed thinking. PIM broadens this problem by showing that relevant information is often fragmented across files, notes, messages, browser tabs and applications. Even when information has been saved, users may forget that it exists, where it is located or why it was originally important.

However, ProjectOS should not become another generic file-management or search tool. Existing task-resumption research mainly examines short-term recovery after interruptions, while PIM research concentrates on keeping, organising and re-finding information. Neither area sufficiently addresses how creative practitioners reconstruct and critically reassess evolving intentions, feedback, discarded alternatives and decision rationales across a long-term project. This defines a more specific research opportunity for ProjectOS.

I therefore see RAG as a mechanism for evidence-grounded project reconstruction rather than automatic content generation. ProjectOS should reconnect users with relevant project materials, distinguish current decisions from outdated ones and invite reflection before work continues. It should also minimise clerical tax by working with existing records rather than demanding continuous documentation. The intended contribution is a reflective project memory that supports continuity while keeping creative judgement with the user.
