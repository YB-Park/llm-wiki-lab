# Retrieval Architecture and Baselines — Research Batch F

Date: 2026-08-12
Status: research note, not policy
Related: Issue #12

## 1. Purpose

A personal LLM Wiki is only valuable if its maintained structure improves actual retrieval enough to justify the cost and risk of maintaining that structure.

This batch asks a deliberately adversarial question:

> When does a compiled wiki beat simpler alternatives such as filesystem search, lexical/vector retrieval, or simply giving a strong model more raw context?

The answer appears strongly query-dependent.

---

## 2. Query classes should be first-class in evaluation

The reviewed retrieval systems repeatedly distinguish qualitatively different information needs.

### Q1 — local / exact lookup

Examples:

- What version introduced this feature?
- What number/date did the source state?
- Where did I write this decision?

These often resemble source text closely. Lexical/vector retrieval and direct evidence access are naturally competitive.

### Q2 — global / sensemaking

Examples:

- What are the main themes across everything I read about agent memory?
- What recurring failure modes appear across these papers?

Microsoft GraphRAG was designed specifically because ordinary local RAG struggles with corpus-wide questions. It precomputes entity/relationship structure and community summaries, then aggregates relevant community-level responses.

### Q3 — relational / multi-hop

Examples:

- Which architecture decision depends on evidence that was later superseded?
- What links concept A to project B through source C?

HippoRAG and graph-based methods target associative/multi-hop retrieval where isolated nearest-neighbor chunks can miss useful paths.

### Q4 — temporal / historical

Examples:

- What did I believe in March, and why did it change?
- Which claim was current before this correction?

This requires temporal semantics, not merely similarity.

### Q5 — provenance / source ownership

Examples:

- Which primary source supports this exact claim?
- Did source A actually say this, or was it synthesized from B and C?

This often requires descending from synthesis to raw evidence.

### Q6 — exploratory navigation

Examples:

- Show me related concepts I may have forgotten.
- What neighboring topic should I inspect next?

Links, hierarchy, aliases, and semantic relations may add value beyond pure answer retrieval.

A single aggregate QA score will hide these differences. E006 should report per-query-class performance.

---

## 3. GraphRAG — expensive structure can help broad corpus questions

Primary source:

- Edge et al., *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*: https://www.microsoft.com/en-us/research/publication/from-local-to-global-a-graph-rag-approach-to-query-focused-summarization/

GraphRAG builds an entity knowledge graph and hierarchical community summaries from source documents. For global sensemaking questions over roughly million-token corpora, the authors report improved comprehensiveness and diversity relative to a conventional RAG baseline.

### Transferable lesson

Precomputed abstraction can make broad questions easier because the retrieval system has an explicit representation of corpus breadth.

This supports the LLM Wiki intuition that durable synthesis can avoid rediscovering the whole corpus every time.

### Major warning

GraphRAG's index is itself a compiled, LLM-generated knowledge representation.

Therefore all of our Batch A risks apply to the index too:

- omission during extraction/summarization,
- stale summaries after source updates,
- wrong entity resolution,
- source-attribution drift,
- expensive refresh.

A graph index should not receive a special exemption from wiki verification merely because it is called a retrieval index.

---

## 4. Local vs global is not a binary architecture choice

Microsoft's DRIFT work combines global community context with local follow-up reasoning. This demonstrates an important design principle:

> query strategies can be composed and escalated rather than selecting one retrieval architecture for every question.

For our wiki, a possible experimental escalation path is:

```text
cheap/local search
      |
      | insufficient breadth?
      v
summary / hierarchy navigation
      |
      | relational ambiguity?
      v
agentic / graph traversal
      |
      | exact/high-risk evidence?
      v
raw source verification
```

This is only a test model, not a chosen production router.

---

## 5. Dynamic community selection — prune before expensive synthesis

Microsoft's dynamic GraphRAG global search starts high in the community hierarchy, uses a cheaper relevance-rating step to prune irrelevant subtrees, and sends only relevant reports into expensive answer generation.

The reported AP News experiment found similar quality with substantially lower token cost than static global search at one tested level, and deeper dynamic selection sometimes improved response detail.

### Transferable principle

**Cheap relevance decisions can precede expensive generative work.**

This generalizes well beyond GraphRAG:

- filesystem/metadata filter before semantic search,
- lexical candidate retrieval before LLM rerank,
- cheap model/router before expensive model,
- dirty/dependency set before reconsolidation,
- query-risk classification before source verification.

It strongly supports our deterministic-first automation philosophy.

---

## 6. LazyGraphRAG — precompute only when reuse justifies it

Primary source:

- Microsoft Research, *LazyGraphRAG: Setting a new standard for quality and cost*: https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/

LazyGraphRAG deliberately avoids LLM-generated entity/community summaries at indexing time and defers more LLM use until query time. Microsoft reports strong cost-quality results across local and global synthetic queries on an AP News corpus, with indexing cost comparable to vector RAG and far below full GraphRAG in their setup.

