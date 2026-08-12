# E007 Pre-Scoring Red-Team Review v0

Status: **review completed before the first scored run**
Date: 2026-08-12

## 1. Why this review exists

E007 is the first trust gate, not a race to produce a clean-looking Wiki.

The project mission is to find the minimum architecture and operating discipline that lets useful understanding compound faster than error and maintenance debt. A first experiment that is easy to run but easy to misinterpret would be worse than delaying execution long enough to make its claims precise.

This review therefore tries to falsify the experiment design before the experiment tries to falsify the hypotheses.

No C0–C4 scored result had been inspected when this review was written.

---

## 2. What E007 can legitimately establish

E007 v0 can test, under one controlled representation and one fixed model/runtime, whether progressively stronger maintenance safeguards change long-horizon knowledge integrity and answerability:

- recursive reuse of derived state,
- re-grounding against source evidence,
- transition verification,
- bounded repair,
- behavioral regression checking.

It can also estimate the **incremental lifecycle cost** of those safeguards under the fixed workload.

If the differences are large and repeatable, E007 can justify deeper ablations and later architecture experiments.

---

## 3. What E007 must **not** be used to claim

Even a very strong E007 result does not by itself establish:

- the best Wiki document granularity,
- the best taxonomy or schema,
- whether Markdown is the final representation,
- the best retrieval architecture,
- whether all-source re-grounding scales to a real long-lived Wiki,
- the optimal automation boundary,
- the best model/provider,
- the right deletion/archive policy,
- real-world usefulness on heterogeneous personal data.

Those belong to E001/E002/E003/E004/E005/E006/E009/E010 and realistic-corpus work.

This boundary is important because E007 deliberately holds several architectural variables constant in order to study maintenance behavior.

---

# 4. Red-team findings

## F1 — C1 → C2 is a **bundled intervention**, not a clean single-variable ablation

C1 receives:

- previous derived Wiki,
- only the new source wave,
- permission to rely on prior derived state.

C2 receives:

- previous derived Wiki,
- the new source wave,
- **all raw sources available so far**,
- an explicit authority rule that derived Wiki text is not factual evidence,
- explicit handling rules for disagreement/correction/history,
- selective source-ID requirements.

Therefore a C2 improvement cannot be attributed solely to one mechanism such as "source citations" or "derived state is not evidence."

It may come from:

- replaying old raw evidence,
- the authority instruction,
- explicit temporal/disagreement instructions,
- provenance cues,
- or their interaction.

### Decision for v0

Do **not** add another condition before the screening run. Treat C2 as a practical **source-grounded maintenance package**.

If C1 → C2 is materially large, open a targeted follow-up ablation such as:

- derived state + new wave + all raw sources, but no authority rule,
- authority rule with selective source retrieval instead of full replay,
- provenance requirement ablations.

This avoids condition explosion while preserving causal honesty.

---

## F2 — All-source re-grounding is a safety upper bound, not a production architecture

C2–C4 reread all available raw sources during maintenance. On a six-wave synthetic corpus this is intentionally feasible and gives source-grounded policies a strong chance to succeed.

At real scale, repeatedly reading the full corpus can become roughly quadratic in cumulative maintenance input as the corpus grows.

### Interpretation rule

If C2/C3/C4 succeed, the conclusion is:

> source re-grounding / verification appears valuable enough to justify finding a scalable selective version.

The conclusion is **not**:

> every production Wiki update should reread every raw source.

Selective routing and progressive retrieval remain separate experiments.

---

## F3 — A degenerate "copy almost everything" Wiki could win accuracy

A verifier that heavily penalizes omission may encourage a derived artifact to retain more and more source text.

That can improve exact/delayed query accuracy while destroying the point of a Wiki as a compact, navigable knowledge layer.

Query accuracy alone therefore cannot tell whether C3/C4 improved knowledge maintenance or merely reduced compression.

### Required measurement

For every derived state record at least:

- Wiki bytes/lines,
- available raw-source bytes/lines,
- Wiki/raw size ratio,
- state growth over waves,
- changed-line churn between Wiki versions,
- source-ID coverage as a descriptive metric.

A safeguard that gains accuracy only by asymptotically reproducing the raw corpus should be reported as such.

---

## F4 — C4 regression probes can fail because of answer noise, not state damage

C4 asks the model to answer previously passing deterministic-friendly queries again. A failed answer may mean:

1. the Wiki really lost/corrupted the required information, or
2. the Wiki is still correct but the answer-generation call made a stochastic mistake.

If case 2 triggers a Wiki repair, behavioral protection becomes an **automation false positive** and may mutate a good state unnecessarily.

### Required interpretation

Separate:

- regression-probe failure,
- confirmed state regression,
- regression repair invoked,
- regression repaired,
- false-positive repair where the pre-repair state still contained sufficient evidence,
- repair-induced new damage.

