# PKM, Wikipedia, and Knowledge Organization — Research Batch D

Date: 2026-08-12
Status: research note, not policy
Related: Issue #10

## 1. Purpose

The earlier batches focus on machine reliability: compilation loss, temporal semantics, provenance, consolidation, regression, and maintenance cost.

A personal LLM Wiki is also a **human knowledge interface**. The user must be able to:

- understand what a page means,
- navigate from overview to detail,
- notice ambiguity,
- recover after renames/splits,
- distinguish source-backed knowledge from personal synthesis,
- and keep using the system without excessive ceremony.

This batch looks at Zettelkasten/PKM and Wikipedia as long-running examples of knowledge organization under growth.

---

## 2. Luhmann's Zettelkasten — connectivity matters more than a clean taxonomy

References:

- Niklas Luhmann Archive bibliographic record for *Communicating with Slip Boxes*: https://niklas-luhmann-archiv.de/bestand/bibliographie/item/luhmann_2015_T-AW01
- Digital Zettelkasten tutorial: https://niklas-luhmann-archiv.de/bestand/zettelkasten/tutorial
- English translation of the 1981 essay: https://zettelkasten.de/communications-with-zettelkastens/

Luhmann's own framing treats the slip box as more than external storage. Its value arises partly because established internal connections can surface combinations the user did not deliberately pre-plan.

The digital archive exposes multiple entry paths rather than one master hierarchy: content overview, keyword register, bibliography, search, note sequences, and cross-references.

### Transferable lesson

A personal knowledge system does not need one perfect taxonomy to be navigable.

Useful navigation may emerge from several overlapping mechanisms:

```text
shallow hierarchy
+ explicit links
+ indexes / maps of content
+ search
+ aliases / redirects
```

This argues against spending too much early effort discovering the "correct" folder tree.

### Important restraint

Modern popular claims such as "every note must be atomic" should not be treated as Luhmann's experimentally validated law. The archival system demonstrates dense linking and local continuation, but it does not establish an optimal digital note token size for LLM retrieval.

Atomicity therefore remains an E001 hypothesis, not a rule.

---

## 3. Retrieval strategy shapes authoring strategy

Recent empirical case study:

- Ferreira et al., *How People Manage Knowledge in their 'Second Brains' — A Case Study with Industry Researchers Using Obsidian*: https://arxiv.org/abs/2509.20187

The study reports that participants' retrieval strategies influenced how they built and maintained their personal knowledge bases.

This is a simple but important reversal of a common design process.

We often ask:

> "How should we organize documents, then how should search find them?"

But real personal systems may work in the other direction:

> "How do I naturally try to retrieve knowledge? That should influence how I author and link it."

### Project implication

E001 (representation) and E006 (retrieval) should not be evaluated independently.

A document structure that works well with hierarchical navigation may differ from one optimized for lexical/vector retrieval. The experiment matrix should evaluate **representation × retrieval strategy interactions**, not choose each in isolation.

---

## 4. Wikipedia's strongest idea for us: verifiability is not the same as inclusion

Primary policy:

- Wikipedia:Verifiability: https://en.wikipedia.org/wiki/Wikipedia:Verifiability

Wikipedia requires factual claims to be attributable to reliable published sources, but its policy also explicitly says that **not all verifiable information must be included**.

This is highly relevant to LLM Wiki ingestion.

A naive system can reason:

```text
source contains fact
=> fact is true/supported
=> put fact in wiki
```

Wikipedia separates two decisions:

```text
Is it supportable?
        !=
Is it useful/appropriate to include here?
```

### Personal-wiki translation

For us, likely questions are:

- Is this information grounded?
- Is it novel relative to what the wiki already knows?
- Is it likely to matter later?
- Does it belong in current synthesis or only raw evidence?
- Would including it improve retrieval or create noise?

This strengthens Q-INGEST-001 and the `No material` ingest outcome seen in Batch A.

A good ingestion system needs a **non-write outcome**.

