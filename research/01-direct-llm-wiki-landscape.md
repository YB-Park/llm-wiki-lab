# Direct LLM Wiki Landscape — Research Batch A

Date: 2026-08-12
Status: research note, not policy
Related: Issue #2

## 1. Purpose

This note surveys systems that directly implement, extend, or experimentally study the LLM Wiki pattern. The goal is not to choose our architecture. The goal is to extract observed mechanisms, failure modes, evidence quality, and experiment implications.

We intentionally separate:

- **Primary design source** — the original pattern or paper.
- **Implementation evidence** — inspectable code/docs describing an operating system.
- **Benchmark evidence** — controlled evaluation with published methodology.
- **Deployment/case-study evidence** — reported real use, often with weaker causal control.
- **Our interpretation** — hypotheses to test, not facts.

Preprints referenced here are not assumed to be peer reviewed.

## 2. Systems reviewed

1. Andrej Karpathy — original `llm-wiki.md` idea file.
2. Astro-Han `karpathy-llm-wiki` — Agent Skills implementation with explicit grounding/lint rules.
3. Nihar Shrotri `llm-wiki` — local-first implementation with structured ingest and hybrid retrieval.
4. LLM-Wiki — *Retrieval as Reasoning: Self-Evolving Agent-Native Retrieval via LLM-Wiki*.
5. WiCER — *Wiki-memory Compile, Evaluate, Refine*.
6. WikiKV — *Schema-Evolving Path-Indexed Storage for Hierarchical Knowledge Navigation*.
7. WikiLoop — *Jointly Learning to Build and Navigate Agent-Native Wikis with Downstream Feedback*.
8. *Beyond Memory* — reusable llm-wiki template plus reported collaborative case studies.

## 3. Original Karpathy pattern

Primary source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

### 3.1 Core model

Karpathy frames the wiki as a **persistent, compounding artifact** between immutable raw sources and the user/agent. Instead of rediscovering cross-document synthesis at query time, new sources are integrated into existing entity/concept/topic pages. The schema/agent instruction file is explicitly part of the architecture and is expected to co-evolve with use.

Three layers:

1. raw sources — curated and immutable,
2. wiki — LLM-owned derived markdown,
3. schema — operating conventions and workflow rules.

Three main operations:

- ingest,
- query,
- lint.

### 3.2 Human role

The original idea is not fully autonomous. Karpathy explicitly says he prefers one-source-at-a-time ingest and remains involved: reading summaries, checking updates, and steering emphasis. Batch ingest with less supervision is presented as an alternative workflow, not the default truth.

This matters for our automation research: the founding pattern already treats automation boundary as a user-specific design choice.

### 3.3 Retrieval

At moderate scale, the proposed baseline is deliberately simple: read `index.md`, then drill into relevant wiki pages. Karpathy reports that an index can work at around ~100 sources / hundreds of pages and suggests adding local search only as scale demands it.

This supports a "complexity on evidence" principle: do not assume embeddings/MCP/graph retrieval are necessary for the first personal-wiki prototype.

### 3.4 Lifecycle hints

The original lint operation is expected to inspect:

- contradictions,
- stale/superseded claims,
- orphan pages,
- missing concept pages,
- missing cross-references,
- knowledge gaps.

However, the original document does **not** define rigorous semantics for overwrite, supersession, deletion, temporal validity, split/merge, or provenance granularity. Those are left to the instantiation.

### 3.5 Important limitation

The source is an idea file, not an empirical validation. Statements such as maintenance becoming cheap because LLMs can update many files are a design intuition/experience report, not evidence that autonomous maintenance remains reliable over long horizons.

---

## 4. Astro-Han `karpathy-llm-wiki`

Primary implementation: https://github.com/Astro-Han/karpathy-llm-wiki

### 4.1 Why it is important

This implementation converts the abstract pattern into explicit operating rules suitable for coding agents. It is especially useful because the rules expose concrete answers to questions the original gist leaves open.

### 4.2 Representation and organization

- immutable `raw/`,
- compiled `wiki/`,
- global `wiki/index.md`,
- append-only `wiki/log.md`,
- shallow topic hierarchy,
- article templates and machine-readable conventions.

### 4.3 Ingest triage

Before editing the wiki, the implementation classifies a source as:

- New,
- Update,
- Disputed,
- No material.

