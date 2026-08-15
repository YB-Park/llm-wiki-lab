# LLM Wiki Dogfood — VS Code-first shell

This extension is the first-class dogfood interaction surface for the project. It is intentionally a thin VS Code adapter over the architecture-neutral Python core under `dogfood/llm_wiki`.

The core remains authoritative for storage, retrieval, provenance, E013 calibration semantics, and the explicit model-call boundary. The extension does not implement a second knowledge model and does not enable persistent compiled state.

## First run

After installing the VSIX, open a **trusted local workspace** in VS Code and use the Command Palette (`Cmd/Ctrl+Shift+P`):

1. `LLM Wiki: Doctor (Zero Model Calls)` — checks Python, the bundled/local core, `compiled_provider=disabled`, Git raw-store safety, and whether Copilot CLI is available. This makes zero model calls and ingests no evidence.
2. If Doctor reports `Git raw-store safety: UNPROTECTED` or `Realistic evidence dogfood: BLOCKED`, **do not ingest sensitive/realistic evidence yet**. Protect the local wiki directory from that Git repository first.
3. `LLM Wiki: New Human Knowledge Note` — optionally open a human-owned Markdown draft for what you learned, believe, or decided. Creating the draft does not initialize, ingest, or mutate Wiki state.
4. `LLM Wiki: Create Topic` — create the first local topic.
5. Open a file you want to preserve as evidence and run `LLM Wiki: Ingest Active File`.
6. Run `LLM Wiki: Search Topic`. When that file still exists with exactly the ingested bytes, the result can navigate to the original workspace-relative file; if it moved or changed, LLM Wiki falls back to the immutable read-only evidence snapshot.
7. If you forgot which topic contains something, use `LLM Wiki: Global Search Current Evidence Across Topics` to discover it without treating superseded history as current or manufacturing an E013 visit.
8. Only when desired, run `LLM Wiki: Ask Luna (Read-only)` and explicitly approve the modal evidence-send warning.

The selected topic appears in the VS Code status bar. Click it to switch topics.

Alpha integrity checks detect many failures but **detection is not backup**. Before entrusting valuable knowledge to the local store, use the backup/restore procedure below. The source repository also keeps the longer operating note in `docs/11-local-backup-restore.md`.

## Minimal backup / restore procedure

The local Wiki directory (`.wiki-lab/` by default) contains private raw evidence, canonical history, provenance, topics, and telemetry. Treat any backup as equally sensitive and use only a destination permitted for that data.

**Snapshot:** stop Wiki writes (closing the VS Code workspace is the simplest Alpha procedure), then copy the **entire Wiki directory as one snapshot** to an approved local/offline location. Do not copy only `raw/` or only `manifest.jsonl`, and do not edit JSONL records in the snapshot. On a suitable private POSIX filesystem, for example:

```bash
cp -a .wiki-lab "$HOME/private-backups/my-project-wiki-2026-08-15"
```

Use an organization-approved equivalent on Windows/macOS. Company or sensitive evidence must follow the organization's backup policy; do not move it to a personal cloud account merely for convenience.

**Restore:** stop Wiki writes, keep the current/damaged directory aside, copy a known-good **whole snapshot** back to the configured Wiki directory, then run `LLM Wiki: Doctor (Zero Model Calls)`. **Do not resume normal ingest/update work unless Doctor reports the local Alpha integrity boundary ready.** If Doctor reports missing/torn/corrupt canonical history or missing raw evidence, stop rather than manually reconstructing history from filenames or surviving files.

This is an Alpha operating procedure, not live transactional backup, cloud sync, automatic retention, or multi-writer snapshotting.

## Current commands

- `LLM Wiki: Doctor (Zero Model Calls)`
- `LLM Wiki: Initialize Workspace`
- `LLM Wiki: Create Topic`
- `LLM Wiki: Select Topic`
- `LLM Wiki: New Human Knowledge Note`
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

## Human-owned Knowledge Note boundary

Version 0.1.7 adds the smallest product step from evidence management toward human knowledge compounding: `LLM Wiki: New Human Knowledge Note`.

The command opens an **untitled Markdown document owned by the user** with only four lightweight prompts:

- Current statement
- Why / reasoning
- Supporting evidence
- Open questions

Creating this draft makes **zero model calls**, requires no topic, writes no E013 telemetry, and does not ingest or mutate canonical Wiki state. There is deliberately no `Type`, `Status`, ontology, graph, automatic promotion, or LLM-authored durable truth in v0.

Saving the Markdown file is ordinary user file ownership. If the user later wants that note preserved as Wiki evidence, `LLM Wiki: Ingest Active File` remains a separate explicit action with the normal topic/trust semantics. This separation is intentional: the product can help a human preserve reasoning without quietly granting the LLM mutation authority.

Whether Knowledge Notes deserve a richer first-class schema is a **dogfood question**, not an assumption. The v0 feature succeeds only if users repeatedly create and later recover useful human reasoning.

## Source navigation boundary

Canonical evidence deliberately stores an immutable content object and opaque evidence revision identity; it does **not** use a workspace path as evidence identity or corroboration.

Version 0.1.6 retains the separate VS Code-local navigation hint introduced in 0.1.4:

- only a workspace-relative path plus evidence SHA is kept in extension workspace state;
- search display can use that relative path to disambiguate repeated basenames such as `README.md`;
- LLM Wiki opens the original workspace file only when its current bytes still hash to the immutable evidence SHA;
- if the file moved, disappeared, or changed, it opens the immutable raw provenance document instead.

This makes navigation convenient without letting a mutable local path rewrite what the evidence actually was.

## Global forgotten-topic discovery boundary

