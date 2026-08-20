# Advisory Design Review — Cross-Workspace Personal Wiki, Library/Federation, and Sync Boundaries

Status: **ADVISORY / NON-BINDING / NOT AN ADR**  
Review date: **2026-08-20 KST**  
Review target snapshot: **`ef8869acc688e6b52b87570376560d7495c77cfa`**  
Repository: `YB-Park/llm-wiki-lab`  
Reviewer context: **AI-assisted architecture review conducted in conversation between the repository owner and OpenAI ChatGPT GPT-5.6 Sol**

> **Authority disclaimer**
>
> This document records an advisory review of one repository snapshot. It is **not** an accepted product decision, ADR, implementation plan, new critical-path item, or authorization to interrupt the current Dogfood GO baseline.
>
> In particular, this review must not be interpreted as permission to bypass Issue #141 natural installed dogfood, reopen E023/G3 semantic persistence/identity work, or weaken the current RAW / DERIVED / HUMAN_KNOWLEDGE authority boundaries.

## 1. Clarification: what “generality” means in this review

A prior advisory review used “generality” mainly to discuss source-note/document-centric derived knowledge, query-time semantic projections, identity, and whether persistent semantic structure should exist at all.

The repository owner clarified a different and more product-central meaning:

> **Generality here primarily means that the user’s LLM Wiki should outlive and transcend one VS Code workspace/project boundary.**

The motivating product behavior is not “support every file format” and not “invent a universal ontology.” It is closer to:

- while working in Project B, ask: **“How did Project A decide this?”**;
- while working in B, deliberately search A because a similar feature/problem existed there;
- find who owned a feature or decision in A, then recover the admitted evidence, reasoning, email/thread history, or Human Knowledge associated with that context;
- reuse prior project learning without copying it manually into B;
- preserve project provenance rather than flattening all memories into one anonymous global corpus.

The product idea can therefore be summarized as:

> **Project memory should become one scoped part of a user-owned Personal LLM Wiki Library.**

This is a different architecture axis from semantic ontology/generalization. The system may remain semantically conservative while becoming much broader in where trustworthy memory can be used.

## 2. Executive assessment

The strongest conclusion of this review is:

> **Do not start by migrating A/B/C into one giant “global Wiki root.” Preserve the existing project stores as authority boundaries and add a Personal Wiki Library / federation layer above them.**

Conceptually:

```text
Trusted VS Code workspace B
        │
        ├── Current project store B
        │      read + explicit write
        │
        └── Personal Wiki Library
               read according to explicit grants
               ├── Project store A
               ├── Project store C
               └── Optional Personal store later
```

This recommendation is not based on a general preference for federation. It follows directly from the current implementation.

Today, several important semantics are naturally **store/root scoped**:

- workspace opt-in;
- Human Knowledge;
- pending lineage decisions;
- source locators;
- maintenance usage accounting;
- Agent Wiki source notes;
- the canonical writer lock;
- manifest/raw/provenance integrity.

Those assumptions are coherent while one Wiki root effectively represents one project-memory authority boundary.

A single shared root can be made to work, but doing so immediately forces the project to redesign permission, source-locator identity, Human Knowledge scope, pending workflow scope, maintenance accounting, and cross-workspace disable semantics at the same time.

A library/federation layer avoids most of that migration and lets the existing Authority Core keep doing what it already does well.

A second conclusion is:

> **The first useful cross-workspace experiment does not need sync, a Personal store, graph/entity infrastructure, vector retrieval, or a new canonical schema.**

The minimum useful slice can be read-only federation over two existing local project stores.

## 3. Relationship to earlier reviews and issues

This review does not replace prior work.

### Issue #101

The 2026-08-15 product review already identified **Personal Wiki scope / workspace silo** as a major product gap and proposed a structure resembling:

```text
Project Store
Personal Store
Store Catalog
Federated Discovery
```

That direction was strategically strong.

This review re-evaluates it against the current 0.1.16 implementation and arrives at a more concrete conclusion: **federation is not only a plausible long-term shape; it is likely the lowest-risk first implementation path for the clarified cross-workspace product intent.**

### Issue #160 / E023

Issue #160 and `docs/14-generality-and-semantic-projections.md` answer a different question:

> What semantic representation should exist above admitted evidence, and when should derived semantic state persist?

The current answer remains conservative: query-time reconstruction is the default; persistent semantic state must earn itself; G3 automatic identity/routing remains closed.

