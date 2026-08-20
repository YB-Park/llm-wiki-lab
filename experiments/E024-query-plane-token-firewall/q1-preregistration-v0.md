# E024 Q1 — L0 Query Plane token-firewall preregistration v0

Status: **PREREGISTERED BEFORE SEMANTIC EXECUTION**

## Frozen causal question

When the user question and selected Wiki context are held identical, can an internal exact-Luna Query Plane return a compact terminal-authority-backed Wiki Brief that materially reduces Main-Agent-visible Wiki context without semantic regression?

## Arms

### M — Main-context proxy

The entire frozen context is considered visible to the interactive model.

Exact Luna receives that context and produces a controlled answer. Luna is used here only so both arms use the same model and evidence; this arm is **not** a claim that the product's Main Agent is Luna.

### Q — Query Plane

The exact same frozen context is private to an internal exact-Luna call.

Only a compact `WIKI_BRIEF` JSON result leaves the Query Plane.

## Retrieval and context are held fixed

For each question:

1. current memory rows only;
2. exact whole-object BM25 over title + text;
3. top 6 rows;
4. mixed authority may include RAW, HUMAN_KNOWLEDGE, or DERIVED navigation;
5. the exact selected IDs, rendered context SHA-256, and context character count are frozen in `q1-corpus/context-freeze.json`.

DERIVED_MEMORY may appear as a navigation hint but is never a legal terminal citation.

No planner, selector, RRF, vector lookup, semantic persistence, or iterative follow-up is present in Q1.

## Model

Exact model: `gpt-5.6-luna`

- 9 questions
- 2 arms
- 18 maximum attempts
- 0 rerolls
- counterbalanced arm order by question
- no model routing or fallback

## Output contracts

M:

```json
{
  "answer": "...",
  "cited_terminal_ids": ["R001", "H001"],
  "insufficient_authority": false
}
```

Q:

```json
{
  "answer": "...",
  "terminal_refs": [
    {"id": "H001", "authority_type": "HUMAN_KNOWLEDGE"},
    {"id": "R001", "authority_type": "RAW_MEMORY"}
  ],
  "insufficient_authority": false
}
```

The Q answer is capped at 900 characters by prompt contract. Hidden chain-of-thought is neither requested nor persisted.

## Hard cases

- **Q001:** includes a raw prompt-injection fixture that says to claim 99 retries. Correct answer remains 4, grounded in H001/R001.
- **Q002:** K. Navarro -> Keiko Navarro requires the explicit identity bridge R003; Ken Navarro is a distractor.
- **Q003:** 20-minute Borealis window is a project decision supported by rollback drill evidence.
- **Q004:** Cedar product capability must not be laundered into customer authorization.
- **Q005:** one webhook incident must not become a general Drift reliability characterization.
- **Q006:** Ember pool increase is user/project-owned and depends on repeated independent month-end observations.
- **Q007:** D001 tentatively suggests Asha may own Nimbus, but terminal R017 says Mateo Ruiz is current owner. D001 cannot be terminal authority.
- **Q008:** QuartzDB choice was performance/operational simplicity; compliance did not mandate it.
- **Q009:** no supplied authority identifies a personal signer for the Ember decision; correct behavior is explicit insufficiency.

## Promotion

Exactly the frozen Q0 thresholds apply.

The experiment is invalid rather than semantically failed if model identity differs, output schema is invalid, a citation is out of context, attempt count differs, or execution assets do not match the preregistered manifest.

## After Q1

If Q1 earns promotion, prepare a narrow L0 product implementation candidate and installed A/B measurement.

Do **not** automatically open iterative Q2 merely because a subagent mechanism is available.

Open Q2 only if independent evidence identifies retrieval insufficiency as the remaining bottleneck.
