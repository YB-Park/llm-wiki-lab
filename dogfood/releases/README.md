# Dogfood VSIX releases

This directory keeps the validated installable VS Code dogfood extension in Git so it can be transferred into environments where GitHub Actions artifacts are inconvenient to access.

## Current

- Versioned: `llm-wiki-dogfood-0.1.16.vsix`
- Stable convenience path: `llm-wiki-dogfood-latest.vsix`
- Extension version: `0.1.16`
- VSIX bytes: `102811`
- VSIX SHA-256: `5fd7c76483b6bef16bff9d3e76fc7b05f05348ae04a2526237843a53891ffb08`
- Validated GitHub Actions build: run `32204779167`
- Validated build head: `e9370663d4763ae0f29d67c572d45c5b80f6c120`

Both VSIX paths contain the exact artifact bytes emitted only after the `VS Code Dogfood` workflow has completed successfully on `main`, including the unpacked packaged Extension Host test.

## Install

In VS Code, open Extensions -> `...` -> **Install from VSIX...** and choose either file above. Open a trusted workspace, protect the configured Wiki directory from that Git repository, and run `LLM Wiki: Initialize Workspace` to explicitly opt that workspace in. `LLM Wiki: Doctor (Zero Model Calls)` is optional diagnostics and never initializes or enables the workspace.

## Publishing rule

This directory is maintained by `.github/workflows/publish-vsix-in-repo.yml`. A versioned file is immutable: if a successful build for the same extension version produces different bytes, publishing fails instead of silently replacing it. Bump the extension version for a new product binary.
