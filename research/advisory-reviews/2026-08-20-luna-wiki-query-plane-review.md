# Advisory Design Review — Luna Wiki Query Plane, Main-LLM Token Firewall, and Delegated Retrieval Reasoning

Status: **ADVISORY / NON-BINDING / NEAR-TERM PRODUCT CANDIDATE / NOT AN ADR / NO RUNTIME CHANGE**  
Review date: **2026-08-20 KST**  
Review target snapshot: **`ef8869acc688e6b52b87570376560d7495c77cfa`**  
Repository: `YB-Park/llm-wiki-lab`  
Reviewer context: **AI-assisted architecture review conducted in conversation between the repository owner and OpenAI ChatGPT GPT-5.6 Sol**

> **Authority disclaimer**
>
> This document records an advisory design review of the query/execution plane. It is not an ADR, accepted product policy, or authorization by itself to mutate the 0.1.16 installed runtime.
>
> Unlike the more speculative semantic-persistence questions parked by E023, this review identifies a **near-term product architecture candidate** that can be implemented largely above the current Authority Core. The recommendation to move quickly is still subordinate to explicit code-change authorization, CI, installed validation, and the existing RAW / DERIVED / HUMAN_KNOWLEDGE authority boundaries.

## 1. The problem this review is actually about

As the Wiki becomes larger and more heterogeneous, the cost of using memory can move from storage/retrieval into the **interactive main LLM's context and reasoning loop**.

Today the conversational Agent can ask the Wiki for candidates, inspect snippets, decide what matters, call `wikiRead`, read more raw text, compare sources, detect conflicts, and only then compose the user's answer.

That is acceptable while the Wiki is small.

It becomes structurally undesirable when the Wiki contains:

- many topics;
- long-lived project history;
- user-owned Human Knowledge;
- derived Agent Wiki notes;
- multiple related decisions or revisions;
- eventually multiple authorized project stores from the Personal Wiki Library/federation direction.

The failure mode is not merely latency.

The Wiki can become a **context tax** on the very LLM it is supposed to help.

The main Agent may consume substantial context and reasoning budget on:

1. query reformulation;
2. candidate review;
3. repeated source reads;
4. relation/identity ambiguity detection;
5. history/status inspection;
6. cross-source comparison;
7. conflict preservation;
8. provenance follow-through;
9. final synthesis.

The repository owner's proposed direction is therefore:

> **The main Agent should make a simple Wiki request and receive a compact final result. A cheap, fixed Luna worker inside LLM Wiki should absorb the retrieval/composition work that would otherwise expand the main Agent's context and reasoning burden.**

This review agrees with that direction, with one major qualification:

> **Hide retrieval complexity from the main Agent, but never hide provenance/authority from the product.**

The intended outcome is a **query-plane / token-firewall architecture**, not an opaque answer oracle.

---

## 2. Executive conclusion

The strongest recommendation is:

> **Introduce a first-class Wiki Query Plane between the interactive Main Agent and the Authority Core, with exact `gpt-5.6-luna` as the default internal query/composition worker.**

Conceptually:

```text
USER
  │
  ▼
MAIN AGENT
  │
  │  wikiConsult(self-contained question, optional scope hint)
  ▼
┌──────────────────────────────────────────┐
│          LLM WIKI QUERY PLANE            │
│                                          │
│  deterministic retrieval / authority     │
│  selection primitives                    │
│                │                         │
│                ▼                         │
│        LUNA QUERY WORKER                 │
│  read / compare / compose inside bounds │
│                │                         │
│                ▼                         │
│        compact WIKI BRIEF                │
└──────────────────┬───────────────────────┘
                   │
                   ▼
            AUTHORITY CORE
       RAW / HUMAN / temporal /
       provenance / current state
```

The key product property is:

> **Wiki-internal search complexity and Luna token consumption should not scale the Main Agent's conversation context in the same way.**

The main Agent should normally receive one compact evidence-backed brief rather than the intermediate retrieval transcript.

This is best understood as a **token and complexity firewall**.

A second conclusion is equally important:

> **Do not begin with a free-running Luna agent that has arbitrary tool access.**

E023 already tested several forms of planner/selector complexity and found that more model-driven retrieval machinery did not automatically preserve authority better. The first product slice should therefore be deliberately simpler than the long-term agentic vision.

Recommended order:

1. **L0 — `wikiConsult`: strong deterministic retrieval + one Luna authority-preserving composition call + compact brief.**
2. Dogfood whether this materially reduces Main-Agent Wiki context/turn burden while preserving answer quality/provenance.
3. **L1 — constrained iterative evidence-follow** only when L0 returns insufficient authority or natural use repeatedly demonstrates retrieval misses that a bounded follow-up can repair.

The architecture should support L1, but L1 does not need to be the first implementation.

---

## 3. Current 0.1.16 behavior: the Main Agent is still the librarian

### 3.1 `wikiMemory` is local retrieval, not Luna delegation