Cross-workspace Personal Wiki capability does **not** require reopening that conclusion.

A user can ask B → A questions using the existing categories:

- `RAW_MEMORY`;
- `HUMAN_KNOWLEDGE`;
- current noncanonical source notes;
- query-time composition.

Therefore:

> **Scope generality can advance independently of semantic-persistence generality.**

### Issue #141

Issue #141 remains the immediate product-evidence track. It explicitly warns against beginning federation without recurring natural evidence.

This advisory review therefore preserves a design direction and candidate experiment only. It does not change the current runtime priority.

## 4. What the current code already gives us

The current implementation contains more useful groundwork for cross-workspace use than the product wording suggests.

### 4.1 The Wiki root can already be absolute

The VS Code host computes `wikiRoot(folder)` from `llmWiki.workspaceDirectory`. If the setting is an absolute path, it uses that path directly.

This means two workspaces can theoretically point at the same physical Wiki root.

That is useful as a diagnostic fact: the Python core is not fundamentally tied to `.wiki-lab` being physically inside the repository.

It does **not** mean a shared root is already a correct product design.

### 4.2 The core writer lock is root-scoped and process-safe on one machine

Canonical Python mutations use a store-level OS lock at `<root>/.writer.lock`.

Therefore multiple processes targeting the same root on one machine are not automatically unsafe for the Python mutations that participate in that lock.

This makes a shared-root prototype technically less reckless than it would otherwise be.

However, the lock does not solve permission scoping, Git/multi-machine divergence, or all host-side writes.

### 4.3 Discovery already knows how to score a union, not incomparable sub-corpora

`discovery.py` deliberately avoids comparing independently calculated per-topic BM25 scores. It gathers the union of current evidence objects, scores that union in one BM25 space, then attaches topic membership.

This is directly relevant to cross-project retrieval.

If multiple project stores are searched, their local BM25 scores should not simply be compared as if they were calibrated. The existing “score the authorized union once” principle is a stronger starting point.

### 4.4 Source identity is already opaque enough to avoid path-derived authority

The core deliberately refuses to derive `origin_id` from filenames or paths. Source IDs are generated as evidence-revision identities and raw object identity is content-addressed.

That discipline should be preserved when a project/store layer is added.

A Git remote URL, workspace path, display name, or repository folder name should not silently become canonical project identity.

## 5. Why “one global root” is attractive

A single shared root is the obvious smallest prototype:

```text
Workspace A ─┐
             ├── ~/.llm-wiki
Workspace B ─┘
```

It has real advantages:

- almost no new storage abstraction;
- current global discovery already spans topics in one root;
- one writer lock serializes many canonical writes;
- one backup target;
- one place to sync;
- source IDs are globally unique enough in practice within that root;
- raw object deduplication works naturally across all content.

If the project wanted a one-day throwaway proof that “B can retrieve something remembered from A,” this is a reasonable experiment harness.

But it is a poor first **product architecture commitment**.

## 6. Why the shared-root approach collides with current semantics

### 6.1 Workspace opt-in is actually root opt-in

`workspace-activation.js` stores one `workspace-opt-in.json` inside the Wiki root.

`isWorkspaceEnabled(root)` checks the core store plus that one marker.

If A and B point to the same root:

- enabling A creates the marker B also observes;
- disabling B deletes the marker A depends on;
- the stored record contains no workspace identity;
- “this workspace is enabled” and “this Wiki root is enabled” collapse into one bit.

That violates the product wording and weakens the authority boundary.

### 6.2 Source locators are workspace-relative but root-global

`agent-state.json` stores source locators as:

```text
source_id -> relative_path + sha256
```

Pending lineage rows also store `workspace_file` as a relative path.

That is correct when one root belongs to one workspace.

With a shared A/B root:

```text
A/docs/architecture.md
B/docs/architecture.md
```

both may be represented only as `docs/architecture.md` in workflow state.

The canonical source IDs remain distinct, but the host-side “same workspace file” meaning becomes ambiguous unless project/scope identity is added.

### 6.3 Human Knowledge is root-global and has no project/topic scope

Current Human Knowledge records are stored under:

```text
<root>/human-knowledge/
```

The record schema contains title, statement, reasoning, source IDs, supersession, authorship, timestamps, and integrity — but no project/topic scope.

Search runs over current Human Knowledge for the entire root.

In a single-project store that is coherent.

