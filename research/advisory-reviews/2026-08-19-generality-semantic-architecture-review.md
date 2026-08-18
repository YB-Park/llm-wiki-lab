# Advisory Design Review — Generality, Semantic Structure, and Cross-Source Knowledge

Status: **ADVISORY / NON-BINDING / NOT AN ADR**  
Review date: **2026-08-19 KST**  
Review target snapshot: **`341c9fffbb32607681fe93add82f9fcfb6e9d555`**  
Repository: `YB-Park/llm-wiki-lab`  
Reviewer context: **AI-assisted architecture review conducted in conversation between the repository owner and OpenAI ChatGPT GPT-5.6 Sol**

> **Authority disclaimer**
>
> This document records an external/advisory design review of one repository snapshot. It is **not** an accepted project decision, an ADR, an implementation plan, a new critical-path item, or authorization to add infrastructure. Recommendations here must pass the project's normal question → evidence → experiment → ADR discipline before they become policy.
>
> The existence of this review must not be interpreted as permission to bypass the Alpha convergence rule, E013/E015 natural-evidence gates, the current HANDOFF priority, or the explicit `Do not start yet` boundaries.

## 1. Why this review exists

The review began with a broad question about whether the current LLM Wiki is becoming too close to a **document summarization / document-memory system**, rather than a genuinely general-purpose Wiki that an LLM can use as durable knowledge over time.

A concrete stress case made that question sharper:

- several important meeting records arrive as DOCX/PDF-like sources;
- several people appear across those records under names, aliases, roles, pronouns, or partial identifiers;
- an Outlook/email history contains additional high-value context, including direct authorship and thread structure;
- the user explicitly admits all of those materials into memory;
- months later, the user asks questions such as:
  - “Who was the person from ABC who kept raising the DPA concern?”
  - “What do we know about Park Jihoon from the admitted evidence?”
  - “Did J.H. Park and Park Jihoon refer to the same person?”
  - “What did that person directly say, versus what meeting notes said about them?”
  - “Did their role or position change over time?”

That scenario is useful because it forces the system to confront cross-source identity, attribution, time, provenance, synthesis, and retrieval at once.

However, it is **only a motivating stress case**.

> **This is not a proposal to turn LLM Wiki into a people directory, contact manager, CRM, phone book, or person-profile product.**
>
> “Person” is one difficult semantic object among many. The same architectural problem appears for organizations, projects, products, contracts, incidents, policies, research concepts, decisions, customers, technologies, events, and other long-lived knowledge subjects. The real question is not “How should we store people?” It is:
>
> **How should a trustworthy LLM Wiki recover and compound useful cross-source semantic knowledge without prematurely hard-coding one universal ontology or allowing derived structure to acquire false authority?**

## 2. Executive assessment

The review's assessment evolved during the discussion.

The first pass identified a real limitation: the current Agent Wiki implementation is **source-scoped and schema-shaped around source notes**, while the product philosophy aspires to richer entities, concepts, relationships, comparisons, tensions, and reusable synthesis. This creates a risk that the product could become a very trustworthy document-memory layer without yet becoming a general semantic Wiki.

An initial candidate response was therefore to add a durable **Knowledge IR / Entity layer** above the trustworthy raw substrate.

After adversarial re-review, that recommendation was deliberately weakened.

The revised position is:

> **A durable Knowledge IR, entity system, or graph-like semantic layer may eventually be valuable, but the project does not yet have enough evidence to promote one into the product architecture.**
>
> The safer next research question is whether a durable semantic structure is necessary at all for a given capability, or whether the same user value can be obtained through raw/source retrieval plus query-time or narrowly materialized derived projections.

The preferred working hypothesis after this re-review is:

> **Admitted evidence is stable authority; semantic structure is derived, replaceable, and must earn persistence through demonstrated retrieval, reasoning, or lifecycle value.**

A second useful formulation is:

> **Generality should be demonstrated at the capability/query boundary before it is enforced as uniformity at the storage boundary.**

This is intentionally more conservative than “build an entity/knowledge graph.”

## 3. What appears strong and should be protected

The project already has unusually strong defenses against the exact failure modes that a semantic layer could reintroduce.

At the reviewed snapshot, the important protections include:

- immutable/verified raw evidence as the authority floor;
- evidence revision identity separated from byte identity;
- explicit current/history lineage;
- explicit correction/change/dispute semantics rather than silent LLM inference;
- optional exact raw-span provenance without promoting it into a global claim graph;
- read-only answer boundaries for canonical state;
- clear separation of `RAW_MEMORY`, `DERIVED_MEMORY`, and `HUMAN_KNOWLEDGE`;
- derived Agent Wiki artifacts marked noncanonical/rebuildable;
- a project discipline that treats interesting architecture as insufficient evidence by itself;
- an Alpha convergence rule that explicitly blocks speculative new core infrastructure.

These are not obstacles to a more general Wiki. They are the reason a more general Wiki can be explored without turning model-generated structure into hidden authority.

Relevant reviewed sources include the [Project Charter](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/docs/00-project-charter.md), [Alpha Core Readiness Gate](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/docs/09-alpha-core-readiness-gate.md), [autonomy/UX philosophy](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/docs/12-autonomy-ux-philosophy.md), and the [reviewed HANDOFF](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/HANDOFF.md).

## 4. The real concern: document-centric derived knowledge

The product philosophy says the Agent Wiki should be able to summarize and link admitted evidence while recording entities, concepts, relationships, comparisons, unresolved tensions, and reusable synthesis.

The current implementation is narrower. At the reviewed snapshot, `agent_wiki.py` emits one source-scoped note with a fixed payload shape:

- `title`
- `summary`
- `operational_rules`
- `boundaries`
- `open_questions`

It also requires fixed minimum/maximum counts for some fields. See the reviewed [`dogfood/llm_wiki/agent_wiki.py`](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/dogfood/llm_wiki/agent_wiki.py).

That is a reasonable dogfood slice for technical/design sources, but it creates a generality question.

A meeting transcript, customer interview, legal memo, research paper, email thread, incident record, personal learning note, or market-research artifact may not naturally contain five-to-ten “operational rules” and three-to-eight “boundaries.” Requiring those fields can become a form of **semantic coercion**: the representation asks the source to fit the schema rather than letting the source's useful structure emerge.

This does **not** imply that the current source-note slice was a mistake. It implies only that:

> **`source-note-v0` should be treated as one derived projection under test, not silently generalized into the permanent ontology of the Wiki.**

## 5. Initial candidate: Knowledge IR / Entity layer

The first review pass considered a durable derived representation resembling:

```text
admitted evidence
      ↓
knowledge extraction
      ↓
knowledge units / entities / relations / events
      ↓
materialized Wiki views
      ↓
LLM retrieval and reasoning
```

A possible sparse Knowledge Unit might have contained concepts such as:

```text
unit_id
kind
statement
subject_refs
object_refs
effective_time?
evidence_refs
```

And a person-like derived entity might have connected multiple source mentions such as:

```text
Park Jihoon
J.H. Park
jihoon.park@example.com
```

with evidence-backed facts, authored statements, events, and temporal changes.

This direction remains a legitimate **experiment candidate**. It could support cross-source compounding, alias-aware lookup, timeline reasoning, multi-hop questions, and reusable materialized views.

But the re-review found that promoting this directly into product architecture would be premature.

## 6. Why the initial Knowledge IR proposal is dangerous if promoted too early

### 6.1 Semantic laundering

Structure creates an appearance of certainty.

Suppose the evidence contains:

- a direct email: “I think we need DPA review before proceeding”;
- a meeting note: “Park raised a security concern”;
- a model synthesis: “Park repeatedly appears as a security-sensitive stakeholder.”

A naive graph/IR can collapse those into visually similar relationships:

```text
Park -> requested -> DPA review
Park -> concerned_about -> security
Park -> has_trait -> conservative
```

The first may be strongly sourced. The second may be an attributed observation. The third may be an unsupported or over-broad characterization.

Once all three are persisted as structured facts, the system can accidentally **upgrade inference into fact by representation**.

This would undermine the project's existing RAW / DERIVED / HUMAN epistemic separation even if no raw bytes were modified.

### 6.2 False merge has a larger blast radius than ordinary retrieval failure

If two different people are merged into one durable entity, downstream state can mix:

- one person's emails;
- another person's meeting comments;
- the first person's role;
- the second person's project involvement;
- derived characterizations built on both.

A false split is inconvenient. A false merge can contaminate a long-lived semantic object and every derived view that depends on it.