At the reviewed snapshot, the Agent-facing `llmWiki_searchMemory` / `wikiMemory` tool performs no model call.

Its runtime path concurrently gathers:

- RAW current discovery across topics;
- DERIVED Agent Wiki note search;
- open pending-lineage rows;
- HUMAN_KNOWLEDGE search.

It returns those results as `LLM_WIKI_MEMORY_RESULT v4` to the conversational Main Agent.

The tool's own contract explicitly tells the Main Agent to follow source IDs with `wikiRead` for load-bearing claims surfaced from DERIVED memory.

This means the Main Agent owns the final retrieval choreography.

### 3.2 The current Agent-visible payload can already become nontrivial

The current tool allows:

- up to 8 raw candidates;
- up to 3 derived candidates;
- up to 3 Human Knowledge candidates;
- up to 5 pending-lineage rows in the formatted result.

Raw discovery snippets are bounded to 320 characters each.

Derived note search can return snippets up to roughly 700 characters each.

Human Knowledge search returns the stored title/statement/reasoning record rather than a tiny fixed snippet; tool input allows statements up to 1,800 characters and reasoning up to 1,600 characters.

Even before provenance follow-through, a realistic `wikiMemory` result can therefore carry many thousands of characters into the Main Agent context.

### 3.3 `wikiRead` amplifies the effect

The Agent-facing `wikiRead` tool allows a verified raw read up to **12,000 characters** per call.

It may also include up to **6,000 characters** of the noncanonical Agent Wiki source note for the same source.

Therefore a Main Agent that performs three useful provenance reads can receive on the order of tens of thousands of Wiki characters after the initial memory result.

The exact host/model token accounting is platform-dependent, but the architectural direction is not ambiguous:

> **The current normal Agent path makes Wiki investigation payload scale directly into Main-Agent tool context.**

### 3.4 This is not a defect in the current Alpha

The current design was appropriate for proving:

- explicit authority labels;
- local read-only retrieval;
- provenance follow-through;
- prompt-injection hardening;
- human-owned decision recovery;
- natural tool routing.

The issue appears because the same explicit low-level interface is likely to become expensive as the Wiki becomes a broader long-term memory system.

---

## 4. A partial predecessor already exists: `Ask Luna`

The repository already contains an important architectural precursor.

The legacy/advanced `LLM Wiki: Ask Luna` path performs:

```text
question
   ↓
current topic-scoped deterministic retrieval
   ↓
render_context(...)
   ↓
exact gpt-5.6-luna
   ↓
validated citation handles
   ↓
read-only answer
```

The Python `ask` command requires:

- an explicit topic;
- `--allow-model-call`;
- a model, defaulting to `gpt-5.6-luna`;
- rendered current evidence.

The VS Code command also shows a modal before sending retrieved evidence to GitHub Copilot.

This is already the right **shape** for a token firewall: retrieval/context lives inside Wiki code, Luna composes, and the user sees an answer instead of manually inspecting every raw candidate.

However, it is not yet the desired Query Plane.

### 4.1 Current Ask Luna is one-shot, not an internal librarian

It does not let Luna:

- inspect initial hits and request a targeted follow-up;
- reformulate a query after discovering ambiguity;
- deliberately follow an identity/policy/temporal bridge;
- choose additional source reads iteratively;
- stop because a requested relation remains unsupported after bounded investigation.

It is conventional one-shot retrieval + composition.

### 4.2 Current Ask Luna is not the Agent's ordinary memory tool

Ordinary Agent use still goes through `wikiMemory` / `wikiRead`.

The Main Agent therefore still pays the investigation-context cost on the normal path.

### 4.3 Current Ask Luna is raw/topic-centric

The Python `ask` path uses `render_context` from raw retrieval.

The richer Agent tool path, by contrast, combines:

- raw discovery;
- Agent Wiki derived notes;
- Human Knowledge;
- pending lineage.

Therefore simply exposing the existing `ask` command as a new Agent tool would be a **coverage regression**, especially for user-owned Human Knowledge.

This is an important implementation seam.

---

## 5. Why the long-term architecture should have a Query Plane

The project already distinguishes durable authority from derived representations.

A complementary runtime distinction is useful:

```text
INTERACTION PLANE
  Main Agent + current user/task context
        │
        ▼
QUERY PLANE
  retrieve / inspect / follow / compose
        │
        ▼
AUTHORITY PLANE
  immutable evidence / Human Knowledge /
  provenance / temporal semantics / integrity
```

The Main Agent and Query Plane have different jobs.

### Main Agent

The Main Agent should answer:

- What is the user trying to accomplish?
- Does prior memory matter?
- How should recovered memory affect the current code/design/task?
- What current conversation context needs to be included in the Wiki question?

### Wiki Query Plane

The Query Plane should answer:

- Which admitted memory is relevant?
- Which sources need verified follow-through?
- Is a bridge/attribution/temporal relation actually established?
- Is a Human Knowledge item the load-bearing authority rather than external evidence?
- Is there an unresolved conflict or explicit negative boundary?
- Is the admitted authority insufficient?
- What compact answer can be returned with terminal provenance?