`No material` is important: ingestion does not imply that a wiki page must change. This is a practical defense against growth-for-growth's-sake and should become an explicit experiment variable later.

### 4.4 Grounding invariant

The strongest mechanism in this implementation is a specific grounding rule: load-bearing exact facts such as numbers, dates, and direct quotations must be locatable in linked immutable raw sources before being written into the wiki. A deterministic evidence checker is used for high-signal literals.

This is materially different from generic "please cite sources" prompting. It turns part of provenance into an executable invariant.

### 4.5 Update semantics

When newer evidence supersedes or contradicts an existing claim, the implementation says to keep the historical claim and annotate it as `Outdated` or `Disputed` rather than silently rewriting history.

That is a concrete candidate for E003 temporal/update experiments, but it should not be adopted yet. It may preserve too much noise in some personal domains.

### 4.6 Failure handling

Lint distinguishes safe mechanical repairs from semantic changes. It checks index consistency and evidence, while missing entries are marked rather than blindly deleted. This is an early example of automation boundaries based on edit risk.

### 4.7 Evidence quality caveat

The repository reports a production knowledge base maintained daily since April 2026 and provides usage statistics. Treat those numbers as maintainer-reported operational evidence, not independent benchmark validation.

---

## 5. Nihar Shrotri `llm-wiki`

Primary implementation: https://github.com/NiharShrotri/llm-wiki

### 5.1 Why it is important

This implementation explores a more engineered end-to-end system rather than relying on an agent reading arbitrary markdown. It is useful for studying how explicit pipelines change the automation boundary and cost profile.

### 5.2 Representation

Each ingest can generate a cluster of:

- source pages,
- entity pages,
- concept pages,
- synthesis pages.

Pages use YAML frontmatter and wikilinks.

### 5.3 Three-pass ingest

The documented ingest pipeline is:

1. structured extraction from source,
2. page drafting/merge per entity or concept,
3. source summary recording pages touched for provenance.

This pipeline reduces some degrees of freedom compared with a fully agentic "read source and edit whatever seems right" flow, but it also introduces ontology assumptions: entity/concept extraction is privileged as the knowledge model.

### 5.4 Human intervention

Ingest is interactive by default: the system shows extracted entities/concepts before filing and requests confirmation per source. This is directly relevant to our automation-boundary research. It demonstrates a practical middle ground between autonomous ingestion and manual authoring.

### 5.5 Retrieval escalation

The implementation supports three query scopes:

- Wiki — thematic synthesis from compiled pages,
- Raw — exact lookup in originals,
- Hybrid — both.

It also uses BM25 + vector similarity + LLM reranking before hydrating top pages. This gives us a concrete design for E006: "compiled synthesis" and "raw evidence" do not need to be mutually exclusive systems; they can be query modes in one system.

### 5.6 Cost-control signal

The project includes intent classification so trivial conversational turns can skip retrieval. The exact reported latency savings are implementation-specific, but the architectural lesson is broader: not every interaction should automatically invoke the full memory pipeline.

### 5.7 Risks

- entity/concept extraction may overproduce pages,
- one LLM call per entity/concept can make ingest expensive,
- hybrid search infrastructure adds complexity before we know our corpus needs it,
- preserving prior page content while appending sources does not by itself solve semantic contradiction or temporal correctness.

---

## 6. LLM-Wiki research system — Retrieval as Reasoning

Primary paper: https://arxiv.org/abs/2605.25480

### 6.1 Main contribution

The paper treats retrieval as an iterative agent reasoning process rather than one-shot similarity lookup. Documents are compiled into structured wiki pages with bidirectional links. The agent receives search/read/link-following tools and can navigate until evidence is sufficient.

### 6.2 Error Book

The system includes a persistent Error Book for structural and semantic self-correction. The important conceptual move is that **failure experience becomes durable system state** instead of being corrected once and forgotten.

This strongly motivates E008 (error-book / feedback learning), but we need to test whether natural-language error rules improve a personal wiki or become a growing pile of brittle prompt patches.

### 6.3 Benchmark evidence

The paper reports improvements over several RAG/graph baselines on multi-hop QA datasets (HotpotQA, MuSiQue, 2WikiMultiHopQA) and on AuthTrace, with especially strong gains on structured multi-document queries.

This is evidence that agent-navigable compiled structure can improve some multi-document retrieval workloads. It is **not** direct evidence that the same structure improves long-lived personal knowledge management, where temporal updates, private notes, changing preferences, and maintenance cost are central.

