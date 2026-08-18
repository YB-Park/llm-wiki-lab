# Workspace activation test contract

Dogfood 0.1.12 separates extension installation from per-workspace permission.

The VS Code language-model tool contribution remains declared in `package.json`, so extension APIs that enumerate contribution metadata (for example `vscode.lm.tools`) may still list an LLM Wiki tool while its `when` clause is false. That metadata enumeration is **not** the product definition of Agent availability.

The product boundary is enforced in two layers:

1. every contributed LLM Wiki tool uses `when: llmWiki.workspaceEnabled && isWorkspaceTrusted`, which controls whether Agent mode may select/reference the tool for that workspace;
2. the extension registers the five runtime tool implementations only after explicit `LLM Wiki: Initialize Workspace`, and disposes those implementations on `LLM Wiki: Disable Workspace (Keep Data)`.

Therefore the Extension Host lifecycle test uses a valid `vscode.lm.invokeTool('llmWiki_searchMemory', ...)` call as the runtime assertion:

- before explicit initialization: invocation rejects;
- after successful explicit initialization: invocation succeeds;
- after Disable Workspace: invocation rejects again while stored Wiki data remains intact.

`LLM Wiki: Doctor (Zero Model Calls)` is diagnostic-only and must not change any of those states.