This is not merely evaluator noise. It is directly relevant to the future automation-boundary question: a noisy diagnostic can cause destructive autonomous maintenance.

Do not hide these false positives by reporting only final query accuracy.

---

## F5 — C4 performs another rewrite after the C3 transition process

C4 first obtains a C3 provisional state, then may perform a regression-specific rewrite. That rewrite is source-grounded by prompt, but it is not currently passed through another online transition gate.

This means C4 is not mathematically guaranteed to preserve every C3 property after a regression repair.

### Decision for v0

Keep the bounded C4 policy unchanged for the initial screening run rather than adding an additional repair loop now.

However, post-hoc analysis must explicitly inspect whether regression repairs introduce new:

- coverage loss,
- preservation loss,
- unsupported claims,
- temporal/source attribution errors.

If regression repair frequently causes new integrity failures, a follow-up experiment should compare:

- one-shot repair,
- repair + post-repair verification,
- repair rejection/fallback,
- two-hit regression confirmation before mutation.

This turns the current weakness into a measured automation-policy question rather than silently assuming it is safe.

---

## F6 — Same-model generation and verification can share blind spots

E007 intentionally pins the same model for maintenance, verification, repair, and query answering.

That controls model capability across conditions, but generator and verifier errors may be correlated. A verifier may confidently approve the same misconception produced by the generator.

### Interpretation rule

A positive C3 result means **same-model fresh-pass transition verification helped in this setup**.

It does not prove that verifier independence is unnecessary.

A later replication should test at least one of:

- same model / fresh context,
- different model verifier,
- deterministic verification for exact classes,
- stronger model only for high-risk verification.

---

## F7 — The single Markdown artifact is a controlled representation, not a winning representation

C1–C4 deliberately maintain one Markdown artifact.

This keeps E007 from mixing maintenance-policy effects with page routing, graph structure, split/merge behavior, retrieval indexes, or claim stores.

Therefore W5's "structural pressure" can reveal content-organization stress inside one artifact, but E007 cannot establish real multi-page split/merge policy.

Representation conclusions belong to E001/E005.

---

## F8 — C0 cost superiority/inferiority depends on future query frequency

C0 has essentially no maintenance cost but repeatedly supplies raw context at query time.

Compiled conditions pay maintenance cost so later queries can use smaller derived state.

A fixed six-wave workload gives one point on this trade-off, but the economic winner can flip depending on how often accumulated knowledge is queried.

### Required analysis

Separate:

- maintenance cost,
- answer/query cost,
- verification/repair cost.

Then model lifecycle cost as a function of downstream query count rather than reporting one aggregate only.

At minimum estimate a break-even curve:

```text
compiled_total(q) = maintenance_cost + q * compiled_answer_cost
raw_total(q)      = q * raw_answer_cost
```

The purpose is not to predict one universal query frequency. It is to expose when compilation begins to pay for itself.

---

## F9 — Adapter-level token counts are not equal to experiment-payload size

The corporate VS Code probe counted the synthetic user message at 167 prompt tokens. The Copilot CLI OTel preflight reported 5,801 input tokens for the corresponding infrastructure test.

These measurements have different accounting boundaries and may include runtime/system context or tokenizer differences.

### Required measurement

Alongside OTel token totals, record deterministic payload measures such as:

- explicit prompt UTF-8 bytes/characters,
- response bytes/characters,
- Wiki-state bytes/lines,
- raw evidence bytes/lines.

OTel totals remain the best observation of real adapter consumption; payload measures explain how much of that is caused by our knowledge material versus fixed harness overhead.

`github.copilot.cost` and `github.copilot.aiu` remain opaque until their semantics are verified.

---

## F10 — Small synthetic Corpus C tests mechanism, not external validity

The controlled corpus is valuable because correction, temporal state, disputed claims, aliases, source ownership, and delayed probes have known ground truth.

But 18 fictional sources cannot expose all behavior of:

- long technical documents,
- papers,
- messy personal notes,
- conversational fragments,
- source-quality differences,
- repeated near-duplicates,
- real topic drift,
- months of organic accumulation.

### Interpretation rule

Corpus C can reject unsafe ideas and identify mechanisms worth pursuing.

No production architecture is approved solely because it performs well on C-v0. A later Corpus R or larger holdout corpus is mandatory before strong real-use claims.

---

## F11 — Fixed source order does not test order robustness

All repetitions currently preserve the same source order.

This is good for a first controlled comparison, but LLM attention and summarization may be order-sensitive.

If a headline result is small or unstable, a later robustness block should permute within-wave source order while preserving wave semantics.

Do not add this variable to the first block unless needed.

---

## F12 — Query batches can create inter-question effects

Several questions are answered in one model call. That keeps call count manageable and is symmetric across primary conditions, but one question may influence how the model frames another.

If failures cluster suspiciously by batch or question position, a later check should compare batched versus isolated answering.