Version 0.1.6 includes the E017 real-dogfood correctness fix for `Global Search Current Evidence Across Topics`.

Before 0.1.6, each topic was BM25-scored independently and the resulting raw scores were compared across topics. Those scores are not comparable when topic corpora differ greatly in size. External dogfood reproduced a concrete failure: an Artemis II question over 1,515 Kubernetes docs, 557 CPython docs, and 10 NASA articles selected the CPython topic even though the NASA topic contained the answer.

The current `discover` path therefore:

- gathers only each topic's **current** evidence;
- deduplicates immutable content objects;
- scores the union once in a shared BM25 space;
- attaches topic membership after scoring;
- still excludes superseded history;
- still does not manufacture an E013 query visit;
- does **not** change topic-scoped W0 `search`, `context`, or `ask` behavior.

This is a correctness repair for forgotten-topic routing, not a new global unscoped model-Ask path.

## Explicit correction / change / disagreement

The Alpha core distinguishes three meanings that should not be inferred automatically:

- **Correction** — the predecessor was wrong and the successor corrects it.
- **Change Source Over Time** — both states may have been correct at different times; the user supplies a timezone-aware effective instant.
- **Unresolved Dispute** — two current evidence revisions disagree and neither is silently chosen as the winner.

Version 0.1.6 retains the accepted ADR-0005 commands introduced in 0.1.4. The user explicitly chooses the participating current evidence revisions. Raw evidence and history remain preserved.

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

## 0.1.7 product hardening

Version 0.1.7 also packages two concrete product-security/correctness fixes accepted from external review #101:

- **Copilot prompt transport:** the complete question + retrieved evidence prompt is no longer placed in process argv. The Copilot CLI receives the transformed model prompt through stdin; argv contains only non-evidence control flags/model configuration. Existing citation-handle validation and explicit consent remain unchanged.
- **Single-writer semantic mutations:** ingest, supersession, correction/change, dispute, and exact-provenance bind operations use one private store-level OS advisory writer lock across their read/validate/write boundary. A competing writer waits briefly or fails with `wiki_writer_busy`, then replays current state rather than committing against a stale pre-state. OS lock ownership dies with the process; the lock file is only a private rendezvous point, not canonical state.

The writer lock does **not** claim cross-file transactional atomicity, multi-host locking, live snapshotting, or a database/WAL. Existing append/fsync/torn-tail/fail-closed contracts remain the durability boundary.

## Ask Luna boundary

`Ask Luna` is deliberately explicit:

1. choose/retain a topic;
2. enter a question;
3. optionally tag the E013 query class;
4. approve a modal warning that retrieved evidence will be sent to GitHub Copilot;
5. only then does the extension invoke the core `ask` path with `--allow-model-call`.

The model is pinned to `gpt-5.6-luna`. The answer is displayed in the Output channel and is never written to canonical wiki state. Programmatic command arguments used by local-only runtime tests do **not** provide a model-consent bypass.

Version 0.1.7 retains the answer/provenance hardening introduced in 0.1.5 and sends the transformed prompt to Copilot over stdin rather than process argv. The model no longer has to emit canonical `src-...` identifiers directly. The transient model context exposes short per-call citation handles such as `C1`/`C2`; the core validates those handles and deterministically maps them back to canonical source IDs before the answer is returned. Unknown handles, raw source IDs emitted by the model, or missing citations fail closed instead of masquerading as provenance. These handles are never stored as evidence identity or trust signals.

The validated production-dogfood Ask adapter remains the Copilot CLI path until the VS Code-native Language Model API spike proves that the exact Luna model can be selected without silent substitution.

## Experimental VS Code-native model discovery

`LLM Wiki: Experimental — Discover Copilot Models (Zero Generation)` is a product-adapter probe for issue [#24](https://github.com/YB-Park/llm-wiki-lab/issues/24). It is safe to run before using real evidence because it does not send a prompt or evidence and does not call model generation.

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

CI runs the Extension Host interaction suite against both the repository development extension and the unpacked packaged VSIX. Separate deterministic tests cover the product helpers, typed temporal CLI operations, current-only cross-topic discovery, global uneven-topic discovery scoring, Git safety, and exact-Luna metadata gate. Authenticated generation is evaluated separately in the guarded remote-lab/dogfood workflows so packaging CI does not consume Copilot quota.

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

This is an **Alpha/dogfood** product, not a polished Marketplace/customer-ready release.

Real assistant-as-user dogfood has now covered both the project repository and three unfamiliar external corpora. External E017 testing found and fixed the uneven-topic forgotten-topic discovery bug included in 0.1.6. Version 0.1.7 additionally begins dogfooding human-owned durable reasoning with a deliberately schema-light Knowledge Note draft while packaging the argv→stdin and single-writer hardening from review #101. It also added a second independent real-user case where X1 materially improved W0 context: a CPython reStructuredText question recovered the current POSIX `forkserver` default and 3.14 rationale under X1. That repair remained partial because the exact multithreaded-fork warning lived in another region of the same long `.rst` document and was still omitted.

Customer readiness therefore still requires:

1. repeated natural multi-session use in the user's own VS Code workflow, so E013/E015 evidence arises without manufactured activity;
2. additional natural W0/X1 divergent cases, if they occur, before any default/routing change;
3. recurrence before adding non-Markdown parser/multiple-unit retrieval complexity for the single CPython multi-aspect case;
4. the separate VS Code-native LM API exact-Luna question only if replacing the validated CLI adapter is still valuable.

The UI remains intentionally command-driven for Alpha. Additional visual UX should follow repeated real-use friction rather than speculative polish.

Compiled knowledge remains disabled. E013 realistic workload evidence decides whether a compiled provider is ever allowed to advance to shadow/opt-in testing.