---

## 5. Wikipedia's "no original research" policy does NOT transfer directly — but its boundary is useful

Primary policy:

- Wikipedia:No original research: https://en.wikipedia.org/wiki/Wikipedia:No_original_research

Wikipedia prohibits synthesis that combines sources to imply conclusions not supported by those sources.

Our personal wiki has a different purpose: generating new personal understanding and hypotheses is one of the main benefits.

Therefore copying the policy would cripple the system.

But the distinction is extremely useful:

```text
source-backed synthesis
        vs
our inference / interpretation / hypothesis
```

Wikipedia solves the risk by forbidding original synthesis from article space. We should probably solve it by **labeling/separating epistemic layers**.

Example:

```text
Evidence
  Source A says X.
  Source B says Y.

Sourced synthesis
  A and B both describe ...

Our interpretation
  This may imply Z because ...

Open question
  Need evidence for Z.
```

The danger is not having original thought. The danger is original thought silently becoming indistinguishable from sourced fact after several LLM rewrites.

This strengthens Q-REP-002 and Q-PROV-002.

---

## 6. Wikipedia summary style — progressive disclosure is a mature pattern

Primary guideline:

- Wikipedia:Summary style: https://en.wikipedia.org/wiki/Wikipedia:Summary_style

Summary style uses layered documents:

```text
broad parent article
   -> concise section about subtopic
   -> link to full child article
```

A child article can stand on its own while its parent exposes only the amount needed to understand the broader topic.

### Why this is promising for LLM Wiki

It maps naturally to our retrieval escalation concept:

```text
index / overview
    -> topic summary
        -> detailed page
            -> raw source
```

This provides **progressive semantic disclosure** for both humans and LLMs.

### Duplication problem

Wikipedia recognizes that duplicated parent/child summaries can drift and supports excerpt/transclusion patterns to keep related summaries synchronized.

This surfaces a critical design question for our wiki:

> If a fact appears in multiple summaries, which copy is canonical and how are the others kept consistent?

An LLM-based system that independently rewrites the same concept across five pages can manufacture contradiction through denormalization.

Possible approaches to test:

- accept duplication and lint it,
- one canonical child page + generated/excerpted summaries,
- independent summaries with explicit derivation/version links,
- retrieval-time generated parent summaries.

This should become part of E005/E007.

---

## 7. Wikipedia article splitting — size is a signal, not the semantic criterion

Primary guideline:

- Wikipedia:Article size: https://en.wikipedia.org/wiki/Wikipedia:Article_size

Wikipedia recommends logically splitting very large articles, but explicitly warns against treating raw size as the only determinant. Some topics simply need longer coverage; splitting should preserve adequate context and attribution.

### Direct implication for us

A hard rule such as:

```text
if page > 5,000 tokens: split
```

is too weak as a semantic policy.

Size can trigger inspection, but the actual split decision should consider:

- independent subtopics,
- semantic cohesion,
- retrieval patterns,
- edit locality,
- duplication after split,
- whether each child has enough independent purpose,
- whether parent summary retains necessary context.

This matches Batch A/Infini Memory results: token thresholds may be operational triggers, but semantic cohesion is the real target.

---

## 8. Redirects — schema migration should preserve old navigation paths

Primary guideline:

- Wikipedia:Redirect: https://en.wikipedia.org/wiki/Wikipedia:Redirect

Redirects exist for renamed topics, alternative names/spellings, merged topics, and other navigation cases.

### LLM Wiki implication

If a page moves from:

```text
concepts/rag.md
```

to:

```text
retrieval/retrieval-augmented-generation.md
```

breaking every historical link/query reference is unnecessary damage.

A rename/split/merge workflow should probably consider:

```text
new canonical identity
+ old aliases / redirect metadata
+ link migration
+ explicit history
```

This is especially important when LLMs may remember or generate old names.

### Deeper insight

Identity and location should probably not be exactly the same concept.