In a shared global root it immediately raises product questions:

- Was this decision made for A, B, or personally/globally?
- Should B see A’s project-specific Human Knowledge by default?
- Can a B decision supersede an A decision accidentally?

Adding scope to Human Knowledge is possible, but federation avoids needing that change for the first cross-project slice.

### 6.4 Pending lineage is root-global

`open_pending_lineage(root)` returns all open pending decisions in `agent-state.json`.

The Agent memory tool currently includes pending lineage rows in its result.

With one global root, B can receive pending workflow state originating in A even when the current question has nothing to do with A.

This is both UX noise and a potential boundary leak.

### 6.5 Maintenance accounting becomes accidentally global

`maintenance_usage` is one day + reserved-call count stored in `agent-state.json`.

The user-facing threshold is configured from the active workspace, but the counter lives in the shared root.

With a shared root, A/B consumption becomes aggregated while settings and mental model remain workspace-oriented.

That may eventually be desirable as a user-level budget, but it would be an accidental behavior rather than a designed one.

### 6.6 Human Knowledge writes are not covered by the Python store lock

Human Knowledge is currently implemented in the VS Code host and publishes Markdown/JSON with host-side atomic file writes.

It validates lineage before write, but does not participate in the Python store’s `.writer.lock` transaction.

The single-workspace baseline reduces the practical race surface. A global root shared by multiple Extension Hosts makes concurrent Human Knowledge supersession/fork races more realistic.

### 6.7 Current Git protection is workspace-relative, not remote-sync safety

`git-safety.js` returns `PROTECTED` whenever the Wiki path is outside the active workspace.

That is sensible for the current threat: “could `.wiki-lab` accidentally be committed into this project repository?”

It does **not** answer the new threat:

> “Is this external Wiki root itself a Git checkout that will push raw evidence to a public or otherwise unintended remote?”

Therefore an external global Git Wiki can currently appear “protected” while being intentionally synced somewhere the existing safety contract never evaluated.

This is one of the strongest reasons not to treat “absolute Wiki root + Git repo” as a product-complete solution.

## 7. Recommended conceptual architecture: Personal Wiki Library

The preferred product concept is:

```text
                          Personal Wiki Library
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
          Project Store A   Project Store B  Optional Personal Store
                 │                │                │
             topics           topics          personal knowledge
             evidence         evidence        / future sources
             HK               HK
             lineage          lineage
```

The active VS Code workspace binds to one **current project store**.

Other stores may be registered as readable library members under explicit grants.

The word “federation” here should not imply distributed systems complexity. The first implementation can be a local catalog containing paths to independent existing stores.

### 7.1 Store and project are not topic

Do not encode projects as topics.

`topic_id` currently represents filing/retrieval organization and owns temporal membership/supersession semantics.

A project may naturally contain:

```text
Project A
  topic: architecture
  topic: auth
  topic: vendor-decisions
```

Project/store scope is a different axis.

Collapsing project into topic would make it difficult to preserve both project boundaries and useful topical filing.

### 7.2 Physical root and logical identity should not be the same thing

A future catalog needs a stable opaque store/project identity, but it should not assume:

```text
scope_id = filesystem path
scope_id = Git remote URL
scope_id = repository name
```

Paths change. Repositories move/rename. Forks can share remotes or diverge. Display names collide.

A better direction is an opaque identifier plus mutable metadata such as display name/aliases.

For the smallest same-machine prototype, the catalog can assign a local opaque ID without migrating the store format.

For cross-machine sync/portable identity, a stable store ID likely needs to travel with the store eventually.

That later persistence should be a narrow explicit schema/config decision rather than inferred identity.

## 8. Recommended access model

Cross-workspace retrieval is not only a filesystem question. It is an **authority/model-exposure** question.

When `wikiMemory` returns A’s evidence while the user is in B, A’s content is exposed to the currently selected Agent/model.

Therefore:

> **A trusted B workspace does not automatically authorize model access to every other project store on the machine.**

The smallest useful policy model is two-sided:

### Store-side library grant

A project store can be explicitly registered as cross-workspace-readable.

Without that registration it is invisible to library search.

### Current-workspace/session library mode

The current workspace may allow one of roughly:

```text
off
explicit-only
ambient
```

For a first version, `explicit-only` is the safest default:

- ordinary B questions search B only;
- “in Project A…” may search A;
- “did we solve this in another project?” may search the authorized library;
- unrelated questions do not silently expose A/C to the model.

