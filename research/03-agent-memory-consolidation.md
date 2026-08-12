# Agent Memory and Consolidation — Research Batch B

Date: 2026-08-12
Status: research note, not policy
Related: Issue #6

## 1. Purpose

LLM Wiki and long-term agent memory are adjacent problems with an important shared core:

> new observations arrive over time; the system must decide what to preserve, how to transform it into durable state, how to revise that state without losing useful information, and how to retrieve the right level of detail later.

This batch focuses on mechanisms that may transfer to a personal LLM Wiki. Benchmark wins are not treated as direct evidence for our workload. Dialogue memories, execution memories, and personal research knowledge differ materially.

Primary systems examined:

- Infini Memory
- LeanMem
- TRUSTMEM
- A-MEM
- Zep / Graphiti
- Mem0
- MemGPT / Letta
- EvoMemBench

## 2. Infini Memory — topic documents as maintainable memory

Primary source: https://arxiv.org/abs/2606.10677

### Core idea

Infini Memory stores long-term state as topic-structured text documents rather than isolated memory fragments. Each topic document aggregates related evidence, metadata, and changing facts.

New observations are **not necessarily merged immediately**. They first enter a buffer and are periodically consolidated into coherent topic documents. Retrieval is agentic: the model iteratively inspects memory through tool calls rather than relying on one-shot top-k retrieval.

### Why this maps closely to LLM Wiki

This is probably the closest agent-memory analogue to the wiki model:

```text
observations -> staging buffer -> topic documents -> iterative retrieval
```

The key contribution for us is not merely "topic documents work." It is the separation between:

- observation capture,
- durable consolidation,
- retrieval-time evidence inspection.

That supports E002: immediate rewrite and staged consolidation must be compared rather than assumed.

### Evidence

The paper reports 64.7% overall on MemoryAgentBench, with ablations indicating topic-structured maintenance and iterative evidence inspection contribute complementary benefits.

### Transfer caveat

MemoryAgentBench is not a multi-year personal knowledge corpus. We should transfer the mechanism as a hypothesis, not the reported score or threshold choices.

---

## 3. LeanMem — heterogeneous information deserves heterogeneous memory policy

Primary source: https://arxiv.org/abs/2608.03463

### Core critique

LeanMem argues that treating all historical content through one summarization/retrieval pipeline creates two opposite failures:

- too much token/model cost when everything is repeatedly processed,
- irreversible evidence loss when everything is compressed uniformly.

It routes informative content according to three properties:

- compressibility,
- temporal dynamics,
- fidelity requirements.

### Memory types

LeanMem uses different durable representations:

- **profile memory** — stable, compact information,
- **event memory** — temporally evolving information,
- **record memory** — detail-sensitive, source-grounded information retaining a path to original evidence.

Critically, only evolving event memories receive recurring maintenance. Stable profiles and immutable records avoid redundant consolidation.

### Transferable principle

This is a major challenge to a naive wiki architecture:

> "one page model + one maintenance policy for everything" may be the wrong abstraction.

A personal wiki contains heterogeneous material:

- stable concepts,
- changing software/product facts,
- personal preferences,
- decisions,
- exact research records,
- source summaries,
- hypotheses.

These may require different compression, update, provenance, and review policies.

### Retrieval

LeanMem also adapts retrieval to the query's evidence needs and expands source-grounded records when finer detail is required. This supports layered retrieval rather than always loading the most detailed representation.

### Cost relevance

The paper explicitly optimizes both construction and inference cost and reports better or competitive accuracy with low/near-low construction cost, inference tokens, and latency on LoCoMo and LongMemEval-S under the tested model settings.

For our project the important lesson is methodological: **maintenance selectivity itself is a cost-control mechanism**. We should not only optimize prompts or model size; we should avoid invoking semantic maintenance on knowledge that has no reason to change.

### Risk

Typed routing creates a new classification burden. If the system misclassifies a changing fact as stable profile or a detail-critical record as compressible summary, the optimization can produce silent errors. The routing policy therefore needs its own evaluation.

---

## 4. TRUSTMEM — verify the transition, not only the final document

Primary source: https://arxiv.org/abs/2606.25161

### Problem framing

TRUSTMEM starts from a failure mode directly relevant to us: memory agents generate write/revise/delete actions, and errors in those updates become **persistent system-state failures**.

