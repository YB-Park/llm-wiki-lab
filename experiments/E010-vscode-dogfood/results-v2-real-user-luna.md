# E010 real-user Luna dogfood — result v2

Status: **MIXED BUT SUBSTANTIVELY USEFUL / NOT CUSTOMER READY**  
Date: 2026-08-15 KST

This result asks a stricter question than deterministic self-repo retrieval: **what happens when the actual project is used as an LLM Wiki and the pinned real model must answer from retrieved evidence?**

The evaluation used the real raw-first Wiki substrate, current-only topic semantics, exact `gpt-5.6-luna` through GitHub Actions Copilot entitlement, the product answer/citation boundary, and `source show` to follow provenance. No company/private evidence was used.

## User-like flows exercised

The repository was ingested into three natural topics. Repo questions deliberately started from cross-topic discovery, as if the user no longer remembered where the evidence had been filed.

Real-model user tasks included:

1. decide whether the product is actually customer-ready;
2. recover why the persistent compiled Wiki remains disabled despite E011/E012;
3. recover why X1 remains non-default and what E015 can/cannot establish;
4. explain fail-closed behavior when canonical manifest state disappears while prior-state evidence survives;
5. apply a correction: false 100 rps note corrected to 120 rps;
6. preserve an unresolved Monday-vs-Tuesday launch dispute.

## What worked

### Customer-readiness reasoning — PASS

The real answer refused to call the current Alpha customer-ready and surfaced missing real-use/product evidence with navigable citations.

### Compiled-Wiki decision recall — PASS

The answer correctly recovered the selective high-reuse E011/E012 result and the need for realistic E013 reuse/update/query-mix evidence before enabling durable compiled state.

### Correction vs change — PASS

With an explicit temporal `correction` relation, Luna answered that the current limit is **120 rps** and that 100 rps was a transcription error rather than a later real-world change. Provenance resolved.

### Unresolved dispute — PASS

With explicit Monday and Tuesday evidence marked disputed, Luna refused to invent a winner and said the Wiki does not establish a trustworthy launch day. Both sides were cited and resolvable.

### Manifest-loss answer — initially failed, then fixed and real-validated

Two independent real calls emitted a non-context `src-...` citation. PR #83 first made this safe by failing closed on non-context citations. PR #87 then removed the namespace collision by exposing only per-context `C1/C2/...` citation handles to the model and deterministically mapping validated handles back to canonical source IDs.

Frozen one-call post-fix retest `31861139058` / artifact `9240602048`: **PASS**.

- answer correctly said surviving raw/provenance indicates prior-state loss and the Wiki must stop/fail closed rather than recreate empty history;
- five canonical citations all resolved;
- final integrity was clean.

## The important diagnosis correction: E015 answer failure was context granularity first

Two W0-backed real answers to the E014/E015 question incorrectly described E015 as if it could establish retrieval quality/default-promotion value.

The first interpretation blamed the model for ignoring explicit negative evidence in E015. That was **too strong and was corrected**.

Zero-model diagnostic `31861868445` / artifact `9240822200` reconstructed the actual rendered context:

- W0 retrieved the correct E015 preregistration object;
- W0's best-paragraph snippet contained the preceding purpose paragraph but omitted the adjacent statements that E015 measures W0/X1 divergence and is **not a quality proof**;
- `source show` later exposed the full source, which caused the earlier evaluator to mistakenly assume the model had seen those omitted paragraphs;
- raising W0 top-k did not repair the within-object excerpt loss;
- X1 on the same 299-file corpus/topic/query rendered context containing both decisive statements.

This matters: **the answer was wrong, but the primary demonstrated failure was Wiki context construction, not a model contradicting a limitation present in its prompt.**

### E015-D1 real-user X1 retest — PASS

Preregistered D1 used exactly one new real Luna call with the same question. W0 current-only discovery still chose the topic; only answer context used X1.

Run `31862013373` / artifact `9240865801`:

- answer rejected default promotion from E014-R1 alone;
- correctly said E015 measures realistic W0/X1 divergence/prevalence;
- explicitly said E015 is **not a quality proof**, cannot establish which mode is correct, and cannot promote X1 by itself;
- five citations resolved;
- integrity clean.

This is the first realistic dogfood case matching the E014-R1 mechanism. It is **one case**, not a global X1 promotion proof.

## E016 verifier detour — stopped after root-cause correction

A structured-answer/verifier experiment was briefly opened under the incorrect assumption that the decisive E015 limitation had been present in the W0 model context.

- structured S1 made one real Luna call, but its context lacked the intended limitation, so the result **does not validly test** whether structured self-checking can preserve a supplied negative constraint;
- verifier V1 explicitly required the literal limitation in context and therefore stopped before `ask_copilot`; **zero verifier calls** were made;
- after W0/X1 context reconstruction and D1 PASS, Issue #86 was stopped as not planned.

Do not use E016 as evidence that a verifier is needed or that a verifier fails. Reopen semantic verification only after a future real failure where the contradictory limitation is demonstrably present in the exact model context.

## Cost discipline

Real Luna calls in this assistant-as-user evaluation sequence:

- initial repo user run: 4;
- post-citation-guard repo rerun: 4;
- isolated correction/dispute completion: 2;
- manifest citation-handle post-fix retest: 1;
- E016 structured S1 detour: 1;
- E015-D1 X1 realistic divergent-case retest: 1;
- E016 verifier V1: **0**.

Total evaluation calls: **13**. No semantic rerolls within a frozen task. A separate one-call transport/authentication smoke is outside this evaluation count.

Calls were narrowed after each finding rather than repeatedly replaying already-observed scenarios.

## Product verdict

The project has now crossed an important evidence boundary:

- it can self-host the full repository;
- real Luna can produce genuinely useful answers from its evidence;
- exact provenance is usable rather than decorative;
- correction/dispute semantics survive through the final model answer;
- the product can fail closed on model citation mistakes;
- a real retrieval/context failure was discovered, isolated, and repaired in one case by the existing X1 candidate.

But the current product still defaults to W0, and we now have a reproducible user question where W0 retrieved the right document yet omitted decisive within-document context. **Do not call the product customer-ready while that known default-path risk has only one quality-labeled X1 repair case.**

Keep W0 as default for now; use natural E015 disagreement to find additional realistic divergent cases. If X1 repeatedly repairs those cases without regressions, then make the next narrow promotion/routing decision. Repeated natural multi-session VS Code use remains required as well.