### 6.4 Transfer risk

The benchmark task optimizes answer retrieval from a knowledge corpus. Our project also cares about:

- long-horizon contamination,
- maintenance debt,
- human trust,
- deletion/supersession,
- token cost over months,
- subjective usefulness,
- IDE workflow friction.

Those dimensions require separate experiments.

---

## 7. WiCER — the compilation-gap warning

Primary paper: https://arxiv.org/abs/2605.07068

### 7.1 Main finding

WiCER directly challenges a naive assumption behind LLM Wiki systems: a coherent compiled wiki may have silently discarded facts required for future questions.

Across 17 RepLiQA domains, the paper reports that blind compilation over-compressed source material and produced much worse QA quality than raw full-context baselines, with 53–60% catastrophic failure rates under the tested wiki conditions.

### 7.2 Proposed repair loop

WiCER uses a CEGAR-inspired loop:

1. compile,
2. evaluate with diagnostic probes,
3. identify failed probes,
4. diagnose source facts missing from the wiki,
5. recompile with cumulative preservation constraints.

The reported result is that one or two targeted iterations recover a large fraction of the lost quality and reduce catastrophic failures. The ablation indicates targeted diagnosis is much more useful than generic "preserve more" instructions.

### 7.3 Implication for our project

**Readability is not a sufficient wiki-quality metric.**

A page can be elegant, accurate in what it says, and still be a bad memory because it omitted the fact a future query needs.

Therefore our evaluation must test information loss through downstream queries/probes, not merely unsupported hallucinations.

### 7.4 New risk: probe overfitting

WiCER also creates a question for us: if we preserve only facts exposed by known diagnostic probes, do we optimize the wiki around yesterday's questions? A personal wiki may need a mix of:

- generic high-value preservation rules,
- synthetic adversarial probes,
- real query failures,
- sampled source-to-wiki coverage audits.

This has been opened separately as an experiment candidate in Issue #3.

---

## 8. WikiKV — schema evolution becomes a storage problem

Primary paper: https://arxiv.org/abs/2606.14275

### 8.1 Main contribution

WikiKV treats an LLM-curated hierarchical wiki as a continuously evolving storage workload. It proposes:

- data-driven initial schema induction,
- Continuous Evolution Operators for schema refinement,
- path-indexed storage,
- navigation designed around hierarchical descent.

### 8.2 Deployment evidence

The paper reports evaluation in a real-world deployment for the WeChat Official Account AI Assistant and an end-to-end AuthTrace evaluation. This makes it one of the more concrete pieces of evidence that schema-evolving hierarchical wikis can operate beyond toy personal vaults.

### 8.3 What transfers to us

The scale and backend are not directly comparable to a personal markdown repo. The transferable idea is narrower:

> taxonomy should be treated as a revisable hypothesis about navigation, not an immutable folder design.

This supports our decision to avoid locking the initial hierarchy too early.

### 8.4 What may not transfer

A personal wiki probably does not need path-indexed KV storage or concurrency protocols at small scale. Copying production database architecture into our MVP would violate our own evidence-first principle.

The relevant experiment is schema-evolution behavior, not the specific storage engine. Issue #5 records this candidate.

---

## 9. WikiLoop — evaluate edits by downstream utility

Primary paper: https://arxiv.org/abs/2607.26604

### 9.1 Main contribution

WikiLoop couples wiki construction and navigation. A Builder proposes edits; a Navigator evaluates the effect of those edits on downstream answering.

Two ideas are especially important:

1. **sufficiency before efficiency** — retrieval-cost penalties apply only after enough evidence has been gathered,
2. **guard against regressions** — edits are discouraged when they improve a target query while degrading unrelated queries.

### 9.2 Why this changes our evaluation model

Most personal wiki workflows judge a page locally:

- is it well written?
- is the frontmatter valid?
- are the citations present?

WikiLoop suggests a stronger criterion:

> Did this edit make the knowledge system more useful without breaking other things?

That turns wiki maintenance into something closer to software regression testing.

### 9.3 Transfer caveat

WikiLoop learns policies under benchmark conditions; we should not assume we need reinforcement learning or learned builders. The transferable principle is **downstream regression testing of knowledge edits**.