If page identity is only its filesystem path, taxonomy evolution becomes unnecessarily destructive.

We do not yet need UUIDs or a database. Even simple aliases/redirect stubs could decouple identity from path enough for a Markdown system. This is an E005/Q-SCHEMA-003 question.

---

## 9. Disambiguation — ambiguity should be represented, not guessed away

Primary guideline:

- Wikipedia:Disambiguation: https://en.wikipedia.org/wiki/Wikipedia:Disambiguation

Wikipedia uses disambiguation pages primarily as **navigation aids**, not content articles. Ambiguous names are routed to distinct topics rather than silently choosing one interpretation.

### Why this matters for LLMs

LLMs have a strong tendency to resolve ambiguity fluently.

In a personal wiki this can cause entity contamination:

```text
"MCP"
  Model Context Protocol?
  Microsoft Certified Professional?
  some internal project acronym?
```

If the system chooses incorrectly during ingest, unrelated evidence can become merged under one canonical page.

A robust system should be allowed to represent:

```text
ambiguous / unresolved identity
```

as a legitimate state.

The correct automation behavior may sometimes be **do not classify yet**.

This directly supports the automation principle that uncertainty should occasionally stop mutation rather than force a confident filing decision.

---

## 10. Wikipedia's anti-circular-source rule maps directly to recursive contamination

Wikipedia's verifiability policy tells editors not to cite Wikipedia itself or mirrors that rely on Wikipedia; the underlying reliable sources should be checked directly.

This is strikingly similar to our Q-PROV-002:

```text
wiki page B
  derived from source A

wiki page C
  reads B
```

C may use B for navigation/context, but treating B itself as independent evidence can create a citation loop.

### Candidate personal-wiki invariant

Not adopted yet:

> Derived pages may inform retrieval and synthesis, but factual promotion should retain a path to non-derived authoritative evidence.

This rule should be tested in E007 rather than accepted solely because Wikipedia uses an analogous editorial discipline.

---

## 11. Maintenance tags are a useful alternative to forced repair

Wikipedia supports intermediate states such as citation-needed, verification-needed, disputed, cleanup, merge/split proposals, etc.

The key architectural pattern is:

> detecting a problem does not require immediately resolving it.

This is especially valuable for LLM Wiki because automatic repair can be worse than visible uncertainty.

Potential states might include:

```text
needs_source
needs_verification
possible_duplicate
possible_split
possible_merge
stale_candidate
disputed
ambiguous
```

These should be thought of as **maintenance queue signals**, not necessarily permanent frontmatter fields.

This supports a human-review workflow where low-confidence semantic changes are proposed/batched instead of executed automatically.

---

## 12. Zettelkasten and Wikipedia solve opposite problems — both are relevant

Zettelkasten is optimized for an individual's creative thought process.

Wikipedia is optimized for a public encyclopedia constrained by verifiability and consensus.

Their differences are instructive:

| Dimension | Zettelkasten tendency | Wikipedia tendency | Personal LLM Wiki question |
|---|---|---|---|
| goal | generate/connect thought | summarize published knowledge | both |
| original ideas | central | excluded from article content | must be explicitly separated |
| structure | locally evolving links/sequences | named articles + policies/categories | hybrid? |
| authority | personal author | external reliable sources/consensus | multiple epistemic authorities |
| ambiguity | author can tolerate idiosyncrasy | explicit disambiguation | how much ambiguity can agent handle? |
| history | research trail | public page history | Git + semantic history? |
| scale | personal | massive collaborative | personal scale but LLM write amplification |

The correct design is unlikely to copy either system wholesale.

---

## 13. New hypothesis: separate knowledge identity from presentation surfaces

Across summary style, redirects, disambiguation, raw evidence, and current synthesis, a pattern emerges.

A concept may have one semantic identity but several useful presentations:

```text
canonical detailed knowledge
      |
      +-- overview summary
      +-- parent-page excerpt
      +-- alias/redirect
      +-- timeline view
      +-- source-evidence view
```