This separation has a useful product invariant:

> **The Main Agent decides what to ask the Wiki; the Wiki decides how to investigate its own admitted memory.**

That is a more scalable mental model than making every future Main Agent learn the Wiki's internal retrieval choreography.

---

## 6. The proposed public tool contract: `wikiConsult`

The exact transport may remain a VS Code Language Model Tool initially and become MCP-compatible later.

Transport is not the architecture decision.

The product contract should look approximately like:

```text
wikiConsult({
  question: "How did we decide X, and why?",
  scopeHint?: "current" | project/library hint
})
```

The Main Agent should provide a **self-contained information need**, not a raw bag of search keywords.

The initial API should resist optional knobs such as `topK`, `maxChars`, planner depth, or model selection. Those are Query Plane implementation details and exposing them simply moves librarian work back into the Main Agent.

### 6.1 Main-Agent behavior

For an ordinary historical/project-memory question, the Main Agent should normally:

1. formulate one compact self-contained Wiki question;
2. call `wikiConsult` once;
3. use the returned brief in the final task response.

It should **not** routinely follow the brief with `wikiRead` merely because the brief is derived.

The Query Plane is responsible for having already resolved its load-bearing basis to terminal authority before returning the brief.

`wikiRead` remains useful when:

- the user explicitly asks for source text/provenance detail;
- exact wording or a quote matters;
- the consult result reports insufficient/ambiguous authority and the user wants to inspect it manually;
- debugging or expert inspection is requested.

This distinction is essential. If every `wikiConsult` is followed by multiple raw reads, the token firewall has failed its purpose.

---

## 7. The return value should be a Wiki Brief, not opaque prose

The correct interpretation of “return only the final result” is:

> **Return only the final useful synthesis to the Main Agent, but preserve compact authority/provenance metadata.**

It should not mean:

> “Return an unsupported paragraph from Luna and make the Main Agent trust it.”

A minimal conceptual v1 shape can stay close to the strongest generic E023 composition output contract:

```text
LLM_WIKI_CONSULT_RESULT v1
query_authority=read_only_derived_query_brief
model=gpt-5.6-luna
canonical_mutation=none
insufficient_authority=no

answer_json="We decided ... because ... [src-...]"
terminal_authority_refs=src-...,hk-...
```

Potential compact additions, if they prove useful:

```text
scope_refs=project-A
conflict_status=none|present|unclear
query_model_calls=1
```

Avoid returning a large internal search trace by default.

### 7.1 Preserve epistemic type naturally

If the result depends on Human Knowledge, the answer should say things like:

- “we decided ...”;
- “your recorded decision says ...”;

rather than presenting the user-owned commitment as independent external fact.

The E023 authority-preserving composition contract already contains this principle.

### 7.2 Preserve direct vs attributed evidence

The brief must not flatten:

- “Alice wrote X”;
- “meeting notes say Alice said X”;
- “a later summary characterizes Alice as X”.

Those are different evidence relations.

### 7.3 Preserve insufficiency

If a requested identity/policy/project/temporal/authorization bridge is missing, the brief should return the supported parts plus the ambiguity.

A confident truth-by-luck answer is a failure even if the guessed conclusion happens to be correct.

### 7.4 Citation validation is necessary but not sufficient

Current `ask_copilot` hardening already does valuable work:

- generated source IDs are replaced with transient citation handles;
- raw evidence cannot invent a citable canonical ID;
- unknown handles fail closed;
- missing citations fail closed;
- a model identity mismatch fails closed;
- prompts are sent through stdin rather than process argv.

Those protections should be reused.

However, citation-handle validation proves that a cited source was supplied; it does **not** deterministically prove semantic entailment of every generated claim.

Therefore the Query Plane remains a derived semantic component and must keep its output explicitly noncanonical.

---

## 8. Why a free-running Luna agent is the wrong first implementation

The user-level vision is correctly agentic: Luna should be able to “dig through the Wiki.”

But E023 supplies a strong warning against starting with unconstrained planning/selection complexity.

### 8.1 E023 G1 planner/selector complexity did not earn itself

E023 tested query-time retrieval/composition mechanisms with exact `gpt-5.6-luna`.

Important retained observations include:

- a question-only planner + BM25 + RRF top-5 had zero semantic improvements over the simple exact-query baseline;
- missing load-bearing sources frequently sat just outside a fixed cutoff;
- evidence-follow retrieval repaired one important identity bridge but did not meet its prospective retrieval promotion threshold;
- later deterministic evidence-follow RRF top-4 spent **8 planner calls** and produced **0 authority improvements and 1 regression**;
- lexical distractors were sometimes reinforced rather than removed;
- in another case the planner correctly identified the missing governing policy, but the candidate-generation budget still failed to expose it.

This is a critical lesson:

> **Model-driven planning cannot compensate for a retrieval primitive that never exposes the needed authority, and more planning can create new selection bottlenecks.**