This is a secondary robustness issue, not a blocker.

---

## F13 — Query tests cannot cover every silent state loss

A fact can disappear from the Wiki without being caught if no current or delayed query happens to require it.

Therefore query accuracy must be paired with post-hoc state integrity audits against evaluator ground truth, especially for:

- still-valid early facts,
- exact identifiers/numbers,
- unresolved disagreements,
- historical states,
- source ownership.

This is already conceptually present in the scoring protocol and must be operationalized before final E007 conclusions.

---

# 5. Adversarial thought experiments

## T-A — The perfect hoarder

Suppose C3 copies 95% of raw text into its Wiki. It scores almost perfectly and never forgets a delayed fact.

Would we call that a successful Wiki?

No. It demonstrates a trustworthy cache, not necessarily a useful compiled knowledge layer. Compression/state-size metrics prevent this from masquerading as an unqualified win.

## T-B — The noisy smoke alarm

Suppose a C4 regression answer randomly omits one exact value even though the Wiki still contains it. C4 rewrites the Wiki to "fix" the issue and accidentally removes a different valid fact.

A final leaderboard might show one recovered query and hide the unnecessary mutation. We therefore need intervention false-positive and repair-induced-damage analysis.

## T-C — The agreeing hallucination

Generator and verifier both infer the same plausible unsupported relationship from the same source wording. The verifier reports `accept`.

This shows why transition verification cannot be assumed to be independent merely because it is a separate call.

## T-D — The 20-query versus 2,000-query Wiki

A compiled Wiki may lose the cost comparison at 20 downstream questions but win massively at 2,000, or vice versa if maintenance is very expensive.

A single fixed total-cost number is therefore insufficient; query-frequency sensitivity matters.

## T-E — The 100× corpus

Full-source replay works beautifully at 18 sources. At 1,800 sources, every update becomes an enormous reread.

A positive safety result therefore creates a new question — how to retain the safety property under selective retrieval — rather than licensing full replay as production design.

## T-F — The unasked deletion

A valid early fact disappears at W2 but is not queried until months later in realistic use. A small benchmark may never ask it.

This motivates state-level audits and delayed probes rather than relying only on query accuracy.

---

# 6. Changes required before first scored conclusions

The following are measurement/interpretation changes that do **not** change the core C0–C4 maintenance prompts:

1. record Wiki/raw size and version churn,
2. record explicit prompt/response payload size in addition to OTel totals,
3. separate maintenance versus answering cost,
4. include query-frequency break-even analysis,
5. classify verifier/regression interventions by yield and possible false-positive harm,
6. operationalize post-hoc state-integrity audits,
7. report C2 as a bundled source-grounded package, not a one-factor proof,
8. report all-source replay as a controlled upper-bound policy, not production guidance.

---

# 7. Follow-up experiments should be conditional, not automatic

Do not run every conceivable ablation now.

Use E007 results to decide which branch deserves deeper investigation.

### If C1 ≈ C2

Question whether full source re-grounding / authority rules are providing meaningful value under this corpus. Inspect failure classes before adding more provenance machinery.

### If C2 ≫ C1

Run a source-replay/authority/provenance ablation to identify which part of the package produced the gain.

### If C3 ≫ C2

Investigate verifier intervention yield, correlated blind spots, and whether cheaper/selective verification can preserve the gain.

### If C3 ≈ C2 with many verifier calls

Treat the verifier as likely ceremony until stronger evidence appears; do not import it into production merely because verification sounds safe.

### If C4 ≫ C3

Study regression-confirmation policy and human/automatic repair boundaries.

### If C4 causes many false-positive or repair-induced failures

Behavioral checks may still be useful as alerts while automatic repair is too aggressive. This becomes direct input to E009 automation-boundary work.

### If all compiled conditions ≈ or < C0

Do not rationalize the Wiki into existence. Investigate whether compilation provides value only at larger query volume, larger corpus scale, different representation, or realistic workflows.

---

# 8. Stop rule against analysis paralysis

Deep review is useful only if it changes what we measure, what we claim, or what we do next.

For the first E007 block:

- do not add new conditions merely because another interesting question exists,
- document confounds instead of pretending they do not exist,
- add only measurements needed to prevent a false headline conclusion,
- use surprising results to open targeted follow-up experiments.

The project should accumulate **better questions and narrower claims**, not an endlessly expanding first benchmark.

---

# 9. Current recommendation

Proceed with E007 Family N after the measurement additions above.

The experiment remains worth running because it tests a foundational question: whether repeated LLM-maintained derived state can stay useful without quietly compounding omission, unsupported synthesis, temporal corruption, and regression.

But the expected output is not "the winning architecture."

The expected output is a map of:

- which safeguards actually change failure behavior,
- which safeguards are expensive ceremony,
- which new failure modes the safeguards themselves introduce,
- and which uncertainty should be investigated next.