An `ambient` standing grant can be explored later if natural use shows that explicit-only routing is too restrictive.

### Write boundary

Default cross-project behavior should be:

```text
current project store: read + explicit write
other registered stores: read only
```

A later explicit user command such as “save this into A” can be separately gated.

Cross-project write is not necessary to prove the main product value.

## 9. Retrieval design for a library

### 9.1 Named-project retrieval

If the user asks:

> “How did A decide this?”

then the retrieval universe can be only A.

This is the simplest and most trustworthy cross-workspace case.

### 9.2 Library-wide retrieval

If the user asks:

> “Did I solve something similar in another project?”

then the system may search the union of explicitly authorized stores.

The important invariant is:

> **Authorization constrains the candidate universe before scoring.**

Do not score all stores and then remove inaccessible hits.

Otherwise inaccessible data can influence:

- document frequency / IDF;
- ranking order;
- candidate counts;
- thresholds;
- possibly timing/diagnostic behavior.

The safer flow is:

```text
registered stores
      ↓
authorization filter
      ↓
authorized current-evidence objects
      ↓
shared deterministic scoring space
      ↓
ranked candidates
```

This directly extends the current global-discovery principle used across topics.

### 9.3 Do not casually merge independent per-store BM25 scores

Current global discovery exists partly because topic-local raw BM25 scores are not comparable across corpora of different sizes.

The same problem reappears one level higher with project stores.

A first library retriever should prefer scoring the authorized union in one space rather than introducing arbitrary normalization or RRF by default.

This also avoids reopening E023 ranking complexity without evidence.

### 9.4 Duplicate bytes across projects

The current core understands that identical raw bytes are not automatically independent corroboration.

Library search should preserve that principle across stores.

If the same document exists in A and B, a cross-library result should be able to represent:

```text
one immutable content object
multiple store/project memberships
multiple evidence/source records
```

without presenting it as two independent supporting sources merely because two projects contained a copy.

### 9.5 Qualified provenance handles

Inside one store, `source_id` is enough to find a source.

Across independent stores, a model/tool result should not rely on a bare `src-...` alone even if random collision is practically unlikely.

The library layer needs a qualified address concept such as:

```text
store_id + source_id (+ topic_id when temporal status matters)
```

This does not require changing canonical source IDs. It can be a host/library-level handle that routes `wikiRead` to the correct existing store.

## 10. Cross-project semantic questions do not require persistent entity architecture

The motivating “find the person responsible in A, then inspect their decisions/emails” example may look like an entity/people-graph requirement.

It is not necessarily one.

A conservative first path is:

```text
B question
  ↓
explicitly target/search A
  ↓
recover A evidence mentioning owner/person/context
  ↓
search A again using recovered names/terms
  ↓
query-time dossier / grounded answer
```

If that repeatedly fails because identity/alias resolution is the blocker, the result becomes useful evidence for a later semantic identity experiment.

Until then, cross-workspace value should not be bundled with G3.

This is a useful product sequencing principle:

> **First prove that access to the right project memory is valuable. Then ask whether that memory needs more persistent semantic structure.**

## 11. Strongest candidate first slice: L0 local read federation

When the current Dogfood GO priority permits a new slice, the highest-value/lowest-risk experiment appears to be:

### Setup

- two real local project stores: A and B;
- B is the currently open trusted workspace;
- A is registered in a local Personal Wiki Library;
- A has an explicit cross-workspace read/model-exposure grant;
- no sync;
- no new model-backed maintenance;
- no migration of A/B canonical logs;
- no global write path.

### User behaviors

1. **Explicit project recall**
   - “How did A decide X?”
   - expected: target A, return A-labeled evidence/Human Knowledge, follow to verified raw when load-bearing.

2. **Cross-project similarity search**
   - “Did I solve something similar in another project?”
   - expected: search authorized library union, show which project each hit came from.

3. **Current-project ordinary question**
   - no cross-project intent.
   - expected: B-only by default.

4. **Unavailable/unauthorized project**
   - expected: bounded, explicit no-access/no-registration result; never silently fall back to unrelated stores.

### What this slice should not contain

- Git sync;
- Personal store writes;
- cross-project writes;
- entity graph;
- automatic person identity resolution;
- vector default;
- background indexing/maintenance;
- schema-v2 migration;
- multi-user collaboration.

The test is simply:

> **Does trusted cross-project retrieval materially reduce rediscovery and let normal Agent work reuse prior project decisions/reasoning?**

## 12. L0 implementation boundaries worth preserving in advance

Even before code exists, the following contract tests are worth treating as design requirements.

### Authorization isolation

- A not registered → B cannot search/read A.
- A registered but current workspace library mode off → A remains invisible.
- explicit A query under explicit-only grant → A visible.
- inaccessible store content must not affect BM25 statistics/ranking.

### Provenance isolation

- every cross-store result identifies its project/store source;
- bare source ID is never routed against an arbitrary store;
- verified raw read resolves within the same store that produced the search hit.

### Write isolation

- rememberSource in B writes only B by default;
- B cannot resolve A pending lineage merely because A was readable;
- B cannot supersede A Human Knowledge without a separate explicit cross-store write contract.

### Workflow isolation

- A pending lineage rows do not appear in ordinary B-only memory results;
- maintenance budget state does not become accidentally shared because the stores are registered together;
- A’s workspace opt-in marker does not control B.

### Failure containment

- missing/unmounted A store fails as “library member unavailable,” not as corruption of B;
- one damaged remote/read-only store must not make current B memory unusable unless the user explicitly targeted that damaged store;
- derived-note corruption in A remains fail-open to A raw evidence, consistent with current policy.

### Privacy/diagnostics

- sanitized diagnostics should not dump absolute roots or private project metadata by default;
- the Agent should be able to say which logical project scopes were used without requiring filesystem path exposure.

## 13. Optional Personal store should come after project federation proves useful

A separate user-level Personal store remains a coherent later component:

```text
Personal Store
  decisions that are not project-specific
  durable personal reasoning
  reusable preferences/principles
  explicitly promoted cross-project synthesis
```

But it should not be a prerequisite for the first cross-project experiment.

The current Human Knowledge model is naturally store-scoped. Keeping A decisions in A, B decisions in B, and only later adding Personal Human Knowledge is a cleaner migration than immediately adding a `scope_id` field to every existing Human Knowledge record.

A Personal store becomes valuable when natural use produces content whose authority genuinely belongs to the person rather than one project.

## 14. Git sync: a useful hypothesis, but a separate gate

The owner suggested a deliberately simple possibility:

> Put the Wiki in Git, sync/push it remotely, and use it from multiple places.

This is a strong hypothesis for a personal developer-oriented product because it offers:

- inspectability;
- familiar backup/version history;
- easy remote transport;
- no new server initially;
- user ownership;
- portability.

The main recommendation is not to reject Git. It is to define its role precisely:

> **Git can be Sync Provider #1. Git should not become the authority model or semantic merge engine.**

### 14.1 Safe first Git hypothesis

The narrowest credible experiment is:

```text
single writer at a time
pull/verify before use
write locally
verify
commit/push
```

If the remote has diverged:

```text
fail closed
no automatic semantic merge
```

This is enough to test whether “my Wiki follows me across machines” is valuable without solving distributed multi-writer history.

### 14.2 Why ordinary Git auto-merge is not yet trustworthy

The Wiki contains append-only logs whose semantic validity depends on replay and ordering constraints.

Two machines can both append valid local history but produce a textual conflict or a merged order that was never validated as one canonical history.

`agent-state.json` is even less merge-friendly because it is one whole JSON object containing:

- pending lineage decisions;
- source locators;
- maintenance usage.

Automatic text merge of that file could drop or duplicate safety-relevant workflow state.

Human Knowledge files are individually immutable-ish records, but supersession validation can race across hosts.

Therefore “Git can merge text” is not equivalent to “Wiki histories can be safely merged.”

### 14.3 Syncability classification is currently mixed

Before serious sync, state should be classified conceptually into at least:

- canonical / authority-bearing and must travel;
- safety-relevant workflow state that must not silently disappear;
- rebuildable derived state;
- host-local cache/locator/configuration;
- usage/budget telemetry.

Today `agent-state.json` intentionally mixes several of those roles.

Issue #132 already records that deletion of this state is not independently detectable and that canonical lineage + pending-state resolution are not one atomic transaction.

Those are tolerable known Alpha boundaries, but multi-machine sync increases their blast radius.

### 14.4 Derived Agent Wiki should not force sync semantics

Because Agent Wiki source notes are explicitly noncanonical/rebuildable, a future sync design should be free to:

- sync them as a cache for convenience;
- omit them and rebuild;
- invalidate them after source/policy mismatch.