### 8.2 A stronger simple baseline emerged

E023 also found that a modestly larger exact lexical evidence prefix repaired important prospective authority misses without planner/selector calls on one separated slice.

G1f then showed both the old and new generic composers at **7/8 PASS, 0 critical errors** on a new separated composition-stress set using the same strong simple exact-BM25 top-6 context.

The project correctly did **not** promote “top-6” as a universal product constant.

The useful mechanism lesson is instead:

> **Before adding an agentic planner, make sure the simple evidence budget/retrieval floor is strong enough.**

The Query Plane should inherit that discipline.

---

## 9. Recommended staged architecture

### L0 — Token Firewall / one-shot Wiki Consult

Goal:

> Move normal Wiki composition off the Main Agent immediately without introducing a new agent-planning research program.

L0 should:

1. use the current authorized Wiki scope;
2. deterministically gather a bounded current candidate set;
3. use DERIVED notes only as noncanonical navigation signals, never terminal authority;
4. include relevant Human Knowledge as explicit user-owned terminal authority;
5. resolve load-bearing raw candidates to bounded verified raw evidence before composition;
6. call exact `gpt-5.6-luna` once with an authority-preserving composition prompt;
7. validate output citation handles/source identities;
8. return a compact Wiki Brief to the Main Agent;
9. mutate no canonical or derived Wiki state.

This already solves most of the architectural token problem.

It also has a very favorable implementation profile because the repo already has:

- `wikiMemory` candidate aggregation;
- raw discovery;
- derived-note search;
- Human Knowledge search;
- verified source reads;
- hardened Luna invocation;
- authority-preserving composition research prompts/fixtures.

### L1 — Constrained iterative evidence-follow

L1 should be added only when natural L0 use demonstrates a need, or when L0 explicitly returns insufficient authority and a bounded follow-up is justified.

L1 is not a generic autonomous agent.

It is a host-controlled state machine with a small action vocabulary, conceptually:

```text
SEARCH(query, authorized_scope)
READ(source_id, bounded_range)
STATUS(source_id/topic)
FINAL(answer, terminal_refs, insufficient)
```

Optional future primitives may include explicitly bounded history/temporal inspection.

Luna should never receive:

- shell;
- arbitrary filesystem access;
- web access;
- generic MCP access;
- source-admission tools;
- Human Knowledge mutation;
- correction/change/dispute/supersession mutation;
- derived maintenance writes.

The controller executes each requested action and validates its arguments.

### 9.1 Why L1 should be controller-mediated

The current hardened Copilot invocation intentionally disables built-in tools/MCPs and agent/task capabilities.

That is a good safety property to preserve.

A controller-mediated loop allows Luna to request Wiki operations without giving evidence text the opportunity to escalate into arbitrary process/network/tool authority.

### 9.2 L1 state should be ephemeral

A query session may internally track:

- normalized question;
- authorized scope;
- search queries issued;
- source IDs already inspected;
- bounded evidence fragments;
- follow-up count;
- terminal citation mapping;
- insufficiency status.

This is **query execution state**, not durable Wiki knowledge.

It should not become:

- RAW evidence;
- HUMAN_KNOWLEDGE;
- a persistent entity graph;
- a persistent semantic dossier;
- an automatically maintained Agent Wiki page.

This keeps the proposal compatible with E023's current query-time reconstruction posture.

---

## 10. Do not store or expose Luna chain-of-thought

The requirement that the intermediate process be “hidden” should be implemented as:

> **Do not inject the internal retrieval/reasoning transcript into the Main Agent's context.**

It should not be implemented as an unauditable black box.

Useful inspectable execution metadata can include:

- model identity;
- model-call count;
- search-operation count;
- source IDs read;
- authorized scopes consulted;
- bounded failure codes;
- final terminal authority refs;
- total internally inspected evidence characters;
- latency.

Do **not** require, persist, or expose private chain-of-thought.

An action/provenance trace is enough for debugging and product trust.

---

## 11. Permission boundary: Query Reasoning needs its own standing grant

This is one of the most important product consequences.

Current `Ask Luna` requires a modal confirmation before retrieved evidence is sent to GitHub Copilot.

An ambient `wikiConsult` cannot show that modal on every ordinary memory query without defeating the intended Agent-first UX.

Therefore the product needs a separate standing grant roughly meaning:

> **Allow LLM Wiki to send retrieved admitted memory to exact Luna for read-only query reasoning in this workspace/scope.**

This is not the same as:

- workspace memory opt-in;
- Agent Wiki maintenance permission;
- source admission;
- Human Knowledge authorship;
- paid/background maintenance budget.

Do not silently reuse the existing AI-summary maintenance grant.

### 11.1 Cross-provider disclosure matters

If the Main Agent is not itself GitHub Copilot, `wikiConsult` may send Wiki evidence to an additional provider/model path.

That must remain an explicit privacy boundary even if the Main Agent would otherwise have received raw tool results.

### 11.2 Prefer local product-owned grant state

