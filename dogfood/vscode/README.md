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

For realistic dogfood, use the extension in a workspace that contains only evidence you are permitted to process. The local `.wiki-lab/` directory is ignored by Git.

## Settings

- `llmWiki.pythonExecutable`: default `python3`.
- `llmWiki.corePath`: optional path to the repository/core root. Empty uses the current extension repository in development.
- `llmWiki.workspaceDirectory`: default `.wiki-lab` inside the active workspace.
- `llmWiki.maxAiCredits`: default `30` per explicit Ask Luna call.

## Current limitations

This is a first usable editor shell, not a polished extension release. It currently uses Command Palette, Quick Pick, Output, status bar, and virtual documents rather than a dedicated sidebar or chat participant.

It does not yet package the Python core independently of this repository, so Extension Development Host use assumes access to the repository's `dogfood` package (or an explicitly configured `llmWiki.corePath`). Packaging/installability is a later productization step after the interaction loop is validated.

Compiled knowledge remains disabled. E013 realistic workload evidence decides whether a compiled provider is ever allowed to advance to shadow/opt-in testing.