### Why this matters to our personal wiki

This is an important counterweight to the "compile everything in advance" instinct.

If a corpus changes frequently or many topics are never queried, extensive precomputation can be wasted work. A lazy approach pays semantic cost only when demand appears.

This yields a central experiment question:

> Which knowledge deserves durable precomputation because it is repeatedly useful, and which knowledge should remain cheap raw/searchable evidence until demand proves otherwise?

That connects retrieval architecture directly to selective maintenance (Issue #8).

---

## 7. RAPTOR — multiple abstraction levels can coexist

Primary source:

- Sarthi et al., *RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval*: https://arxiv.org/abs/2401.18059

RAPTOR recursively clusters and summarizes text into a tree, then retrieves information from different abstraction levels. Its experiments report gains on tasks requiring holistic or multi-step understanding.

### Transferable lesson

A knowledge system need not choose between tiny chunks and giant summaries. It can expose multiple abstraction levels.

This supports a layered wiki model:

```text
raw detail
  -> local/topic synthesis
      -> broader overview/index
```

### But the WiCER warning remains

Recursive summaries are lossy compiled artifacts. More abstraction levels may improve navigation while creating more surfaces that can omit or stale.

Therefore hierarchical summaries must be evaluated for:

- coverage loss,
- duplication drift,
- refresh cost,
- source fallback behavior.

---

## 8. Dynamic hierarchical indexes add maintenance complexity

Research extending recursive-abstractive retrieval to dynamic datasets explicitly identifies a problem we already expect: adding/removing documents makes hierarchical clustering/summaries expensive to maintain.

This supports a general rule for our experiments:

> evaluate retrieval structures under repeated updates, not only a frozen corpus.

A structure that wins on a static benchmark may be unacceptable for a personal knowledge base that changes every day.

---

## 9. HippoRAG — relational retrieval can help multi-hop questions

Primary source:

- Gutiérrez et al., *HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models*: https://arxiv.org/abs/2405.14831

HippoRAG combines knowledge-graph structure with Personalized PageRank and reports strong multi-hop QA performance, including lower cost than some iterative retrieval approaches under its experiments.

HippoRAG 2 later emphasizes a crucial trade-off: graph-oriented memory can improve associative/sensemaking behavior while needing to remain competitive with standard RAG on basic factual retrieval.

### Project implication

If we add links/graphs, the benchmark cannot contain only relationship-heavy questions. It must include exact/simple factual queries so graph sophistication does not silently degrade the common case.

---

## 10. LightRAG — dual-level retrieval and incremental update

Primary source:

- Guo et al., *LightRAG: Simple and Fast Retrieval-Augmented Generation*: https://arxiv.org/abs/2410.05779

LightRAG combines graph structure with vector representations and distinguishes lower-level and higher-level retrieval. It also explicitly addresses incremental updates.

For us, the important signal is convergence:

- exact/local evidence benefits from fine-grained retrieval,
- broader conceptual questions may benefit from higher-level structure,
- dynamic corpora require update-aware indexing.

Again, this does not imply we need a graph database.

---

## 11. The index itself is part of the knowledge lifecycle

A recurring architectural mistake is to treat retrieval infrastructure as neutral plumbing.

But an LLM-generated index can contain semantic claims:

```text
entity aliases
relationships
cluster membership
community summaries
hierarchy
query-expanded concepts
```

These can be wrong or stale.

Therefore we should distinguish:

### Deterministic/low-semantic indexes

- filenames,
- Git metadata,
- exact tokens,
- BM25/FTS,
- source IDs,
- explicit links.

### Derived semantic indexes

- embeddings,
- entity extraction,
- inferred links,
- graph communities,
- LLM summaries,
- generated aliases.

The second group should have lifecycle/version/refresh semantics proportional to its risk and cost.

---

## 12. Baselines the LLM Wiki must beat

The first controlled experiments should not compare only sophisticated wiki variants.

### B0 — raw filesystem + grep/search

No semantic index. Exact filenames/text search and direct model reading.

### B1 — raw + lexical retrieval

BM25/FTS/ripgrep-like candidate retrieval, then LLM answer.

### B2 — raw + vector retrieval

Conventional embedding-based RAG.

### B3 — raw + larger-context retrieval

Retrieve substantially more raw text or, where feasible, provide the whole controlled corpus to a long-context model.

### B4 — compiled topic wiki + simple index

Closest to Karpathy's minimal pattern.

### B5 — layered wiki + raw fallback

Overview/topic/detail with source verification on demand.

### Optional later baselines

Only if simpler variants expose a real deficiency:

- hierarchical summary tree,
- graph/relational retrieval,
- fully agentic iterative retrieval.

This ordering protects us from solving problems we do not yet have.

---

## 13. Cost-quality should be measured as a frontier

A retrieval system can usually buy more quality with more tokens, model calls, and preprocessing.

Therefore comparing only the best-quality configuration is misleading.

For each method we should record something like:

```text
quality at low budget
quality at medium budget
quality at high budget
index/build cost
maintenance cost after updates
query cost
human review/repair cost
```

The useful result is a **cost-quality frontier**, not a single winner.

For personal use, an architecture that is 2% more accurate but requires 20x maintenance may be inferior.

---

## 14. Query router as a hypothesis

A future personal wiki may classify a query before retrieval.

Possible classes and default strategies to test:

| Query need | Cheap first strategy | Escalation |
|---|---|---|
| exact/date/number | lexical/raw | source verification |
| known topic explanation | topic wiki | detail/raw |
| global themes | overview/hierarchy | broader map-reduce |
| relational/multi-hop | linked/graph candidates | agentic traversal |
| temporal/history | status/timeline metadata | raw/version history |
| provenance | source map | exact source/span |
| exploratory | links/related topics | semantic/graph expansion |

A router can also be wrong, so router accuracy/cost must be included in evaluation.

---

## 15. Retrieval and maintenance are coupled

A query failure may mean at least four different things:

1. knowledge was never ingested,
2. knowledge exists in raw evidence but retrieval failed,
3. derived wiki omitted it during compilation,
4. derived/index state is stale or structurally misleading.

The repair action should depend on the diagnosis.

A dangerous system would respond to every failed query by rewriting the wiki.

A better experimental pipeline is:

```text
query failure
   -> diagnose missing vs retrieval vs compilation vs stale
   -> record failure
   -> propose minimal repair
   -> regression test
```

This connects E006 with E008 and Issue #3/#4.

---

## 16. Representation × retrieval matrix

Batch D argued that note structure and retrieval cannot be chosen independently. Batch F strengthens that conclusion.

At minimum, compare selected combinations of:

### Representations

- raw only,
- source summaries,
- topic documents,
- layered parent/child synthesis,
- more atomic linked units.

### Retrieval

- lexical,
- vector,
- index/hierarchy navigation,
- mixed escalation,
- agentic traversal where justified.

The objective is not exhaustive Cartesian testing. It is to avoid attributing a retrieval mismatch to a representation failure.

---

## 17. Strongest conclusions from Batch F — hypotheses only

1. **Retrieval is query-class dependent; one universal expensive pipeline is unlikely to be optimal.**
2. **Simple lexical/vector/raw-context baselines must remain serious competitors.**
3. **Precomputed synthesis is most defensible when reuse/global sensemaking value exceeds indexing and refresh cost.**
4. **Lazy/deferred LLM use is a strong candidate for frequently changing or rarely queried knowledge.**
5. **Cheap routing/pruning before expensive generation should be tested broadly.**
6. **Hierarchical summaries can improve abstraction navigation but inherit all compilation-loss/staleness risks.**
7. **Graph structure may help associative/multi-hop tasks but must not degrade factual/local retrieval.**
8. **Retrieval indexes are part of the maintained knowledge system, not neutral infrastructure.**
9. **The evaluation target is a cost-quality-maintenance frontier across query classes.**
10. **Query failure requires diagnosis before maintenance.**

None of these are adopted architecture decisions.

---

## 18. Phase 1 baseline suite

The first experiment suite should include these mandatory baselines wherever technically feasible:

```text
B0 raw + deterministic filesystem/text search
B1 raw + lexical retrieval
B2 raw + semantic/vector retrieval
B3 raw + large-context baseline
B4 minimal compiled topic wiki
B5 layered compiled wiki + raw fallback
```

Graph/hierarchical/agentic approaches should be added only when the tested corpus/query class gives them a plausible advantage.

This baseline suite becomes the defense against architecture enthusiasm.

## 19. Sources

- Edge et al., *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*: https://www.microsoft.com/en-us/research/publication/from-local-to-global-a-graph-rag-approach-to-query-focused-summarization/
- Microsoft Research, *Introducing DRIFT Search*: https://www.microsoft.com/en-us/research/blog/introducing-drift-search-combining-global-and-local-search-methods-to-improve-quality-and-efficiency/
- Microsoft Research, *GraphRAG: Improving global search via dynamic community selection*: https://www.microsoft.com/en-us/research/blog/graphrag-improving-global-search-via-dynamic-community-selection/
- Microsoft Research, *LazyGraphRAG: Setting a new standard for quality and cost*: https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/
- Sarthi et al., *RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval*: https://arxiv.org/abs/2401.18059
- Chucri et al., *Recursive Abstractive Processing for Retrieval in Dynamic Datasets*: https://arxiv.org/abs/2410.01736
- Gutiérrez et al., *HippoRAG*: https://arxiv.org/abs/2405.14831
- Gutiérrez et al., *From RAG to Memory / HippoRAG 2*: https://arxiv.org/abs/2502.14802
- Guo et al., *LightRAG*: https://arxiv.org/abs/2410.05779