A standing query-model grant should preferably be local product state scoped to the workspace/library authorization context, not a setting that can be accidentally committed and shared as project configuration.

The exact storage choice needs implementation review, but the semantic requirement is:

- explicit;
- revocable;
- scope-bound;
- not silently broadened by opening another project;
- no per-query approval storm after it is granted.

---

## 12. Model policy: exact Luna, no silent fallback

The repository owner explicitly prefers Luna for this workload because its token economics make Wiki-internal reasoning cheap enough that token minimization inside the Query Plane is not the primary concern.

That preference should become a simple product hypothesis:

> **Use exact `gpt-5.6-luna` as the Query Plane worker. Do not add model routing/selection complexity unless independent evidence later requires it.**

This is consistent with the current adapter, which verifies the returned model identity.

### 12.1 No silent fallback to the Main Agent

If Luna is unavailable, authentication fails, or the exact model cannot be used, the Query Plane should fail with a bounded causal result.

It should not silently respond by dumping low-level raw results into the Main Agent and asking the expensive model to take over.

That would violate the token-firewall contract precisely when the user least expects it.

A low-level manual fallback may remain available through `wikiMemory/wikiRead`, but it should be explicit rather than automatic.

### 12.2 No daily “cheap model” cap by default

Interactive Wiki query reasoning is different from optional background/ingest maintenance.

The current maintenance soft-guard exists for standing derived generation/spend behavior.

For user-triggered/Agent-triggered interactive `wikiConsult`, the primary safety bound should be **per-consult loop/evidence/latency bounds**, not an arbitrary low daily call quota.

Track usage for visibility; do not optimize away the very Luna reasoning the architecture is intended to delegate.

---

## 13. The optimization target changes

The product should distinguish at least three resource surfaces:

1. **Main-Agent Wiki burden**
   - Main-visible Wiki result characters/tokens;
   - number of Wiki tool turns visible to the Main Agent;
   - number of Main-Agent follow-up reads caused by Wiki use.

2. **Internal Query Plane work**
   - Luna model-call count;
   - internal evidence characters/tokens inspected;
   - search/read operations;
   - latency.

3. **Provider billing/usage**
   - exact token usage when upstream reports it;
   - actual AI credits/premium requests only when upstream reports them;
   - never infer billing units from call count or token count.

For this architecture, the primary product metric is:

> **How much useful, trustworthy Wiki knowledge reaches the Main Agent per unit of Main-Agent context/interaction burden?**

A large Luna-internal token count is acceptable if:

- answer quality is preserved;
- latency remains tolerable;
- provider policy permits it;
- the Main Agent receives a small stable interface.

This is intentionally different from optimizing total tokens across all models.

---

## 14. Concrete implementation seam in the current codebase

The current language/runtime split matters.

### 14.1 The rich Agent memory aggregator lives in JavaScript

`agent-tools.js` currently combines:

- Python raw discovery;
- Python Agent Wiki note search;
- JavaScript Human Knowledge search;
- JavaScript/CLI pending state.

Human Knowledge is implemented and integrity-validated in `human-knowledge.js`.

### 14.2 The existing Luna answer path lives in Python

`adapters.py` owns the hardened `ask_copilot` transport and citation-handle boundary.

The Python `ask` command builds raw context and invokes Luna.

### 14.3 Do not solve L0 by duplicating authority semantics casually

A naive Python-only Query Plane would either omit Human Knowledge or duplicate the JavaScript Human Knowledge validation/search semantics.

Neither is attractive for a fast first slice.

The narrow implementation candidate is therefore:

> **Keep L0 candidate aggregation/control in the VS Code JavaScript layer, and add a small stdin-based Python composition bridge that reuses `ask_copilot` for exact Luna.**

Conceptually:

```text
agent-tools.js
  │
  ├─ raw discover/search
  ├─ derived search -> source routing
  ├─ Human Knowledge search
  ├─ verified raw materialization
  │
  └─ stdin JSON envelope
          │
          ▼
query_plane_cli.py / query_plane.py
          │
          └─ adapters.ask_copilot(... gpt-5.6-luna ...)
                  │
                  ▼
             compact result
```

Using stdin matters because the repo already deliberately moved private/user evidence out of process argv.

Do not reintroduce prompt/evidence argv leakage just to bridge JavaScript and Python.

---

## 15. Suggested code surface for an L0 implementation

This is an advisory map, not an implementation authorization.

### `dogfood/vscode/package.json`

Likely changes:

- add a `llmWiki_consultMemory` Language Model Tool;
- tool reference name such as `wikiConsult`;
- make its description the preferred ordinary memory-query path;
- keep low-level search/read as explicit provenance/debug surfaces;
- add a user-visible command or onboarding surface for the standing Luna query grant if needed.

### `dogfood/vscode/entry.js`

- Agent tool count moves from 5 to 6 if `wikiConsult` is added rather than replacing an existing tool;
- runtime registration remains gated by workspace trust/opt-in.

### `dogfood/vscode/agent-tools.js`