The remote transport must never require derived artifacts to reconstruct authority.

### 14.5 Remote privacy needs a new contract

Current Git safety protects against accidental inclusion in the **active project Git repository**.

A sync provider needs a different decision:

> “I intentionally authorize this Wiki/store to leave the local machine and travel to this remote.”

That grant should be explicit and separate from workspace opt-in.

For GitHub-backed sync, repository visibility may be inspectable, but generic Git remotes do not provide one universal public/private semantic. The product should therefore avoid claiming generic remote privacy it cannot verify.

## 15. Concurrency implications

### Same machine, one shared root

The Python writer lock is a strong asset and would serialize many canonical mutations.

But host-side Human Knowledge publication and root-global workspace state still make shared-root use semantically awkward.

### Independent project stores

Federation naturally reduces write contention:

- A writes A;
- B writes B;
- library search reads both.

Cross-project retrieval becomes mostly a read-composition problem instead of a cross-project transaction problem.

That is another reason federation is the better first product slice.

### Multiple machines

This is a sync/replication question, not merely a writer-lock question.

The current OS lock cannot protect two clones on separate machines. A later sync provider must establish a separate no-divergence/lease/version protocol if concurrent writers are allowed.

Do not infer multi-machine safety from the existing local writer lock.

## 16. Store catalog: what it should and should not own

A minimal local library catalog could conceptually contain:

```text
store_id
root locator
mutable display name
optional aliases
read/library grant metadata
availability/health cache
```

It should **not** become a second canonical knowledge database.

The catalog should not own:

- raw evidence;
- correction/change/dispute truth;
- Human Knowledge text;
- source-note semantic truth;
- copied provenance.

It is a routing/authorization registry.

If it is lost, the desired long-term property is that registered stores remain intact and can be re-registered.

This is consistent with the project’s preference for reconstructible control-plane state where possible.

## 17. Scope naming and aliases

Users will say “A”, “payments”, “old gateway project”, or a repository nickname.

The product should support convenient aliases, but alias resolution should remain a routing aid rather than authority identity.

A safe pattern is:

```text
opaque store_id = stable identity
A / Payments / old-gateway = mutable aliases
```

If an alias matches multiple stores, fail closed or ask the Agent/user to disambiguate rather than guessing a target project and returning authoritative-looking memory from the wrong one.

## 18. Cross-project answers should expose scope provenance

A trustworthy answer should make it legible that information came from another project.

For example:

```text
Project A — Human Knowledge
Decision: ...
Reasoning: ...

Project A — Raw evidence
src-...
```

The user should not need a full database UI, but project scope should be visible enough that cross-project memory does not become context laundering.

A B answer that silently mixes A and B evidence is harder to audit and can create false assumptions that a policy/decision applies globally.

## 19. Scope is not applicability

A subtle but important rule:

> **Finding a decision in Project A does not mean that decision applies to Project B.**

Cross-project retrieval increases access, not epistemic transfer.

The Agent may say:

- “A chose X because Y”;
- “this may be relevant to B because the constraints look similar”;

but should not silently promote:

- “therefore B should use X.”

This is particularly important for Human Knowledge. A project-local decision is authoritative as a record of what was decided in A, not as a universal user preference.

A future Personal store can hold genuinely cross-project principles when the user explicitly promotes them.

## 20. Recommended sequencing

### Now

- keep 0.1.16 Dogfood GO baseline stable;
- continue Issue #141 natural installed use;
- preserve this review and Issue #202 as parked traceability.

### L0 — when activated

**Local read-only project federation**

- catalog two or more existing stores;
- current store read/write;
- other registered stores read-only;
- explicit-only cross-project access first;
- qualified provenance;
- authorized-union retrieval.

No sync and no semantic infrastructure.

### L1 — only if L0 is useful

**Personal Library UX / routing polish**

- project aliases;
- library availability/health;
- better Agent scope-routing hints;
- optional standing ambient-library grant if natural use justifies it.

### L2 — if genuinely cross-project human knowledge appears

**Optional Personal store**

- explicit personal/global Human Knowledge;
- project → personal promotion remains user-owned;
- no automatic promotion of project decisions into global beliefs.

### S0 — independent sync design gate

- classify syncable vs host-local vs rebuildable state;
- resolve or explicitly bound `agent-state.json` portability semantics;
- define remote privacy grant;
- define verified pre/post sync integrity.