Therefore entity identity is not automatically “routine filing.” In ambiguous cases it can become a high-consequence semantic judgment.

### 6.3 Taxonomy/schema lock-in

The Charter already lists taxonomy drift, summary collapse, false precision, retrieval blindness, and maintenance debt as threats. A universal semantic schema can reintroduce all of them at once.

The project's own [initial synthesis](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/research/02-initial-synthesis.md) explicitly warned against prematurely choosing `concept/entity/source` as a permanent ontology or assuming one permanent knowledge unit.

### 6.4 Maintenance amplification

A single newly admitted source might require updates to multiple person views, project views, concept pages, timelines, relation indexes, and alias maps.

That can transform “remember this source” into a large semantic maintenance event. Cost, regressions, and model-induced write amplification can grow much faster than user value.

### 6.5 Derived retrieval can dominate raw evidence incorrectly

A concise persistent profile is attractive to retrieval. If it is wrong or overgeneralized, the system may repeatedly retrieve that derived object instead of the underlying heterogeneous evidence.

A semantic layer must therefore remain a navigation/compilation aid, not an irreversible compression boundary.

## 7. A more conservative abstraction: Evidence Core + Derived Projections

The preferred architecture hypothesis after re-review is not “one universal Knowledge IR.” It is a stable trust core with **multiple optional derived projections**.

```text
                       USER / LLM
                           │
                      query / task
                           │
              ┌────────────┴────────────┐
              │                         │
       derived projections        raw/source retrieval
              │                         │
     ┌────────┼─────────┐               │
     │        │         │               │
 source    person     concept        exact/history
 note      dossier    synthesis       evidence
     │        │         │               │
     └────────┴─────────┴──────┬────────┘
                               │
                       grounded context
                               │
                               ▼
                              LLM

-------------------------------------------------------------

                    TRUST / AUTHORITY CORE

 admitted evidence
 evidence identity / integrity
 provenance
 current / history
 correction / change / dispute
 human admission
 Human Knowledge authorship
```

The important invariant is:

> **The Trust Core should not need to understand the semantic ontology used by a derived projection.**

This makes the core general because it is largely **knowledge-type agnostic**, not because it knows every knowledge type.

A future projection might be:

- `source-note-v0`
- an ephemeral person dossier
- a persistent fixed-identity person dossier
- a decision-history view
- a timeline
- a concept synthesis
- a project summary
- a semantic search index

Those representations do not need to share one permanent ontology on day one.

They should share authority rules:

- derived;
- noncanonical;
- inspectable;
- reversible/rebuildable;
- provenance-bound;
- unable to silently become Human Knowledge or Raw Evidence.

## 8. The key question: must semantic structure be persistent?

The motivating user capability does **not** automatically require a persistent entity store.

For a query such as:

> “Who was the ABC person who kept raising the DPA concern?”

one possible implementation is purely query-time:

```text
query
  ↓
retrieve relevant admitted evidence / source notes
  ↓
LLM identifies candidate person and relevant mentions
  ↓
retrieve additional evidence
  ↓
build temporary cross-source dossier
  ↓
answer with provenance
  ↓
discard temporary dossier
```

If this reliably answers the user's questions, then a persistent `person-0172`, alias lifecycle, entity merge/split machinery, graph maintenance, and schema migration may not be justified.

This is especially important for an LLM-facing Wiki. Traditional human wikis need persistent pages for navigation. An LLM can potentially construct a useful view **on demand**.

Therefore:

> **The product requirement is “the LLM can recover and use the knowledge,” not “a permanent node/page must exist internally.”**

## 9. Persistence should be earned by repeated value

A semantic projection may deserve persistence if natural use demonstrates that query-time reconstruction is too expensive, inconsistent, slow, or retrieval-fragile.

For example, a persistent person dossier might become justified if:

- the same identity is repeatedly reconstructed across sessions;
- alias ambiguity causes recurring failures;
- repeated cross-source synthesis consumes material model budget;
- query-time reconstructions disagree despite stable evidence;
- a maintained dossier materially improves downstream answer quality;
- the lifecycle/review burden remains manageable.

This suggests a staged progression:

```text
query-time synthesis
        ↓
fixed-identity persistent synthesis
        ↓
identity candidate suggestions
        ↓
bounded automatic identity/routing
```

The last step should not be assumed merely because the first two work.