It distinguishes three transition-level failure dimensions:

1. **coverage** — did the update omit important new information?
2. **preservation** — did the update corrupt or destroy useful existing memory?
3. **faithfulness** — did the update introduce unsupported content?

A Memory Transition Verifier evaluates candidate memory updates along these dimensions.

### Why this matters more than ordinary lint

A final wiki page can look valid while the transition was bad.

Example:

```text
before: A, B, C
new evidence: D
result: A, C, D
```

The resulting text may be internally coherent and perfectly cited, but `B` was accidentally lost. Final-state validation alone may miss this.

The correct object of evaluation may therefore be:

```text
(previous state, new evidence, proposed next state)
```

rather than only `proposed next state`.

### Evidence

The paper reports improvements across MemoryAgentBench, HaluMem, and Mem-alpha validation, including transition-level reductions in omission, corruption, and hallucination against the strongest tested baseline for each error type.

### Mapping to our failure taxonomy

The correspondence is striking:

- coverage failure ~ F2 omission / compilation loss,
- preservation failure ~ F5 maintenance-induced regression (and some temporal corruption),
- faithfulness failure ~ F1 fabrication.

This suggests that our knowledge compiler should eventually test **transition invariants** in addition to static document invariants.

### Transfer caveat

TRUSTMEM trains a verifier/update policy; we do not need to assume RL or a learned verifier. The transferable concept is the three-way transition test.

---

## 5. A-MEM — memory as an evolving linked network

Primary source: https://arxiv.org/abs/2502.12110

### Core idea

A-MEM draws inspiration from Zettelkasten. New memories receive structured attributes and links to semantically related historical memories; adding a memory can also trigger updates to existing memory representations.

### Relevance

This supports two LLM Wiki ideas:

- links can be generated/evolved rather than fixed at ingest,
- adding knowledge may change how existing knowledge is described or connected.

### Important caution

Dynamic linking and evolution create write amplification. Every new item can trigger additional LLM interpretation of old state. This is exactly where a personal wiki can spend large token budgets maintaining structure rather than providing value.

The lesson is therefore not "use Zettelkasten links automatically." It is that **relationship maintenance has both retrieval value and lifecycle cost**, which should be measured.

---

## 6. Zep / Graphiti — time is a memory primitive

Primary source: https://arxiv.org/abs/2501.13956

### Core idea

Zep/Graphiti represents memory as a temporal knowledge graph that continuously synthesizes conversational and structured data while retaining historical relationships.

### Relevance

This is important evidence that agent-memory research treats temporal change as a first-class architectural problem rather than a metadata afterthought.

It strengthens the motivation for Q-UPD-002 and E003, especially for:

- changed preferences,
- changing entity attributes,
- sequential facts,
- historical queries.

### Scope boundary

Whether a graph is justified for our personal wiki is a separate question. Batch C should inspect its temporal/bitemporal semantics in detail. The takeaway here is only that **time-aware update semantics are already a central memory-system problem**.

---

## 7. Mem0 — explicit extract/consolidate/retrieve pipeline

Primary source: https://arxiv.org/abs/2504.19413

Mem0 is useful as an example of a production-oriented memory pipeline that extracts salient information from interactions, consolidates it into persistent memory, and retrieves relevant memories later. Its graph variant adds relational structure.

For us, the main conceptual lesson is pipeline separation:

```text
conversation/source
    -> candidate memory extraction
    -> consolidation/update
    -> persistent store
    -> query-time retrieval
```

This reinforces the idea that "capture" and "promote into canonical knowledge" do not need to be the same action.

Benchmark/token/latency results from conversational personalization should not be transferred directly to personal research knowledge.

---

## 8. MemGPT / Letta — context is a hierarchy, not one bucket

Primary source: https://arxiv.org/abs/2310.08560

MemGPT models context management after virtual memory: limited in-context memory is backed by larger external memory tiers, with the agent explicitly moving information between them.

For LLM Wiki, the relevant insight is architectural rather than representational:

> not all persistent knowledge needs to be loaded into every model call.

This is obvious in principle, but important for our VS Code/Copilot constraint. The wiki should help construct small, task-relevant context rather than becoming a reason to attach the whole knowledge base to every interaction.

---