- add `WikiConsultTool`;
- reuse current raw/derived/Human Knowledge candidate aggregation;
- construct a bounded terminal-authority context;
- call a stdin-backed query-plane model bridge;
- format a compact result;
- keep canonical mutation impossible;
- avoid routinely returning raw snippets to the Main Agent.

### `dogfood/llm_wiki/query_plane.py` / `query_plane_cli.py`

Candidate responsibilities:

- accept a strict JSON envelope via stdin;
- validate exact allowed shape/size;
- construct/freeze an authority-preserving query prompt;
- call exact Luna via existing hardened adapter;
- validate exact compact JSON output;
- return only bounded structured output;
- no store writes;
- no filesystem discovery outside already supplied/validated Wiki context;
- no generic tool access.

### `dogfood/llm_wiki/adapters.py`

- reuse the current stdin Copilot transport;
- reuse citation-handle isolation/materialization;
- preserve exact model mismatch failure;
- potentially factor a generic cited structured-call helper rather than copy the hardened transport.

### Existing Authority Core modules

Prefer **no changes** to:

- raw store identity;
- manifest/provenance;
- correction/change/dispute semantics;
- Human Knowledge authorship model;
- writer locking;
- source admission.

That is one reason this is a good near-term candidate: the feature can live mostly in the read/query plane.

---

## 16. How DERIVED Agent Wiki should participate

DERIVED memory remains useful, but its role should be precise.

For the Query Plane:

> **DERIVED Agent Wiki is a navigation/index signal, not terminal factual authority.**

A derived note may help identify:

- a relevant source ID;
- a concept/term that lexical raw search missed;
- a likely area to inspect.

Before Luna's final load-bearing claim relies on that content, the Query Plane should resolve back to:

- verified RAW evidence; or
- explicit HUMAN_KNOWLEDGE.

This lets the product gain semantic-routing value from derived notes without laundering them into truth.

The rule matches the project's existing authority philosophy and the E023 authoritative-anchor invariant.

---

## 17. How HUMAN_KNOWLEDGE should participate

Human Knowledge is not merely another lexical document.

It is terminal authority for:

- what the user/project explicitly decided;
- what rationale the user explicitly confirmed;
- what the user explicitly believes or owns as a hypothesis.

The Query Plane should preserve that ownership in the brief.

Example:

Bad:

> “Redis is used only for queues.”

Better when the load-bearing basis is Human Knowledge:

> “Your recorded project decision is to use Redis only for the queue subsystem.”

If supporting raw evidence is linked and materially relevant, the Query Plane may inspect it as additional support, but Human Knowledge should not be disguised as independent external corroboration.

---

## 18. Cross-workspace federation makes this architecture more important, not less

The separate cross-workspace advisory recommends project-store federation/library rather than one giant global root.

If that direction is later implemented, the Query Plane becomes the natural single interface over multiple authorized stores.

The Main Agent should not have to do:

```text
search B
read B1
search A
read A3
search C
read C2
compare A/B/C
```

Instead:

```text
wikiConsult(
  question="Did another project solve a similar issue, and what did it decide?",
  scopeHint="all authorized projects"
)
```

The Query Plane can perform the store-specific retrieval internally and return one compact project-attributed brief.

### 18.1 Authorization must still be outside Luna

The authorized store set must be fixed **before candidate generation and before Luna sees any evidence**.

Luna may not decide:

- which unauthorized project to open;
- whether a workspace grant should be widened;
- whether another project is readable because its name looks relevant.

The Query Plane is a consumer of the authorization boundary, not an authority to modify it.

---

## 19. Prompt-injection and tool-authority implications

The current product correctly treats memory text as untrusted data.

A more agentic internal query worker increases the importance of this rule because malicious admitted evidence could attempt to instruct the internal worker to:

- call external tools;
- expose secrets;
- widen scope;
- mutate memory;
- ignore policy;
- follow invented source IDs.

The proposed controller-mediated design contains the blast radius:

- evidence remains quoted/untrusted;
- Luna receives only Wiki-query actions;
- action arguments are controller-validated;
- source IDs must exist in the authorized Wiki view;
- external web/shell/filesystem tools are absent;
- all mutations are absent;
- final citations must resolve to supplied terminal authority.

This is preferable to giving Luna a generic MCP/tool environment and relying on prompt instructions alone.

---

## 20. Failure modes and explicit mitigations

### F1. Semantic bottleneck / Luna summary becomes de facto truth

Risk:

The Main Agent sees only the brief and over-trusts it.

Mitigation:

- explicit `derived_query_brief` status;
- terminal authority refs in the result;
- insufficiency field;
- raw/Human ownership semantics preserved;
- user can inspect provenance on demand.

### F2. Truth-by-luck

Risk:

Luna answers a missing identity/policy/temporal bridge correctly by coincidence.

Mitigation:

- authority-preserving composer contract;
- missing bridges must produce ambiguity/insufficiency;
- L1 may perform bounded follow-up when justified;
- no semantic claim that citation validation equals entailment proof.