## 10. E021 is encouraging, but narrower than an entity system

[E021 cross-source concept compounding](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/experiments/E021-concept-compounding/results-v0.md) is important positive evidence.

It showed that, for a **fixed concept identity and deliberately relevant source sequence**, Luna could maintain one derived/noncanonical/rebuildable concept page across multiple sources while retaining admitted raw provenance and treating prior generated state as working state rather than evidence.

That earns confidence in the **compounding mechanism**.

It does not demonstrate:

- automatic concept/entity discovery;
- identity resolution;
- deduplication;
- automatic source-to-concept routing;
- refresh timing;
- large-scale semantic retrieval;
- graph/ontology infrastructure.

E021 itself explicitly records those boundaries and says not to ship automatic concept routing from the result alone.

The safe inference is:

> **Fixed-target cross-source derived compounding is promising. Semantic target discovery/routing/identity remains a separate problem.**

## 11. Entity identity should remain derived and reversible if tested

If a person/entity projection is tested, its identity should initially be treated as a **derived semantic aid**, not raw authority.

A future experimental entity could therefore be:

```text
DERIVED
NONCANONICAL
REVERSIBLE
SPLITTABLE
MERGEABLE
REBUILDABLE
```

Strong identity signals may be handled differently from weak signals.

Examples of potentially strong signals:

- the same stable email address in structured message metadata;
- a deterministic contact identifier from a trusted source adapter;
- explicit human confirmation that two mentions are the same person.

Examples of weak/ambiguous signals:

- name similarity;
- abbreviation similarity;
- same role in nearby text;
- model inference from context alone.

Ambiguous identity does not always need to be resolved during ingest. A query can surface the ambiguity when it matters:

> “The stored evidence does not establish whether J.H. Park and Park Jihoon are the same person.”

This “resolve on consequence” strategy may avoid both approval storms and premature semantic mutation.

## 12. Source format generality is a separate architectural problem

The motivating scenario mentions PDF, DOCX, and Outlook/email artifacts. That should **not** be conflated with the semantic/entity question.

The reviewed dogfood shell is primarily UTF-8 text oriented. Binary/source-container formats introduce a separate provenance problem:

```text
Original Artifact
  PDF / DOCX / MSG / EML
  immutable bytes + hash
        │
        │ extractor/parser + version
        ▼
Normalized Rendition
  text / blocks / headers / tables / message parts
        │
        ▼
Semantic Projection(s)
```

The normalized text of a PDF is not necessarily the original evidence artifact; it is an extraction/rendition of that artifact. DOCX and MSG likewise contain structure and metadata that should not be flattened casually.

A robust future source-adapter contract may need to preserve:

- original immutable artifact identity;
- normalized/extracted representation;
- parser/extractor identity and version;
- structural locators such as page, block, message header/body, thread, table, or attachment;
- a path from semantic claim → normalized region → original artifact.

This is a separate experiment axis.

The first person/generalization experiment should preferably use **frozen normalized text fixtures** so that parser quality does not confound the semantic representation result. Binary ingestion/provenance can then be evaluated independently and later combined.

## 13. Attribution is more subtle than entity linking

Cross-source person knowledge must distinguish at least these epistemically different cases:

1. a person directly authored a statement in an email;
2. a meeting record says the person said something;
3. a forwarded/quoted message contains text originally authored by someone else;
4. a derived Wiki synthesis characterizes a pattern across several sources.

These should not silently collapse into the same semantic relation.

For example:

```text
"Park requested DPA review in a direct email"
```

is different from:

```text
"Meeting notes attribute a DPA concern to Park"
```

which is different from:

```text
"Across admitted sources, Park appears to be a recurring stakeholder on privacy/security questions"
```

The last statement may be useful, but it is clearly **derived characterization**.

The project should be especially cautious about converting repeated observations into durable personality/profile assertions such as “security conservative” or “opposes SaaS.” Those are often broader than the evidence supports and are not necessary to satisfy the core Wiki use case.

## 14. Provenance must bottom out in admitted evidence

The reviewed [ADR-0006](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/decisions/ADR-0006-local-exact-raw-span-provenance-not-claim-graph.md) made an important narrow decision: exact raw-span provenance can exist without becoming a global claim graph, and the pointer itself is not authority.

That discipline should extend to semantic projections.

A projection may use prior generated state as **working state**, as E021 did. But durable derived claims should not form an evidentiary chain such as:

```text
person dossier
  ↓ evidence
concept page
  ↓ evidence
source note
  ↓ evidence
another source note
```

The evidence chain must eventually resolve to admitted evidence.

A useful invariant is:

> **Every load-bearing durable derived claim must be able to bottom out in admitted evidence; another derived artifact may help compilation, but it does not become primary evidence merely because it persisted.**

## 15. Persistent updates are transitions, not just final documents

If a semantic dossier is ever persisted, validating only the new final text is insufficient.

Example:

```text
old dossier: A, B, C
new evidence: D
new dossier: A, C, D
```

Every surviving sentence may be individually grounded, yet important prior knowledge `B` disappeared.

This is compilation loss / maintenance regression.

The project's own research already identifies fabrication, omission/compilation loss, temporal corruption, structural corruption, and maintenance-induced regression as distinct failure classes. See [Initial Synthesis](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/research/02-initial-synthesis.md).

Adjacent memory research such as TRUSTMEM further motivates evaluating memory updates as transitions with coverage, preservation, and faithfulness rather than only scoring the final state.

This increases the cost of a persistent semantic layer and is another reason not to create one before it is needed.

## 16. Proposed Generality Gate — architecture-neutral first

The recommended next semantic/generalization experiment is not “build an entity system.”

It is:

> **For heterogeneous admitted sources, is persistent semantic identity required to recover cross-source knowledge reliably enough to justify its lifecycle cost, or are raw/source projections plus query-time synthesis sufficient?**

A useful experimental matrix is:

| Variant | Persistent semantic state | Purpose |
|---|---:|---|
| **A. Raw + current retrieval** | No | Strong simple baseline |
| **B. Raw + current source Agent Notes** | Source-scoped only | Current product-shaped baseline |
| **C. Query-time semantic dossier** | No | Test cross-source synthesis without semantic persistence |
| **D. Fixed-identity persistent dossier** | Yes, identity supplied/frozen | Test value of persistence separately from identity resolution |
| **E. Automatic identity/routing** | Yes | Test the hardest automation only after persistence earns value |

The order matters.

Do **not** start at E.

### Why C matters

If C solves the motivating user questions well, the project can avoid a large class of entity lifecycle complexity.

### Why D is separate from E

If D materially outperforms C, persistent compounding may be valuable even if automatic entity resolution is unsafe. A product could still support user-confirmed/fixed identity and obtain most of the benefit.

### Why E comes last

Automatic identity/routing should be tested only after the project has demonstrated that a persistent target is worth maintaining at all.

## 17. Suggested frozen challenge corpus

The corpus should be deliberately broader than the current developer-document dogfood while remaining small enough to audit manually.

A person-heavy cross-source scenario is useful, but only as one test family.

One frozen bundle might contain 15–30 normalized sources with 8–12 recurring participants and deliberately include:

- aliases and abbreviations;
- English/Korean or alternate name forms;
- same/similar names for different people;
- stable identifiers such as email addresses in structured metadata;
- role changes over time;
- organization changes;
- direct authored email statements;
- meeting-note attribution;
- forwarded/quoted email text;
- pronouns and shorthand references;
- duplicated/copied message content;
- sources that disagree;
- formerly-correct but no-longer-current roles;
- facts relevant only after cross-source synthesis.

The corpus should also contain non-person semantic targets so the test does not accidentally optimize the architecture for “people pages.” Examples:

- a project whose decision rationale is distributed across meetings and email;
- a vendor contract whose constraints appear across memo/email/meeting sources;
- a technical concept whose understanding evolves across research notes;
- an incident whose timeline spans messages and postmortem notes;
- a customer requirement repeated under different wording.

## 18. Suggested questions

Person-oriented questions can include:

- Who is Park Jihoon in the admitted evidence?
- Is J.H. Park the same person as Park Jihoon?
- Who first raised the DPA concern?
- What did Park directly author versus what was attributed to Park by others?
- Did Park's role change over time?
- Did Park's position actually change, or did the source context change?
- Show the original evidence for this answer.

General cross-source questions should also include:

- Why was Vendor X adoption delayed?
- Which constraints recur across the contract memo, meetings, and email thread?
- How did our understanding of Concept Y change over time?
- Which sources disagree about the incident root cause?
- What customer requirement appears repeatedly under different wording?
- What do we know now, what did we believe earlier, and why did it change?

