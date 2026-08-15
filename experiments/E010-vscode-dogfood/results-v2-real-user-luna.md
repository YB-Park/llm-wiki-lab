# E010 real-user Luna dogfood — result v2

Status: **MIXED / NOT CUSTOMER READY**

Date: 2026-08-15 KST

This result answers a different question from the deterministic self-repo retrieval gate: **what happens when the project is actually used as an LLM Wiki and the pinned real model must answer from retrieved evidence?**

The evaluation used the normal raw-first Wiki substrate, current-only topic retrieval, normal read-only `ask --allow-model-call`, exact `gpt-5.6-luna` through GitHub Actions Copilot entitlement, and `source show` to follow model citations. No company/private evidence was used.

## Runs

### User-like repo run v0 — `31860128676`

- whole tracked UTF-8 repository ingested into three natural topics;
- user was treated as having forgotten the topic: four repo questions started with cross-topic discovery, then normal topic-scoped Ask;
- four real Luna calls occurred;
- customer-readiness, compiled-Wiki, and E014/E015 answers were captured;
- manifest-loss answer emitted a non-context `src-...` citation, and the evaluation failed when `source show` proved it was not navigable provenance.

This exposed Issue #81: model output was not post-validated against the exact context citation namespace.

### Grounding fix — PR #83

PR #83 added fail-closed citation validation and strengthened the answer contract. It does not reroll, delete, or silently substitute citations. Any model citation not present in Wiki-generated metadata for that exact Ask is rejected before the answer is returned/displayed.

### User-like repo run v1 — `31860463983`

The same four questions were rerun once under the revised product contract.

- customer-readiness answer remained grounded and useful;
- compiled-Wiki answer remained substantively useful;
- E014/E015 answer **again overclaimed E015**, despite retrieval including the actual E015 preregistration and despite the strengthened negative-constraint prompt;
- manifest-loss answer again fabricated a non-context current-looking `src-...`; this time the product correctly failed closed with `copilot_unknown_source_citation` before displaying the answer.

Thus #81's trust boundary is fixed, but the repeated manifest case is still a usability/reliability problem and is tracked in #85.

The repeated E015 semantic error falsifies the prompt-polish-only hypothesis and motivates the narrow verification candidate in #86.

### Temporal user completion — `31860606549`

To avoid spending four more Luna calls only to reach the two temporal scenarios, a separate two-call completion used the same product Ask path.

#### Correction — manual and automatic PASS

Evidence:
- old note: approved cache limit 100 rps;
- new note: the old note had a transcription error; actually approved limit is 120 rps;
- explicit `correction` relation recorded.

Luna answer:

> The approved cache limit is **120 requests per second**. This is a **correction of an earlier transcription error**, not a later real-world change.

The cited source resolved successfully.

#### Unresolved dispute — manual PASS

Evidence:
- note A says production launch Monday;
- note B says production launch Tuesday;
- explicit unresolved `dispute` relation recorded.

Luna answer:

> The Wiki does not establish a trustworthy production launch day. The evidence is explicitly contested: one note says **Monday**, while another says **Tuesday**.

Both cited sources resolved successfully. The simple automatic keyword gate marked this task false only because it did not include `contested` / `does not establish` among accepted uncertainty phrases; manual review is a PASS. The harness miss must not be misreported as a product failure.

Final integrity audit for the temporal Wiki was clean.

## Manual user verdict by task

| User task | Verdict | Reason |
|---|---|---|
| Are we customer-ready? | **PASS** | Refused the customer-ready claim and identified missing real-use evidence with navigable citations. |
| Why is compiled Wiki disabled? | **PASS** | Correctly recovered the selective high-reuse result and realistic E013-style evidence needed before activation. |
| Why is X1 non-default / what can E015 tell us? | **FAIL** | Correct retrieval, valid citations, but the answer contradicted E015's explicit `not a quality proof` boundary in two independent calls. |
| What happens if canonical manifest is lost while prior-state evidence survives? | **SAFE FAIL** | Two independent calls produced non-context citations. After #83 the unsafe answer is blocked, but the user still gets no useful answer. |
| Correction vs real-world change | **PASS** | Correct current value and relation semantics, navigable provenance. |
| Unresolved dispute | **PASS** | Preserved both sides and refused to invent a winner, with both sources navigable. |

## What this says about the product

### Stronger than the deterministic E010 gate alone suggested

- The Wiki can recover and answer substantial project-decision questions using the real pinned model.
- The cross-topic discovery -> topic-scoped Ask path is usable for forgotten-topic recovery on several realistic questions.
- Exact provenance is not merely stored; successful answers can be followed back to actual evidence records.
- Correction and dispute semantics survive all the way through the model answer in the tested scenarios.
- The fail-closed answer boundary now prevents a fabricated citation from masquerading as provenance.

### Weaker than a customer-ready trust claim requires

- A model can cite valid evidence and still draw a conclusion that the evidence explicitly forbids.
- Prompt strengthening alone did not eliminate the observed E015 semantic failure.
- Asking the model to emit canonical `src-...` IDs directly is brittle when raw evidence legitimately contains many historical/source-like identifiers. Fail-closed validation makes this safe but not reliably useful.
- The assistant-run evaluation used real Wiki operations and real Luna, but the model-backed portion ran through the GitHub Actions/CLI substrate, not an authenticated human clicking through the final VS Code UI. Packaged VSIX behavior is separately covered by Extension Host tests; repeated natural multi-session use in the user's own workspace remains necessary.

## Cost discipline

The two full repo attempts made four real Luna calls each, and the temporal completion made two: **10 real Luna calls total** for this user-like evaluation sequence. Raw OTEL showed exact `gpt-5.6-luna` request/response model metadata and `github.copilot.cost=1.0` per chat span. No semantic rerolls were used inside a task.

The repeated full run was justified by a product contract change (#83). The final temporal scenarios were isolated into two calls specifically to avoid paying for four already-observed questions a third time.

## Customer-readiness consequence

The earlier P1–P5 product blockers remain closed. Real-model access through GitHub Actions is also proven. But this evaluation adds two **observed answer-layer blockers** before a strong customer-ready claim:

1. **#85 — citation transport reliability:** move toward per-context citation handles so source-like strings inside evidence do not repeatedly cause safe-but-useless refusals.
2. **#86 — semantic constraint verification:** because the same E015 forbidden-conclusion error survived a stronger prompt, test the smallest structured/verification mechanism before adopting any verifier stack.

Repeated natural multi-session VS Code use remains required as well.

## Bottom line

The product is no longer just a trustworthy storage/retrieval prototype: several real-Luna user flows are genuinely useful and the temporal/provenance philosophy survives actual answering. But the answer layer has now demonstrated a concrete failure mode that deterministic retrieval metrics could not reveal. **Do not call the current system customer-ready until that answer-layer evidence is addressed and repeated natural use is observed.**
