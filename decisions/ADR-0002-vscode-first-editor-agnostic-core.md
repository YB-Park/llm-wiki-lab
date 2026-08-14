# ADR-0002 — VS Code-first product surface with editor-agnostic core

Status: **accepted**

Date: 2026-08-14

## Context

The project is intended to become a personal LLM Wiki used primarily inside an existing developer workflow. The concrete first target is VS Code together with Git/GitHub, GitHub Copilot, and local Markdown/code files.

Early dogfood work used a Python CLI because it is easy to test, automate, instrument, and keep architecture-neutral. That CLI is useful substrate, but allowing it to become the de facto product UX would drift away from the intended workflow and make realistic workload calibration less representative of the eventual system.

At the same time, binding storage, retrieval, provenance, temporal semantics, calibration, or maintenance rules directly to VS Code APIs would make the trustworthy core harder to test and unnecessarily constrain future expansion.

## Alternatives considered

### A. CLI-first product

Keep the Python CLI as the primary user experience and optionally add editor integrations later.

Pros:
- minimal implementation work;
- highly scriptable;
- straightforward testing.

Cons:
- repeated terminal/context switching;
- poor fit with the intended developer workflow;
- dogfood observations would measure a workflow we do not intend to ship as primary;
- source navigation and provenance inspection are less natural.

### B. VS Code-only monolith

Move core wiki semantics into a VS Code extension and treat the extension as the system.

Pros:
- direct access to editor APIs;
- one implementation surface.

Cons:
- couples epistemic/storage semantics to one UI runtime;
- weakens headless testing and reproducibility;
- makes later non-VS-Code surfaces unnecessarily expensive;
- risks duplicating research logic inside UI code.

### C. VS Code-first adapter over an editor-agnostic core

Keep the trustworthy core independent of the editor, while making VS Code the first-class product and dogfood interaction surface.

Pros:
- matches intended usage;
- preserves deterministic/headless testing;
- supports VS Code-native source navigation and interaction;
- allows later surfaces without rewriting knowledge semantics;
- keeps research and product-interface concerns separable.

Cons:
- requires an adapter boundary and two layers;
- packaging the core with a future extension requires deliberate productization work.

## Decision

Adopt **Alternative C**.

The project is **VS Code-first, not VS Code-only**.

1. VS Code is the primary product and dogfood interaction target.
2. Storage, raw authority, retrieval, provenance, temporal semantics, E013 calibration semantics, and later maintenance rules should remain editor-agnostic where practical.
3. CLI/Python surfaces are substrate, tests, automation hooks, and fallbacks; a terminal-only workflow is not the intended finished UX.
4. Product-facing dogfood work should preferentially expose VS Code commands, editor/source navigation, Quick Pick or equivalent selection, status/context surfaces, and Copilot-assisted answering.
5. VS Code adapters must not silently weaken model-call consent, provenance, raw-authority, or canonical-mutation rules defined by the core.
6. The extension layer must not independently enable a durable compiled provider before the relevant evidence gates authorize it.
7. Later expansion to other editors, web interfaces, or services is allowed without changing this decision, provided the trustworthy core remains shared rather than forked.

## Evidence / rationale

The target environment was already stated in the project charter as VS Code + Git/GitHub + GitHub Copilot + Markdown-first local files. E011/E012 also reinforced that product value depends not only on model quality but on retrieval/provenance interaction and repeated-use economics. E013 specifically requires realistic dogfood observations, so the observation surface should resemble the intended product workflow rather than a convenient research-only CLI.

This ADR does **not** decide whether persistent compilation should be enabled. It only fixes the interaction/product boundary.

## Expected failure modes

- The VS Code adapter grows business/epistemic logic that diverges from the core.
- The CLI remains easier than the extension and silently becomes the real product again.
- Packaging constraints tempt duplication of the Python core in JavaScript/TypeScript.
- VS Code UX convenience bypasses explicit model-call consent or provenance navigation.
- Editor-specific features are mistaken for evidence about the knowledge architecture.

Mitigation: keep core-owned tests, adapter boundary tests, and explicit product-vs-architecture separation in issues and PRs.

## Re-evaluation triggers

Revisit this ADR if:

- realistic users overwhelmingly work outside VS Code;
- VS Code extension constraints prevent required trustworthy behavior;
- a shared service/runtime becomes necessary for reasons demonstrated by experiments or deployment constraints;
- the editor-agnostic boundary creates materially higher reliability or maintenance risk than a single-runtime design.

A future change should supersede this ADR rather than silently editing away the VS Code-first decision.