### S1 — narrow Git replication experiment

- private/explicit remote;
- single-writer / no-divergence contract;
- pull → verify → use/write → verify → push;
- fail closed on divergence;
- no automatic canonical merge.

### Later only if earned

- concurrent multi-machine writers;
- service-backed sync;
- remote catalog/federation;
- cross-project writes;
- persistent cross-project semantic dossiers/entities;
- vector/index architecture for scale.

## 21. What not to bundle with this direction

This review specifically recommends against turning “Personal Wiki” into a bundle containing all of the following at once:

- global storage migration;
- PDF/DOCX/email ingestion redesign;
- universal ontology;
- entity graph;
- vector database;
- multi-root VS Code UI;
- cloud sync;
- automatic cross-project writes;
- background maintenance;
- people/profile database.

Those are independent axes.

The cross-workspace value proposition can be tested while nearly all of them remain absent.

## 22. Decision matrix

| Option | Strength | Main cost/risk | Review judgment |
|---|---|---|---|
| Shared global Wiki root | Fastest proof, one corpus, one backup | Conflates workspace opt-in, HK scope, locators, pending state, budgets | Useful throwaway/prototype harness; weak first product commitment |
| Project stores + local federation | Preserves current authority boundaries, minimal schema change | Needs catalog + cross-store retrieval composition | **Best first implementation hypothesis** |
| Project stores + Personal store + catalog | Best long-term conceptual fit | Personal/global HK semantics need explicit product design | **Recommended target shape after federation value is proven** |
| One new global schema/vault with project scope everywhere | Unified querying and storage | Broad migration and many simultaneous semantic changes | Too much for next slice |
| Cloud service first | Solves reachability/sync centrally | New trust, privacy, ops, auth, service dependency | Premature |
| Git-backed shared Wiki as architecture | Familiar developer workflow | Merge/privacy/concurrency semantics become architectural truth | Keep Git as provider/experiment, not core ontology |

## 23. Strongest final recommendation

The clarified product direction changes the interpretation of “general LLM Wiki.”

The next important generality question is not:

> “Can the Wiki represent more kinds of documents or entities?”

It is:

> **“Can one user carry trustworthy knowledge across project boundaries without destroying the provenance, permissions, and project-specific meaning that made the knowledge trustworthy?”**

The current code suggests a surprisingly conservative answer:

> **Do not globalize the Authority Core first. Globalize access to multiple existing Authority Cores.**

Or more concretely:

> **Project Store → Personal Wiki Library → authorized federated retrieval.**

This preserves the strongest current invariants, does not require G3, and creates a narrow product experiment with obvious user value.

If that experiment succeeds, then Personal storage and sync can be earned as the next layers.

Git is a credible first sync transport once remote exposure, state portability, and divergence are explicitly bounded. It should remain replaceable.

## 24. Reviewed implementation surfaces

Primary implementation and project sources inspected for this review at snapshot `ef8869acc688e6b52b87570376560d7495c77cfa`:

- `HANDOFF.md`
- `docs/00-project-charter.md`
- `docs/12-autonomy-ux-philosophy.md`
- `docs/14-generality-and-semantic-projections.md`
- `research/advisory-reviews/2026-08-19-generality-semantic-architecture-review.md`
- `dogfood/llm_wiki/store.py`
- `dogfood/llm_wiki/discovery.py`
- `dogfood/llm_wiki/agent_state.py`
- `dogfood/llm_wiki/agent_wiki.py`
- `dogfood/llm_wiki/writer_lock.py`
- `dogfood/vscode/entry.js`
- `dogfood/vscode/agent-tools.js`
- `dogfood/vscode/workspace-activation.js`
- `dogfood/vscode/git-safety.js`
- `dogfood/vscode/human-knowledge.js`
- `dogfood/vscode/package.json`
- Issue #25
- Issue #101
- Issue #110
- Issue #132
- Issue #141
- Issue #160

## 25. Traceability

A parked follow-up issue was created to preserve this architecture axis without promoting it to implementation:

- **Issue #202 — Advisory follow-up: cross-workspace Personal Wiki library/federation gate**

The intended relationship is:

```text
#141  current natural product evidence
#160  semantic structure / persistence generality
#202  cross-workspace Personal Wiki scope/library generality
#132  known workflow-state reliability boundary relevant to later sync
```

None of those links alone authorize implementation. The normal evidence → decision → ADR discipline remains in force.