This prevents the experiment from degenerating into a contact-management benchmark.

## 19. Evaluation should separate failure classes

Do not reduce the Generality Gate to one answer-accuracy score.

At minimum, consider separate measurements for:

- answer correctness;
- evidence recall;
- exact provenance resolvability;
- wrong-person / wrong-entity attribution;
- false merge;
- false split;
- temporal correctness;
- direct-vs-indirect attribution correctness;
- unsupported characterization / epistemic upgrade;
- compilation loss across updates;
- retrieval failure despite stored evidence;
- model calls / tokens / lifecycle maintenance cost;
- human intervention count;
- repair/rebuild cost after an injected semantic mistake.

False merge and unsupported characterization deserve especially strong scrutiny because they can create durable misinformation about a semantic subject while appearing internally coherent.

## 20. The baseline must remain strong and simple

A sophisticated memory architecture should not be compared only against a weaker previous Wiki variant.

The meaningful competitor is increasingly:

```text
raw admitted evidence
+ good retrieval
+ sufficient context
+ capable LLM
```

If a persistent semantic layer delivers only marginal utility while multiplying maintenance, review, migration, and repair cost, the architecture has not earned itself.

The project's existing research already recognizes this. The [Agent Memory and Consolidation review](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/research/03-agent-memory-consolidation.md) explicitly argues that elaborate memory should be compared against raw/search/long-context baselines and that heterogeneous information may need heterogeneous maintenance policy.

## 21. Promotion rules should be written before implementation

A future Generality Gate should preregister decision conditions rather than letting an attractive result justify whichever architecture was just built.

Illustrative logic:

```text
If B ≈ A:
  current source-note layer has not demonstrated generality value in this corpus.

If C materially > B:
  cross-source query-time semantic compilation is valuable.
  Do not infer that persistence is needed.

If D materially > C across repeated natural-like queries/updates:
  persistent fixed-target semantic projection may be earned.
  Evaluate lifecycle cost and transition safety.

Only if D is already earned and identity/routing remains a material blocker:
  test E automatic identity/routing.
```

The exact thresholds should be preregistered separately; this review does not set them.

## 22. What this review does **not** recommend

This review does not recommend, authorize, or imply a need to immediately build:

- a graph database;
- RDF/OWL or a universal ontology;
- a permanent `Entity`/`Relation` core schema;
- a universal `KnowledgeUnit` as canonical or near-canonical truth;
- automatic person profiling;
- a contact/CRM/phone-book product;
- broad automatic entity merge/split;
- automatic concept routing from E021;
- vector search as a new default merely because paraphrase retrieval is desirable;
- binary PDF/DOCX/MSG ingestion and semantic architecture in one combined change;
- background semantic maintenance;
- autonomous canonical mutation;
- replacement of raw evidence with summaries/graphs;
- promotion of derived artifacts into evidence.

A graph, vector index, entity store, or Knowledge IR could still become useful later. The point is that each should be justified by a concrete failure/value boundary rather than by architectural elegance.

## 23. Relationship to current project decisions and gates

This review is intended to **strengthen**, not bypass, existing project discipline.

### Project Charter

The [Project Charter](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/docs/00-project-charter.md) already says the project is not initially trying to create a universal ontology or graph database and explicitly lists taxonomy drift, summary collapse, false precision, retrieval blindness, maintenance debt, and automation complacency as threats.

### Design-question register

The reviewed [Design Question Register](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/docs/02-design-questions.md) keeps the canonical knowledge unit, fact/interpretation/hypothesis distinctions, metadata-vs-prose structure, hierarchy, taxonomy evolution, and entity/alias resolution open or experimental. This review should not silently close those questions.

### Alpha Core convergence rule

The [Alpha Core Readiness Gate](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/docs/09-alpha-core-readiness-gate.md) says to stop adding core infrastructure by default and requires actual dogfood failure, preregistered evidence-boundary crossing, or trust/data-loss failure before new core work is justified.

### ADR-0006

[ADR-0006](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/decisions/ADR-0006-local-exact-raw-span-provenance-not-claim-graph.md) deliberately accepted a narrow exact-provenance capability while rejecting a global claim graph. Its “pointer, not authority” framing is a useful precedent for keeping semantic projections derived and scoped.

