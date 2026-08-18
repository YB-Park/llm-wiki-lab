# Dogfood VSIX releases

This directory keeps the validated installable VS Code dogfood extension in Git so it can be transferred into environments where GitHub Actions artifacts are inconvenient to access.

## Current

- Versioned: `llm-wiki-dogfood-0.1.12.vsix`
- Stable convenience path: `llm-wiki-dogfood-latest.vsix`
- Extension version: `0.1.12`
- VSIX bytes: `94341`
- VSIX SHA-256: `1a8cac3520ce55e0cca3ac79dd4447b01c8f146aece436bd87d35324e35d9504`
- Validated GitHub Actions build: run `32103419086`
- Validated build head: `7508eff913226647eb558ed690e0da954673e183`

Both VSIX paths contain the exact artifact bytes emitted only after the `VS Code Dogfood` workflow has completed successfully on `main`, including the unpacked packaged Extension Host test.

## Install

In VS Code, open Extensions -> `...` -> **Install from VSIX...** and choose either file above. Open a trusted workspace, protect the configured Wiki directory from that Git repository, and run `LLM Wiki: Initialize Workspace` to explicitly opt that workspace in. `LLM Wiki: Doctor (Zero Model Calls)` is optional diagnostics and never initializes or enables the workspace.

## Publishing rule

This directory is maintained by `.github/workflows/publish-vsix-in-repo.yml`. A versioned file is immutable: if a successful build for the same extension version produces different bytes, publishing fails instead of silently replacing it. Bump the extension version for a new product binary.
