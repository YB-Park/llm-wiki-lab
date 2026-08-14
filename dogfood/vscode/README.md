# LLM Wiki Dogfood — VS Code-first shell

This extension is the first-class dogfood interaction surface for the project. It is intentionally a thin VS Code adapter over the architecture-neutral Python core under `dogfood/llm_wiki`.

The core remains authoritative for storage, retrieval, provenance, E013 calibration semantics, and the explicit model-call boundary. The extension does not implement a second knowledge model and does not enable persistent compiled state.

## First run

After installing the VSIX, open a **trusted local workspace** in VS Code and use the Command Palette (`Cmd/Ctrl+Shift+P`):

1. `LLM Wiki: Doctor (Zero Model Calls)` — checks Python, the bundled/local core, `compiled_provider=disabled`, Git raw-store safety, and whether Copilot CLI is available. This makes zero model calls and ingests no evidence.
2. If Doctor reports `Git raw-store safety: UNPROTECTED` or `Realistic evidence dogfood: BLOCKED`, **do not ingest sensitive/realistic evidence yet**. Protect the local wiki directory from that Git repository first.
3. `LLM Wiki: Create Topic` — create the first local topic.
4. Open a file you want to preserve as evidence and run `LLM Wiki: Ingest Active File`.
5. Run `LLM Wiki: Search Topic`. When that file still exists with exactly the ingested bytes, the result can navigate to the original workspace-relative file; if it moved or changed, LLM Wiki falls back to the immutable read-only evidence snapshot.
6. If you forgot which topic contains something, use `LLM Wiki: Global Search Current Evidence Across Topics` to discover it without treating superseded history as current or manufacturing an E013 visit.
7. Only when desired, run `LLM Wiki: Ask Luna (Read-only)` and explicitly approve the modal evidence-send warning.

The selected topic appears in the VS Code status bar. Click it to switch topics.

Before entrusting valuable knowledge to the local store, read [`../../docs/11-local-backup-restore.md`](../../docs/11-local-backup-restore.md). Alpha integrity checks detect many failures but **detection is not backup**.

## Current commands

- `LLM Wiki: Doctor (Zero Model Calls)`
- `LLM Wiki: Initialize Workspace`
- `LLM Wiki: Create Topic`
- `LLM Wiki: Select Topic`
- `LLM Wiki: Ingest Active File`
- `LLM Wiki: Ingest Active File as Authoritative Update`
- `LLM Wiki: Search Topic`
- `LLM Wiki: Global Search Current Evidence Across Topics`
- `LLM Wiki: Record Correction`
- `LLM Wiki: Change Source Over Time`
- `LLM Wiki: Record Unresolved Dispute`
- `LLM Wiki: Record Feedback`
- `LLM Wiki: Ask Luna (Read-only)`
- `LLM Wiki: Show Calibration Summary`
- `LLM Wiki: Experimental — Discover Copilot Models (Zero Generation)`

## Source navigation boundary

Canonical evidence deliberately stores an immutable content object and opaque evidence revision identity; it does **not** use a workspace path as evidence identity or corroboration.

Version 0.1.4 adds a separate VS Code-local navigation hint after active-file ingest:

- only a workspace-relative path plus evidence SHA is kept in extension workspace state;
- search display can use that relative path to disambiguate repeated basenames such as `README.md`;
- LLM Wiki opens the original workspace file only when its current bytes still hash to the immutable evidence SHA;
- if the file moved, disappeared, or changed, it opens the immutable raw provenance document instead.

This makes navigation convenient without letting a mutable local path rewrite what the evidence actually was.

## Explicit correction / change / disagreement

The Alpha core distinguishes three meanings that should not be inferred automatically:

- **Correction** — the predecessor was wrong and the successor corrects it.
- **Change Source Over Time** — both states may have been correct at different times; the user supplies a timezone-aware effective instant.
- **Unresolved Dispute** — two current evidence revisions disagree and neither is silently chosen as the winner.

Version 0.1.4 exposes these accepted ADR-0005 semantics directly from the Command Palette. The user explicitly chooses the participating current evidence revisions. Raw evidence and history remain preserved.

`Ingest Active File as Authoritative Update` is a separate E013 workload boundary; it is not automatically a correction/change/supersession relation.

## Customer feedback

`LLM Wiki: Record Feedback` writes only the existing local fixed-code E013 outcome/reason values. Ask Luna also offers `Helpful` / `Not helpful` after displaying an answer. No free-text feedback is stored by this path.

This is product evidence, not permission for the LLM to mutate canonical state.

## Doctor boundary

Doctor is deliberately local and cheap. It:

- checks whether the configured Python executable can start;
- invokes the real `LLM Wiki: Initialize Workspace` editor-to-core boundary;
- confirms the local config format and `compiled_provider=disabled`;
- classifies the local raw store as `NOT_GIT`, `PROTECTED`, or `UNPROTECTED` using local Git inspection only;
- audits existing Alpha raw/canonical integrity without repair/reconstruction;
- reports whether Copilot CLI is present;
- reports local readiness and realistic evidence dogfood readiness separately;
- makes **zero model calls**.