### Autonomy philosophy

The [autonomy/UX philosophy](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/docs/12-autonomy-ux-philosophy.md) already provides the correct authority split: human admission/epistemic commitment versus LLM-owned routine derived compilation/maintenance inside granted scope. Semantic projections fit naturally inside the Agent Wiki only while they remain reversible/noncanonical and do not impersonate human knowledge or rewrite source meaning.

### E021

[E021](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/experiments/E021-concept-compounding/results-v0.md) provides narrow positive evidence for fixed-target cross-source derived compounding, not automatic identity/routing.

### Current HANDOFF

The reviewed [HANDOFF](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/HANDOFF.md) explicitly says not to start vector/graph/ontology infrastructure, automatic concept routing from E021, federation, or chunk compilation without natural evidence. This review is not intended to alter that immediate priority.

## 24. External/adjacent research consulted

These references informed the review as **adjacent evidence and alternative architectural patterns**, not as direct validation of this repository's workload.

### Retrieval and cross-source structure

- **GraphRAG — From Local to Global: A Graph RAG Approach to Query-Focused Summarization**  
  https://arxiv.org/abs/2404.16130  
  Relevant because it derives an entity graph/community summaries from source documents for corpus-level/global questions. It is evidence that graph-like derived indexes can help some retrieval classes, not evidence that this Wiki needs a canonical graph.

- **HippoRAG — Neurobiologically Inspired Long-Term Memory for Large Language Models**  
  https://arxiv.org/abs/2405.14831  
  Relevant because graph structure and Personalized PageRank are used for associative/multi-hop retrieval. Again, this supports a retrieval hypothesis, not a storage mandate.

- **RAPTOR — Recursive Abstractive Processing for Tree-Organized Retrieval**  
  https://arxiv.org/abs/2401.18059  
  Relevant as a counterexample to “semantic generality requires an entity graph”: hierarchical derived summaries can improve broader/holistic retrieval with a different representation.

### Long-term memory and selective representation

- **MemGPT — Towards LLMs as Operating Systems**  
  https://arxiv.org/abs/2310.08560  
  Relevant for hierarchical memory/context management and the principle that not all persistent state belongs in every model context.

- **A-MEM — Agentic Memory for LLM Agents**  
  https://arxiv.org/abs/2502.12110  
  Relevant for dynamically linked/evolving memory and the corresponding risk of relationship-maintenance write amplification.

- **Mem0 — Building Production-Ready AI Agents with Scalable Long-Term Memory**  
  https://arxiv.org/abs/2504.19413  
  Relevant for separating extraction, consolidation, persistence, and retrieval; its graph variant also illustrates that relational structure is an optional enhancement rather than the only possible memory form.

- **Zep — A Temporal Knowledge Graph Architecture for Agent Memory**  
  https://arxiv.org/abs/2501.13956  
  Relevant for treating changing facts and historical relations as first-class memory concerns. It does not by itself justify a graph for this project.

### 2026 memory research especially relevant to the re-review

- **Infini Memory — Maintainable Topic Documents for Long-Term LLM Agent Memory**  
  https://arxiv.org/abs/2606.10677  
  Relevant because observations can be staged and periodically consolidated into topic documents rather than immediately rewritten into one universal semantic store.

- **TRUSTMEM — Learning Trustworthy Memory Consolidation for LLM Agents with Long-Term Memory**  
  https://arxiv.org/abs/2606.25161  
  Relevant because it frames persistent memory updates as transitions that should preserve coverage, preservation, and faithfulness.

- **LeanMem — Simple and Efficient Long-Term Memory for LLM Agents**  
  https://arxiv.org/abs/2608.03463  
  Relevant because heterogeneous information is routed into profile/event/source-grounded record memory according to different fidelity and temporal needs, challenging one-representation/one-maintenance-policy designs.

- **EvoMemBench — Benchmarking Agent Memory from a Self-Evolving Perspective**  
  https://arxiv.org/abs/2605.18421  
  Relevant because strong long-context baselines remain competitive and no single memory form is uniformly best across settings. This strengthens the requirement that a complex semantic layer must beat a strong simpler baseline on the project's actual workload.

The repository's own [Agent Memory and Consolidation research](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/research/03-agent-memory-consolidation.md) contains additional project-specific interpretation of several of these systems.

## 25. Conditions that should cause this assessment to be revisited