### F3. Retrieval candidate ceiling hides the needed source

Risk:

No planner can recover authority it never sees.

Mitigation:

- preserve a strong simple evidence budget;
- do not prematurely squeeze internal Luna evidence for token savings;
- evaluate evidence budget before planner complexity;
- use natural L0 failures to justify L1.

### F4. Agentic loop burns many calls without improving authority

Risk:

E023 already observed planner overhead without net authority gain.

Mitigation:

- L0 first;
- L1 only conditional;
- per-consult round/search/read bounds;
- stop/fail as insufficient when bounds expire;
- usage trace available for diagnosis.

### F5. Prompt injection widens tool authority

Mitigation:

- host-mediated small action set;
- no shell/web/arbitrary MCP;
- memory text always untrusted data;
- controller validates action scope/IDs.

### F6. Query model grant is confused with maintenance permission

Mitigation:

- separate standing Luna query grant;
- separate UX wording/counters;
- no silent reuse of AI-summary setting.

### F7. Luna unavailable causes surprise Main-Agent token explosion

Mitigation:

- fail closed with causal result;
- no silent low-level fallback;
- manual/raw fallback remains explicit.

### F8. Query transcript becomes durable semantic state

Mitigation:

- query session is ephemeral;
- no automatic write-back;
- any later reusable synthesis must follow existing Agent Wiki/Human Knowledge authority rules separately.

### F9. Main Agent ignores `wikiConsult` and keeps using low-level tools

Mitigation:

- tool descriptions make `wikiConsult` the preferred ordinary memory path;
- low-level tools become provenance/debug-specific;
- installed dogfood measures actual routing;
- if necessary, later hide/de-emphasize low-level search from ambient model routing without removing expert/manual access.

### F10. Hidden usage becomes confusing

Mitigation:

- return/query-log exact model-call counts;
- surface usage in product-owned UI when needed;
- keep tokens and premium/AI-credit billing units distinct;
- do not introduce a low arbitrary daily query cap merely because usage is hidden.

---

## 21. Evaluation: this does not require another giant research program

The first question is primarily a **product/runtime architecture** question:

> Can the Wiki absorb its own retrieval/composition work while sending much less material and fewer tool turns to the Main Agent?

E023 already supplies enough warning/evidence to avoid starting with elaborate retrieval planning.

Therefore L0 should not be blocked on a new large synthetic architecture bake-off.

### 21.1 L0 product metrics

Measure at least:

- `main_visible_wiki_chars`;
- Main-Agent Wiki tool-turn count;
- number of Main-Agent raw follow-up reads;
- Luna model-call count;
- internal evidence characters inspected;
- end-to-end latency;
- returned terminal authority ref count;
- `insufficient_authority` rate;
- user/Agent helpfulness outcome;
- provenance follow-through when explicitly requested.

Stable character counts are useful even when exact Main-Agent tokenizer accounting is unavailable.

### 21.2 Semantic safety checks

Use new/fresh cases or natural use for:

- Human Knowledge ownership preservation;
- direct vs third-party attribution;
- missing identity bridge;
- current vs superseded evidence;
- unresolved dispute;
- explicit negative/non-goal boundary;
- malicious instruction inside evidence;
- citation outside supplied authority;
- Luna model mismatch/unavailability.

Do not rerun frozen E023 semantic slices merely to produce a positive number.

### 21.3 L1 promotion evidence

L1 should be justified by examples where:

- L0 is insufficient/wrong because the first candidate context lacks a necessary authority bridge;
- a bounded follow-up could plausibly retrieve that bridge;
- the improvement cannot be obtained simply by a safer evidence budget or existing derived-navigation signal.

The relevant success criterion is not “Luna used more reasoning.”

It is:

> **The bounded follow-up recovers missing authority or resolves ambiguity with no unacceptable new semantic regressions.**

---

## 22. Proposed initial zero-model / mocked contract tests

Before any real Luna product call, the implementation can cheaply prove:

1. `wikiConsult` is read-only and cannot mutate manifest/provenance/Human Knowledge.
2. no Luna query occurs without the explicit standing query grant.
3. query grant is distinct from Agent Wiki maintenance permission.
4. exact Luna model identity is required; no fallback model.
5. no prompt/evidence appears in process argv.
6. model output cannot cite an unknown or raw-evidence-injected source handle.
7. Human Knowledge carries explicit user-owned authority metadata into the composition context.
8. DERIVED note text cannot become terminal authority without raw/Human resolution.
9. superseded evidence is not silently presented as current.
10. malicious evidence cannot request shell/web/write operations because those operations do not exist in the query controller.
11. Luna failure does not dump the raw candidate corpus into the Main Agent automatically.
12. compact result size remains bounded even when internal evidence context is large.
13. tool activity trace contains action/source metadata but no required chain-of-thought.
14. disabling the workspace still hides the query tool.
15. if future federation is enabled, unauthorized stores never enter retrieval scoring or the Luna prompt.

---

## 23. Recommended implementation progression

