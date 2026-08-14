# LLM Wiki Dogfood — VS Code-first shell

This extension is the first-class dogfood interaction surface for the project. It is intentionally a thin VS Code adapter over the architecture-neutral Python core under `dogfood/llm_wiki`.

The core remains authoritative for storage, retrieval, provenance, E013 calibration semantics, and the explicit model-call boundary. The extension does not implement a second knowledge model and does not enable persistent compiled state.

## First run

After installing the VSIX, open a **trusted local workspace** in VS Code and use the Command Palette (`Cmd/Ctrl+Shift+P`):

1. `LLM Wiki: Doctor (Zero Model Calls)` — checks Python, the bundled/local core, `compiled_provider=disabled`, Git raw-store safety, and whether Copilot CLI is available. This makes zero model calls and ingests no evidence.
2. If Doctor reports `Git raw-store safety: UNPROTECTED` or `Realistic evidence dogfood: BLOCKED`, **do not ingest sensitive/realistic evidence yet**. Protect the local wiki directory from that Git repository first.
3. `LLM Wiki: Create Topic` — create the first local topic.
4. Open a file you want to preserve as evidence and run `LLM Wiki: Ingest Active File`.
5. Run `LLM Wiki: Search Topic` and choose a result to open its read-only provenance document.
6. Only when desired, run `LLM Wiki: Ask Luna (Read-only)` and explicitly approve the modal evidence-send warning.

The selected topic appears in the VS Code status bar. Click it to switch topics.

## Current commands

- `LLM Wiki: Doctor (Zero Model Calls)`
- `LLM Wiki: Initialize Workspace`
- `LLM Wiki: Create Topic`
- `LLM Wiki: Select Topic`
- `LLM Wiki: Ingest Active File`
- `LLM Wiki: Ingest Active File as Authoritative Update`
- `LLM Wiki: Search Topic`
- `LLM Wiki: Ask Luna (Read-only)`
- `LLM Wiki: Show Calibration Summary`
- `LLM Wiki: Experimental — Discover Copilot Models (Zero Generation)`

Search results are shown in the `LLM Wiki` Output channel and in a Quick Pick. Selecting a result opens the source through a read-only `llm-wiki-source:` virtual document. Opening that source goes through the core `source show` command so E013 provenance-follow semantics remain core-owned.

## Doctor boundary

Doctor is deliberately local and cheap. It:

- checks whether the configured Python executable can start;
- invokes the real `LLM Wiki: Initialize Workspace` editor-to-core boundary;
- confirms the local config format and `compiled_provider=disabled`;
- classifies the local raw store as `NOT_GIT`, `PROTECTED`, or `UNPROTECTED` using local Git inspection only;
- reports whether Copilot CLI is present;
- reports local raw/search/provenance readiness, realistic evidence dogfood readiness, and Ask Luna readiness separately;
- makes **zero model calls**.

`PROTECTED` means the configured local wiki directory is outside the workspace Git tree or ignored by that Git repository. `UNPROTECTED` means it is inside a Git work tree and not ignored. Version 0.1.3 warns but does **not** silently edit `.gitignore`, `.git/info/exclude`, or other Git metadata.

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

`LLM Wiki: Experimental — Discover Copilot Models (Zero Generation)` is a research/product-adapter probe for issue #24. It is safe to run before using real evidence because it does not send a prompt or evidence and does not call model generation.

It asks the VS Code Language Model API only for Copilot model metadata and opens a JSON report containing:

- `generationCalls: 0`;
- API/selection status;
- model id, family, version, name, vendor, and max-input-token metadata;
- exact match counts for `gpt-5.6-luna`.

The gate is intentionally strict. Only an exact `id === "gpt-5.6-luna"` or `family === "gpt-5.6-luna"` is treated as an exact metadata signal. A name that merely contains “Luna”, a preview label, or another GPT model does not pass. Selection failure does not trigger another model or fallback.

Even if an exact metadata signal appears, this discovery command does **not** switch Ask Luna to the VS Code-native adapter. A separate bounded synthetic generation smoke is required first.

## Run in Extension Development Host

Open the repository root in VS Code, then press `F5` and choose:

`Run LLM Wiki Dogfood Extension`

A second Extension Development Host window opens with the extension loaded. Development mode uses the shared repository Python core rather than a generated bundled copy.

## Installable VSIX dogfood

CI builds `llm-wiki-dogfood.vsix`. The VSIX bundles the shared Python core **at package time** under the extension's `python/` directory. That generated copy is build output, not a second source-of-truth implementation.

The installed extension therefore does not require a checkout of this repository for normal raw/retrieval/provenance use. It still requires Python to be available on the machine.

CI runs the same Extension Host interaction suite twice: once against the repository development extension and once against the unpacked packaged VSIX. The packaged test exercises initialization, Doctor, topic creation, active-file ingest, topic search, and read-only provenance using the bundled core. Separate deterministic tests cover Git safety and the exact-Luna metadata gate. CI does not attempt authenticated Copilot model discovery because that requires the user's real VS Code/Copilot session.

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

This is a first usable editor shell, not a polished Marketplace release. It currently uses Command Palette, Quick Pick, Output, status bar, and virtual documents rather than a dedicated sidebar or chat participant.

Version 0.1.3 detects an unprotected Git raw store but does not yet provide an automatic protection action; any future action must be explicit, local, and reversible.

The VS Code-native LM API adapter remains experimental until exact Luna selection and a bounded synthetic smoke pass. The existing CLI adapter remains authoritative for Ask Luna in the meantime.

Compiled knowledge remains disabled. E013 realistic workload evidence decides whether a compiled provider is ever allowed to advance to shadow/opt-in testing.