`PROTECTED` means the configured local wiki directory is outside the workspace Git tree or ignored by that Git repository. `UNPROTECTED` means it is inside a Git work tree and not ignored. The extension warns but does **not** silently edit `.gitignore`, `.git/info/exclude`, or other Git metadata.

Doctor does not print local paths, usernames, hostnames, environment variables, evidence, prompts, or answers.

## Ask Luna boundary

`Ask Luna` is deliberately explicit:

1. choose/retain a topic;
2. enter a question;
3. optionally tag the E013 query class;
4. approve a modal warning that retrieved evidence will be sent to GitHub Copilot;
5. only then does the extension invoke the core `ask` path with `--allow-model-call`.

The model is pinned to `gpt-5.6-luna`. The answer is displayed in the Output channel and is never written to canonical wiki state. Programmatic command arguments used by local-only runtime tests do **not** provide a model-consent bypass.

The validated production-dogfood Ask adapter remains the Copilot CLI path until the VS Code-native Language Model API spike proves that the exact Luna model can be selected without silent substitution.

## Experimental VS Code-native model discovery

`LLM Wiki: Experimental — Discover Copilot Models (Zero Generation)` is a product-adapter probe for issue #24. It is safe to run before using real evidence because it does not send a prompt or evidence and does not call model generation.

It asks the VS Code Language Model API only for Copilot model metadata and opens a JSON report containing:

- `generationCalls: 0`;
- API/selection status;
- model id, family, version, name, vendor, and max-input-token metadata;
- exact match counts for `gpt-5.6-luna`.

The gate is intentionally strict. Only an exact `id === "gpt-5.6-luna"` or `family === "gpt-5.6-luna"` is treated as an exact metadata signal. A name that merely contains “Luna”, a preview label, or another GPT model does not pass. Selection failure does not trigger another model or fallback.

Even if an exact metadata signal appears, this discovery command does **not** switch Ask Luna to the VS Code-native adapter. A separate bounded synthetic generation smoke is required first.

## Run in Extension Development Host

Open the repository root in VS Code, then press `F5` and choose `Run LLM Wiki Dogfood Extension`.

A second Extension Development Host window opens with the extension loaded. Development mode uses the shared repository Python core rather than a generated bundled copy.

## Installable VSIX dogfood

CI builds `llm-wiki-dogfood.vsix`. The VSIX bundles the shared Python core **at package time** under the extension's `python/` directory. That generated copy is build output, not a second source-of-truth implementation.

The installed extension therefore does not require a checkout of this repository for normal raw/retrieval/provenance use. It still requires Python to be available on the machine.

CI runs the Extension Host interaction suite against both the repository development extension and the unpacked packaged VSIX. Separate deterministic tests cover the product helpers, typed temporal CLI operations, current-only cross-topic discovery, Git safety, and exact-Luna metadata gate. CI does not attempt authenticated Copilot generation because that requires the user's real VS Code/Copilot session.

To install a downloaded VSIX in VS Code, use the Extensions view's `Install from VSIX...` action.

## Runtime prerequisites

- a trusted VS Code workspace;
- Python available as `python3` by default, configurable via `llmWiki.pythonExecutable`;
- GitHub Copilot CLI installed and authenticated only if you choose the current `LLM Wiki: Ask Luna (Read-only)` path;
- an authenticated Copilot-capable VS Code session only if you choose the experimental model-discovery command.

For realistic dogfood, use the extension in a workspace that contains only evidence you are permitted to process and run Doctor first. Treat `UNPROTECTED` as a stop condition for realistic evidence ingestion.

## Settings

- `llmWiki.pythonExecutable`: default `python3`.
- `llmWiki.corePath`: optional override. Empty uses the bundled core in an installed VSIX and the repository core during extension development.
- `llmWiki.workspaceDirectory`: default `.wiki-lab` inside the active workspace.
- `llmWiki.maxAiCredits`: default `30` per explicit Ask Luna call.

## Current limitations

This is an **Alpha/dogfood** product, not a polished Marketplace/customer-ready release. It currently uses Command Palette, Quick Pick, Output, status bar, and virtual documents rather than a dedicated sidebar or chat participant.

The E010 automated P1–P5 blockers are addressed in 0.1.4, but customer readiness still requires two kinds of evidence CI cannot manufacture:

1. the exact-Luna gate in the user's real VS Code/Copilot Pro session;
2. repeated multi-session customer-like use (capture → leave → recall later → provenance → correction/change/dispute/feedback).

The VS Code-native LM API adapter remains experimental until exact Luna selection and a bounded synthetic smoke pass. The existing CLI adapter remains authoritative for Ask Luna in the meantime.

Compiled knowledge remains disabled. E013 realistic workload evidence decides whether a compiled provider is ever allowed to advance to shadow/opt-in testing.