### Phase Q0 — advisory/design freeze

This document + tracking issue.

No runtime change.

### Phase Q1 — L0 product slice

Implement:

- separate query-model standing grant;
- `wikiConsult` Agent tool;
- current-store only;
- deterministic candidate collection;
- Human Knowledge + verified raw authority context;
- DERIVED navigation only;
- one exact Luna composition call;
- compact brief;
- no automatic raw follow-up by Main Agent;
- zero-model/mock hardening tests.

Do **not** combine with cross-workspace federation in the first code slice.

### Phase Q2 — installed natural dogfood

Observe:

- whether the ordinary Main Agent chooses `wikiConsult` naturally;
- whether answers remain useful;
- how much Wiki payload/turn count drops from the Main Agent path;
- whether users still frequently need manual `wikiRead`;
- whether L0 misses expose a repeated need for follow-up retrieval;
- whether interactive Luna latency is acceptable.

### Phase Q3 — constrained L1 only if earned

Add bounded SEARCH/READ/final loop only from actual L0 insufficiency/miss evidence.

No graph/entity/vector/persistent semantic state is implied.

### Phase Q4 — connect to Personal Wiki Library

If/when the separate federation direction is implemented, add authorized multi-store scope underneath the same `wikiConsult` contract.

The Main-Agent interface should remain stable.

---

## 24. Relationship to existing project gates

### Issue #141 — natural installed dogfood

This Query Plane is strongly related to the normal Agent experience but is not evidence that the current 0.1.16 runtime is broken.

The current baseline should still be treated honestly.

However, the owner has explicitly identified Main-Agent Wiki burden as a strategic concern and prefers to advance this architecture promptly. That makes a separate near-term product slice reasonable rather than waiting indefinitely for an accidental large-Wiki failure.

### Issue #160 / E023

This review is **not** reopening G2 persistence or G3 identity/routing.

E023 contributes safety/mechanism lessons:

- planner/selector complexity is not automatically better;
- a selection bottleneck can discard authority preserved elsewhere;
- truth-by-luck is a critical trust failure;
- simple evidence budget can outperform extra planning complexity;
- composition must preserve authority type and missing bridges.

The Query Plane remains query-time/ephemeral and therefore fits the current E023 posture.

### Cross-workspace Personal Wiki / federation review

This is a separate axis.

Federation answers:

> **Which authorized Wiki stores can be searched?**

The Query Plane answers:

> **Who performs the search/read/reasoning work and what reaches the Main Agent?**

They compose naturally but should be implemented independently.

### Autonomy philosophy

The proposal is strongly aligned with the existing principle:

> The human controls admission and epistemic commitment; the LLM controls routine retrieval, organization, compilation, and maintenance inside granted authority.

A Wiki Query Plane makes that delegation more literal: routine retrieval mechanics become Wiki-owned rather than Main-Agent-owned.

---

## 25. What this review does NOT recommend

Do not interpret this review as support for:

- giving Luna unrestricted MCP/shell/web access;
- making Luna a canonical writer;
- automatically persisting every query synthesis;
- storing private chain-of-thought;
- replacing RAW/HUMAN authority with Luna summaries;
- treating citations as proof of semantic entailment;
- hard-coding E023 top-6 as the product retrieval policy;
- rerunning frozen E023 cases to tune the Query Plane;
- adding graph/entity/vector infrastructure;
- requiring cross-workspace federation before L0;
- silently using the AI-summary maintenance grant for query reasoning;
- silently falling back to the Main Agent when Luna is unavailable;
- optimizing away Luna reasoning merely to minimize total token count.

---

## 26. Final assessment

The repository is closer to this architecture than it first appears.

It already has:

- an Agent-first ordinary conversation surface;
- deterministic raw/derived/Human memory retrieval;
- verified raw source reads;
- exact Luna invocation;
- prompt/evidence stdin protection;
- citation-handle isolation;
- authority-aware query-time composition research;
- explicit product philosophy that routine retrieval mechanics belong to the LLM.

What is missing is primarily the **boundary**:

> The ordinary Main Agent currently receives the low-level Wiki retrieval products and acts as the librarian.

The recommended next boundary is:

> **LLM Wiki owns a Luna-backed Query Plane and the Main Agent talks to it through a compact `wikiConsult` contract.**

The first implementation should be intentionally modest:

```text
current-store authority
      ↓
strong/simple deterministic retrieval
      ↓
verified terminal context
      ↓
exact Luna composer
      ↓
compact answer + terminal refs + insufficiency
      ↓
Main Agent
```

Only after real use proves the one-shot path inadequate should the internal worker evolve into a bounded iterative evidence-follow librarian.

The main architectural principle is:

> **Let Luna spend the Wiki tokens; protect the Main Agent's context.**

The matching trust principle is:

> **Hide the retrieval process from the Main Agent's context, not the result's provenance from the user/system.**

That combination appears to be a strong near-term product direction for a Wiki that is expected to become large, cross-source, and eventually cross-project.