This review should not become a frozen doctrine. Revisit it when evidence changes.

Examples:

1. natural installed use repeatedly fails to recover cross-source people/project/concept knowledge that the user reasonably expects the Wiki to remember;
2. query-time cross-source synthesis is measurably too expensive, slow, or inconsistent;
3. fixed-identity persistent compounding materially improves repeated retrieval/reasoning over ephemeral synthesis;
4. alias/entity ambiguity becomes a recurring real-user blocker;
5. a non-entity projection (timeline, decision view, concept page, hierarchical summary) clearly solves the same failures more cheaply;
6. source-format generality introduces provenance failures that change the architecture assumptions;
7. semantic maintenance causes recurrent compilation loss, contamination, or review burden;
8. future model/context improvements make a previously useful persistent projection unnecessary.

## 26. Recommended interpretation of “generality” for now

The project should resist two opposite mistakes:

1. **Document-only complacency** — assuming source summaries are automatically a sufficiently general Wiki.
2. **Ontology-first overreaction** — assuming a general Wiki requires a universal semantic schema before the workload proves it.

A better current target is:

> **A general LLM Wiki can admit heterogeneous evidence, preserve its authority and provenance, and let the LLM recover the right cross-source semantic view for a task — while only persisting semantic structures whose long-term value has been demonstrated.**

That view may be a source note, temporary person dossier, concept synthesis, decision history, timeline, or something not yet designed.

The implementation should remain free to discover which representations are actually useful.

## 27. Concise takeaway

The motivating “multiple meeting records + email history + recurring people” scenario exposed a real generality gap, but it should not narrow the product into a people-memory system.

The deeper issue is whether the Wiki can move beyond **document-centric derived notes** into reliable **cross-source semantic use** without sacrificing the trust properties that make the project distinctive.

The first instinct — add a Knowledge IR/entity layer — remains plausible, but is too large a product commitment without comparative evidence.

The safer hypothesis is:

> **Stable evidence core + optional rebuildable semantic projections + strong raw fallback.**

And the next semantic architecture decision, when natural evidence makes it relevant, should be earned through a Generality Gate that compares:

```text
raw retrieval
vs source notes
vs query-time semantic synthesis
vs fixed-target persistent synthesis
vs automatic identity/routing
```

rather than assuming the last and most complex option in advance.

---

## Appendix A — reviewed repository references

All links below are pinned to the exact reviewed repository snapshot `341c9fffbb32607681fe93add82f9fcfb6e9d555` so that later edits do not silently change what this review was reacting to.

- [README — project framing and experiment-before-policy rule](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/README.md)
- [Project Charter](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/docs/00-project-charter.md)
- [Research Map](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/docs/01-research-map.md)
- [Design Question Register](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/docs/02-design-questions.md)
- [Alpha Core Readiness Gate](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/docs/09-alpha-core-readiness-gate.md)
- [Autonomy and UX philosophy](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/docs/12-autonomy-ux-philosophy.md)
- [HANDOFF at review snapshot](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/HANDOFF.md)
- [ADR-0006 — exact local provenance, not claim graph](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/decisions/ADR-0006-local-exact-raw-span-provenance-not-claim-graph.md)
- [Initial Synthesis After Direct LLM Wiki Research](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/research/02-initial-synthesis.md)
- [Agent Memory and Consolidation — Research Batch B](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/research/03-agent-memory-consolidation.md)
- [E021 — cross-source Agent Wiki concept compounding v0](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/experiments/E021-concept-compounding/results-v0.md)
- [`agent_wiki.py` — current source-note projection implementation](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/dogfood/llm_wiki/agent_wiki.py)
- [Dogfood README — current raw/retrieval/provenance shell and source scope](https://github.com/YB-Park/llm-wiki-lab/blob/341c9fffbb32607681fe93add82f9fcfb6e9d555/dogfood/README.md)

## Appendix B — status vocabulary for this review

To avoid accidental authority inflation:

- **Observation** — something visible in the reviewed repository state.
- **Concern** — a plausible failure/risk inferred from that state.
- **Hypothesis** — a candidate explanation or design direction requiring evidence.
- **Experiment candidate** — a proposed way to discriminate among hypotheses.
- **Recommendation** — advisory prioritization, not project policy.
- **Decision** — **not created by this document**; project decisions still require the repository's ADR process.