If each presentation independently owns truth, consistency cost explodes.

If every presentation is generated live, query cost and non-determinism may explode.

Therefore we need to experiment with where canonicality lives and which surfaces are stored vs derived.

This is a deeper version of E001 than simply "atomic vs topic note."

---

## 14. Representation × retrieval should be a joint experiment

After Batch D, E001 and E006 should be partially crossed.

Candidate matrix:

| Representation | Navigation | Lexical search | Semantic/vector | Agentic traversal |
|---|---|---|---|---|
| source summaries | test | test | test | test |
| topic docs | test | test | test | test |
| atomic linked notes | test | test | test | test |
| layered parent/child summaries | test | test | test | test |
| mostly raw + minimal index | test | test | test | test |

We do not need every Cartesian combination initially, but we should avoid concluding that a representation is bad when the retrieval method mismatches it.

---

## 15. Human-ergonomics constraints before we choose templates

Any future page template should be evaluated against at least these questions:

- Can a human understand the page without reading metadata machinery?
- Is the source/interpretation boundary visible when it matters?
- Can overview reading stay concise?
- Can exact evidence be reached quickly?
- Does a rename/split preserve old paths/aliases?
- Can unresolved ambiguity exist without forcing a bad classification?
- Can problems be flagged for later without triggering immediate expensive repair?
- Does the user need to review the same fact in multiple duplicate summaries?

This is where PKM experience intersects directly with our automation-boundary research.

---

## 16. Strongest conclusions from Batch D — hypotheses only

1. **A single perfect folder taxonomy is probably not required; multiple navigation mechanisms can coexist.**
2. **Atomicity is not a law. Semantic cohesion and retrieval behavior matter more than arbitrary note size.**
3. **Grounded information still needs an inclusion threshold; 'verifiable' does not mean 'put it in the wiki.'**
4. **Personal synthesis is valuable but must remain distinguishable from source-backed statements.**
5. **Layered summary/detail structure is promising, but duplicated summaries create consistency risk.**
6. **Redirects/aliases are likely essential for low-cost taxonomy evolution.**
7. **Ambiguity should sometimes remain unresolved rather than be auto-classified.**
8. **Problem detection and problem repair should be separate operations.**
9. **Representation and retrieval must be tested together.**

None are adopted policies.

---

## 17. Next dependency

The next batch should examine **software/database maintenance patterns** — materialized views, incremental recomputation, schema migration, dependency graphs, CI/regression testing, garbage collection, and docs-as-code.

The purpose is to convert our increasingly clear semantic risks into operational mechanisms that are cheap, deterministic where possible, and observable in Git/VS Code.

## 18. Sources

- Niklas Luhmann Archive, *Communicating with Slip Boxes* bibliographic record: https://niklas-luhmann-archiv.de/bestand/bibliographie/item/luhmann_2015_T-AW01
- Niklas Luhmann Archive, digital Zettelkasten tutorial: https://niklas-luhmann-archiv.de/bestand/zettelkasten/tutorial
- Luhmann translation, *Communications with Zettelkastens*: https://zettelkasten.de/communications-with-zettelkastens/
- Ferreira et al., *How People Manage Knowledge in their "Second Brains"*: https://arxiv.org/abs/2509.20187
- Wikipedia:Verifiability: https://en.wikipedia.org/wiki/Wikipedia:Verifiability
- Wikipedia:No original research: https://en.wikipedia.org/wiki/Wikipedia:No_original_research
- Wikipedia:Summary style: https://en.wikipedia.org/wiki/Wikipedia:Summary_style
- Wikipedia:Article size: https://en.wikipedia.org/wiki/Wikipedia:Article_size
- Wikipedia:Redirect: https://en.wikipedia.org/wiki/Wikipedia:Redirect
- Wikipedia:Disambiguation: https://en.wikipedia.org/wiki/Wikipedia:Disambiguation
