# LLM Wiki Dogfood — VS Code-first shell

This extension is the first-class dogfood interaction surface for the project. It is intentionally a thin VS Code adapter over the architecture-neutral Python core under `dogfood/llm_wiki`.

The core remains authoritative for storage, retrieval, provenance, E013 calibration semantics, and the explicit model-call boundary. The extension does not implement a second knowledge model and does not enable persistent compiled state.

## Current commands

Open the Command Palette (`Cmd/Ctrl+Shift+P`) and run:

- `LLM Wiki: Initialize Workspace`
- `LLM Wiki: Create Topic`
- `LLM Wiki: Select Topic`
- `LLM Wiki: Ingest Active File`
- `LLM Wiki: Ingest Active File as Authoritative Update`
- `LLM Wiki: Search Topic`
- `LLM Wiki: Ask Luna (Read-only)`
- `LLM Wiki: Show Calibration Summary`

A selected topic appears in the VS Code status bar. Click it to change topics.

Search results are shown in the `LLM Wiki` Output channel and in a Quick Pick. Selecting a result opens the source through a read-only `llm-wiki-source:` virtual document. Opening that source goes through the core `source show` command so E013 provenance-follow semantics remain core-owned.

## Ask Luna boundary

`Ask Luna` is deliberately explicit:

1. choose/retain a topic;
2. enter a question;
3. optionally tag the E013 query class;
4. approve a modal warning that retrieved evidence will be sent to GitHub Copilot;
5. only then does the extension invoke the core `ask` path with `--allow-model-call`.

The model is pinned to `gpt-5.6-luna`. The answer is displayed in the Output channel and is never written to canonical wiki state.

## Run in Extension Development Host

Open the repository root in VS Code, switch to the `dogfood/minimal-shell-v0` branch, then press `F5` and choose:

`Run LLM Wiki Dogfood Extension`

A second Extension Development Host window opens with the extension loaded.

## Installable VSIX dogfood

CI also builds `llm-wiki-dogfood.vsix`. The VSIX bundles the shared Python core **at package time** under the extension's `python/` directory. That generated copy is build output, not a second source-of-truth implementation.

The installed extension therefore does not require a checkout of this repository for normal raw/retrieval/provenance use. It still requires Python to be available on the machine.

To install a downloaded VSIX in VS Code, use the Extensions view's `Install from VSIX...` action.

## Runtime prerequisites

- a trusted VS Code workspace;
- Python available as `python3` by default, configurable via `llmWiki.pythonExecutable`;
- GitHub Copilot CLI installed and authenticated only if you choose `LLM Wiki: Ask Luna (Read-only)`.

For realistic dogfood, use the extension in a workspace that contains only evidence you are permitted to process. The local `.wiki-lab/` directory is ignored by Git when working in this repository; other repositories should also ignore their local wiki directory if Git is enabled.

## Settings

- `llmWiki.pythonExecutable`: default `python3`.
- `llmWiki.corePath`: optional override. Empty uses the bundled core in an installed VSIX and the repository core during extension development.
- `llmWiki.workspaceDirectory`: default `.wiki-lab` inside the active workspace.
- `llmWiki.maxAiCredits`: default `30` per explicit Ask Luna call.

## Current limitations

This is a first usable editor shell, not a polished Marketplace release. It currently uses Command Palette, Quick Pick, Output, status bar, and virtual documents rather than a dedicated sidebar or chat participant.

Compiled knowledge remains disabled. E013 realistic workload evidence decides whether a compiled provider is ever allowed to advance to shadow/opt-in testing.