Issue #4 records an experiment candidate comparing local-quality acceptance against downstream-utility + regression-suite acceptance.

---

## 10. Beyond Memory — preserve failure paths

Primary paper: https://arxiv.org/abs/2607.24759

### 10.1 Main contribution

This work treats llm-wiki as a substrate for collaborative knowledge work and emphasizes preservation of dead ends, reversed claims, and reasoning history. Its template uses append-only conventions to retain failure paths.

### 10.2 Case-study signal

The paper reports a two-author project's retroactive audit where initially claimed evidence coverage was revised downward, then improved after a fix, while preserving the failed path. This is relevant not because the exact numbers generalize, but because it demonstrates a useful property: **the artifact can preserve evidence that earlier conclusions were wrong.**

### 10.3 Implication

For our project, "clean current truth" and "recoverable epistemic history" may need separate surfaces. A wiki page optimized for today's answer need not expose every abandoned path inline, but the system should probably be able to reconstruct why a belief/decision changed.

This supports investigating archive/supersession/tombstone models rather than hard deletion as the default lifecycle mechanism.

---

## 11. Cross-system comparison

| System | Ingest | Representation | Organization | Update / contradiction | Provenance | Retrieval | Evaluation | Human role | Key failure insight |
|---|---|---|---|---|---|---|---|---|---|
| Karpathy idea | agent reads curated source | interlinked Markdown synthesis | schema-defined, flexible | revise and flag contradictions; underspecified semantics | raw is source of truth | index first; search later | informal lint | source curation + guided ingest | maintenance assumptions largely untested |
| Astro-Han | triage: new/update/disputed/no-material | topic articles | shallow topics + index/log | preserve outdated/disputed history | exact-fact grounding to immutable raw | index + full-text | deterministic + semantic lint | agent operates, user decides ambiguous/destructive cases | unsupported exact facts and silent history rewrite |
| Nihar | structured 3-pass pipeline | sources/entities/concepts/synthesis | typed pages | merge related pages | source page records touched pages | BM25 + vector + rerank; wiki/raw/hybrid | lint + optional contradiction check | confirm extracted filing by default | page explosion, ingest cost, ontology assumptions |
| LLM-Wiki paper | compile documents | linked structured wiki | agent-navigable links | Error Book self-correction | benchmark-oriented source grounding | search/read/follow links | multi-hop QA/AuthTrace | mostly system-level benchmark | flat retrieval interface limits agent reasoning |
| WiCER | compile then probe/refine | compiled wiki abstraction | not central | recompile to preserve diagnosed missing facts | source facts used in diagnosis | full-context/wiki QA | RepLiQA diagnostic probes | automated experimental loop | **compilation silently drops critical facts** |
| WikiKV | offline hierarchical curation | hierarchical wiki nodes | induced and evolving schema | continuous evolution operators | metadata/storage dependent | budgeted hierarchical navigation | deployment + AuthTrace | production system | fixed schema does not fit evolving corpus |
| WikiLoop | builder proposes edits | persistent linked wiki | inherited wiki structure | accept edits by downstream utility | benchmark evidence | Navigator agent | target gain + regression guard | learned builder/navigator | locally good edit can harm unrelated queries |
| Beyond Memory | collaborative accumulation | append-oriented wiki | template-defined | preserve reversals/failures | artifact history | agent-aware wiki | reported case studies/audits | humans + agents | polished final state can erase useful failure history |

---

## 12. Recurring patterns

### 12.1 Raw/derived separation is nearly universal

Systems repeatedly distinguish authoritative source material from LLM-derived synthesis. This convergence is strong enough to treat the idea as a leading hypothesis, but not yet an adopted detailed provenance policy.

### 12.2 "Compile once" is misleading

Mature designs are not actually one-shot compilation. They add:

- cascade updates,
- lint,
- error books,
- probe-driven refinement,
- schema evolution,
- downstream regression signals.

A more accurate mental model is **continuous incremental compilation with verification and repair**.

### 12.3 Maintenance requires multiple authority levels

Implementations separate low-risk deterministic actions from semantic edits and destructive actions. This aligns with our reserved automation-boundary research axis.

### 12.4 Retrieval is hybridizing again

Even systems inspired by "anti-RAG" ideas often reintroduce lexical/vector search or raw-source fallback. The durable distinction is therefore not "RAG vs no RAG". It is more usefully framed as:

- raw retrieval only,
- compiled knowledge only,
- or a layered system where compiled structure guides access to raw evidence.

### 12.5 Query failures can be maintenance signals

LLM-Wiki Error Book, WiCER diagnostic probes, and WikiLoop downstream feedback all point toward the same deeper principle:

> use failures of the knowledge consumer to improve the knowledge producer.

This deserves dedicated experimentation.

---

## 13. Major unresolved conflicts

### 13.1 Append-only history vs concise current truth

- *Beyond Memory* values preserving failed paths.
- Personal retrieval benefits from low-noise current representations.

We likely need separate current-state and historical/audit surfaces rather than choosing one globally.

### 13.2 Aggressive compilation vs fact preservation

- Compiled synthesis reduces repeated reasoning and context cost.
- WiCER shows compression can destroy future answerability.

The optimal compression level is workload-dependent and must be experimentally measured.

### 13.3 Fixed typed schema vs emergent structure

- Typed entity/concept pages create predictability.
- WikiKV motivates schema evolution.
- Personal PKM may contain concepts that do not fit stable ontology boundaries.

We should not assume a single universal page type model.

### 13.4 Autonomous maintenance vs human trust

- Automation is the value proposition.
- Interactive ingest and risk-tiered lint show that unlimited autonomy is not obviously desirable.

This remains a first-class future research axis.

---

## 14. Experiment implications

### Existing experiments strengthened

- **E001 knowledge-unit comparison** — strengthened by typed-page vs topic-page divergence and WiCER omission risk.
- **E003 temporal semantics** — strengthened by Astro-Han's explicit outdated/disputed handling and failure-path preservation.
- **E004 provenance granularity** — strengthened by executable grounding invariants.
- **E005 split/merge** — strengthened by WikiKV schema evolution.
- **E006 retrieval escalation** — strengthened by Wiki/Raw/Hybrid query scopes.
- **E007 long-horizon contamination** — still critical; none of the reviewed work fully answers personal multi-month recursive contamination.
- **E008 error book** — directly supported as a pattern, but needs recurrence/overgeneralization tests.
- **E009 human review risk tiers** — practical implementations already use interactive confirmation and differentiated lint authority.
- **E010 IDE usability** — remains intentionally later-stage.

### New explicit experiment candidates

- Issue #3 — detect and repair compilation loss using diagnostic probes.
- Issue #4 — accept wiki edits based on downstream utility + regression risk.
- Issue #5 — schema evolution under split/merge pressure.

---

## 15. Initial conclusions — hypotheses only

1. **The biggest danger is not only hallucination; omission during synthesis may be equally dangerous.**
2. **A wiki needs tests, not only lint.** Some tests should ask whether knowledge remains answerable after edits.
3. **Raw source access should remain available even if the wiki is the normal query surface.**
4. **History preservation and current-answer quality should probably be separate concerns.**
5. **Taxonomy is likely an evolving artifact, not a one-time folder decision.**
6. **The correct automation target is probably not "maximum autonomy" but "maximum low-risk leverage under observable, reversible edits."**
7. **The system should learn from retrieval/query failures, not just from ingest-time rules.**

None of these are adopted architecture decisions. They are inputs to the next research and experiment phases.

## 16. Sources

### Primary design / implementation

- Andrej Karpathy, `llm-wiki.md`: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Astro-Han, `karpathy-llm-wiki`: https://github.com/Astro-Han/karpathy-llm-wiki
- Nihar Shrotri, `llm-wiki`: https://github.com/NiharShrotri/llm-wiki

### Primary research

- Ming et al., *Retrieval as Reasoning: Self-Evolving Agent-Native Retrieval via LLM-Wiki*: https://arxiv.org/abs/2605.25480
- Huerta, *WiCER: Wiki-memory Compile, Evaluate, Refine*: https://arxiv.org/abs/2605.07068
- Li et al., *WikiKV: Schema-Evolving Path-Indexed Storage for Hierarchical Knowledge Navigation*: https://arxiv.org/abs/2606.14275
- Ming et al., *WikiLoop: Jointly Learning to Build and Navigate Agent-Native Wikis with Downstream Feedback*: https://arxiv.org/abs/2607.26604
- Moreira & Sweet, *Beyond Memory: A Templated Substrate for Heterogeneous Collaborative Knowledge Work with LLM Agents*: https://arxiv.org/abs/2607.24759