## 9. EvoMemBench — strong warning against architecture monoculture

Primary source: https://arxiv.org/abs/2605.18421

### Benchmark framing

EvoMemBench compares 15 representative memory methods with strong long-context baselines under a standardized protocol across:

- in-episode vs cross-episode memory,
- knowledge-oriented vs execution-oriented content.

### Main result relevant to us

The paper concludes that current memory systems are far from a general solution:

- long-context baselines remain highly competitive,
- memory helps most when current context is insufficient or tasks are difficult,
- no single memory form wins consistently across all settings,
- retrieval-oriented memory remains strong for knowledge tasks,
- procedural/long-term experience can help execution tasks when memories match task structure.

### Project implication

This is a strong reason not to evaluate our Wiki only against other Wiki variants.

A meaningful baseline must include something like:

```text
raw sources + good search + large context
```

If a sophisticated wiki requires substantial maintenance but does not beat a simple search/context baseline on our real workload, its architecture is not justified.

This also changes our cost question: the competitor is not "no memory"; it is an increasingly capable long-context model with filesystem/search access.

---

## 10. Cross-system comparison

| System | Write unit | Consolidation | What evolves? | Fidelity strategy | Retrieval | Cost-control mechanism | Main lesson for Wiki |
|---|---|---|---|---|---|---|---|
| Infini Memory | topic observation/document | buffered periodic consolidation | topic docs | metadata + coherent evidence | iterative agentic read | defer/reduce rewrites | separate capture from consolidation |
| LeanMem | profile/event/record | selective | mainly event memory | records retain source path/detail | adaptive type/budget selection | do not maintain stable info repeatedly | heterogeneous info needs heterogeneous policy |
| TRUSTMEM | memory transition | candidate update verification | any updated state | coverage/preservation/faithfulness | orthogonal | prevent expensive persistent errors | test before→after transitions |
| A-MEM | linked note/memory | evolution on new links | notes + relations | semantic attributes | linked retrieval | not primary focus | relationships can evolve, but cause write amplification |
| Zep/Graphiti | temporal graph facts/events | continuous graph update | temporal relations | history retained | graph retrieval | not primary focus | time/change need explicit semantics |
| Mem0 | extracted salient memories | explicit consolidation | persistent memories/graph | extraction rules | semantic/graph retrieval | selective memory vs full history | capture and promotion are separate stages |
| MemGPT | memory tiers/pages | explicit memory movement | external/context state | backing store | agent-managed paging | small active context | persistent state should not flood every prompt |
| EvoMemBench | benchmark abstraction | varies by system | varies | benchmarked | varies | compares against long context | no universal memory architecture; simple baseline matters |

---

## 11. Strongest convergence after Batch B

### 11.1 Capture is not consolidation

Several systems separate incoming observations from durable synthesized memory. This weakens the naive rule "every source ingest rewrites canonical wiki pages immediately."

### 11.2 Maintenance should be selective

LeanMem makes the clearest case: stable and source-grounded information can avoid recurring semantic rewriting, while dynamic event-like knowledge receives evolution work.

This may be central to both reliability and token economics.

### 11.3 Knowledge update is a state transition

TRUSTMEM gives us a better abstraction for edits:

```text
old state + new evidence -> proposed state
```

The proposed state should preserve relevant old knowledge, cover important new knowledge, and remain faithful to evidence.

### 11.4 Exact/high-fidelity evidence should resist compression

LeanMem record memory and Batch A's WiCER result converge on the same point from different directions: some information should stay cheaply addressable in source-grounded form rather than being repeatedly summarized.

### 11.5 Query need should determine evidence depth

MemGPT, LeanMem, Infini Memory, and layered Wiki implementations all support progressive/context-sensitive access rather than uniform retrieval depth.

### 11.6 Elaborate memory must beat a simpler baseline

EvoMemBench makes this non-negotiable. "Raw corpus + search + long context" should remain in our experimental matrix.

---

## 12. A new architecture hypothesis: maintenance classes, not just page types

The most important new hypothesis from this batch is that **maintenance policy may be more fundamental than document taxonomy**.

Instead of starting with:

```text
concept/
people/
projects/
papers/
```

we may eventually classify knowledge along dimensions such as:

```text
stability:      stable <-> rapidly changing
fidelity need:  compressible <-> source-exact
authority:      raw <-> derived <-> personal judgment
lifecycle:      append-only <-> superseding
impact:         low <-> high consequence
```

Those attributes could determine:

- whether LLM consolidation is allowed,
- how often it runs,
- how much provenance is required,
- whether source fallback is mandatory,
- whether human review is required,
- whether old state can be replaced or only superseded.

This is a hypothesis, not a schema proposal. We should test whether such maintenance classes improve reliability enough to justify added classification complexity.

---

## 13. Experiment implications

### E001 — knowledge-unit comparison

Add a heterogeneous-policy variant. Compare not only different note units but:

- uniform representation/maintenance,
- mixed representations or metadata-driven maintenance classes.

### E002 — immediate vs staged consolidation

Strengthened substantially by Infini Memory. Add selective consolidation as another axis:

- all buffered knowledge consolidated,
- only knowledge classified as dynamic/reconsolidation-worthy.

### E003 — temporal semantics

Strengthened by LeanMem event memory and Zep/Graphiti. Batch C should define the exact temporal models to test.

### E004 — provenance

High-fidelity record/source pointers should be evaluated alongside claim-level citation. A source pointer can preserve detail cheaply but may shift work to retrieval time.

### E006 — retrieval escalation

Add query-dependent evidence budgets/types and compare against raw-search + long-context baseline.

### E007 — long-horizon contamination

Add maintenance selectivity as a variable: does repeatedly rewriting only dynamic knowledge reduce error amplification?

### E009 — human review risk tiers

Risk may depend not only on operation (`edit`, `delete`) but on memory class: replacing a volatile event summary differs from rewriting a high-fidelity decision record.

---

## 14. New experiment candidates

### Candidate A — Memory transition verification

Compare wiki update validation strategies:

1. final-state lint only,
2. final-state grounding only,
3. transition check for coverage + preservation + faithfulness,
4. transition check + regression queries.

Stress with deliberate omission, accidental deletion, hallucinated additions, stale temporal updates, and legitimate removals.

### Candidate B — Uniform vs selective maintenance

Compare:

1. every relevant source triggers canonical rewrite,
2. buffered periodic consolidation of all knowledge,
3. knowledge-class-aware selective consolidation,
4. mostly raw/search baseline with minimal derived maintenance.

Measure answer quality, omission, stale state, tokens/model calls, human review, and repair cost across long update sequences.

These candidates directly address both correctness and the user's IDE/token-cost concerns.

---

## 15. Questions this batch does NOT answer

- What exact maintenance classes should exist?
- Can an LLM classify those classes reliably enough?
- Should source material be copied locally, versioned, or referenced externally?
- What exact temporal model should be used?
- How should hard deletion/privacy erasure interact with historical auditability?
- At what corpus size does graph/vector infrastructure pay for itself?
- How much verification cost is justified for ordinary personal notes?

Those remain open.

---

## 16. Next research dependency

Batch C should now focus on **temporal knowledge, provenance, event sourcing, and deletion semantics**.

The reason is structural: Batch B suggests different knowledge evolves differently, but we cannot design selective maintenance until we understand what "changed," "superseded," "historical," "corrected," and "deleted" should mean.

## 17. Primary sources

- Ji et al., *Infini Memory: Maintainable Topic Documents for Long-Term LLM Agent Memory*: https://arxiv.org/abs/2606.10677
- Liao et al., *LeanMem: Simple and Efficient Long-Term Memory for LLM Agents*: https://arxiv.org/abs/2608.03463
- Yang et al., *TRUSTMEM: Learning Trustworthy Memory Consolidation for LLM Agents with Long-Term Memory*: https://arxiv.org/abs/2606.25161
- Xu et al., *A-MEM: Agentic Memory for LLM Agents*: https://arxiv.org/abs/2502.12110
- Rasmussen et al., *Zep: A Temporal Knowledge Graph Architecture for Agent Memory*: https://arxiv.org/abs/2501.13956
- Chhikara et al., *Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory*: https://arxiv.org/abs/2504.19413
- Packer et al., *MemGPT: Towards LLMs as Operating Systems*: https://arxiv.org/abs/2310.08560
- Wang et al., *EvoMemBench: Benchmarking Agent Memory from a Self-Evolving Perspective*: https://arxiv.org/abs/2605.18421
