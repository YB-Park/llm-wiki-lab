# Dogfood VSIX releases

This directory keeps the validated installable VS Code dogfood extension in Git so it can be transferred into environments where GitHub Actions artifacts are inconvenient to access.

## Current

- Versioned: `llm-wiki-dogfood-0.1.14.vsix`
- Stable convenience path: `llm-wiki-dogfood-latest.vsix`
- Extension version: `0.1.14`
- VSIX bytes: `97090`
- VSIX SHA-256: `7ddce126b8877957928acd901ab1b762d2a9a5673201b6bce32a7426a419216c`
- Validated GitHub Actions build: run `32118652040`
- Validated build head: `5ce0b49bb009b8a13632ced2352ef767c26db68f`

Both VSIX paths contain the exact artifact bytes emitted only after the `VS Code Dogfood` workflow has completed successfully on `main`, including the unpacked packaged Extension Host test.

## Install

In VS Code, open Extensions -> `...` -> **Install from VSIX...** and choose either file above. Open a trusted workspace, protect the configured Wiki directory from that Git repository, and run `LLM Wiki: Initialize Workspace` to explicitly opt that workspace in. `LLM Wiki: Doctor (Zero Model Calls)` is optional diagnostics and never initializes or enables the workspace.

## Publishing rule

This directory is maintained by `.github/workflows/publish-vsix-in-repo.yml`. A versioned file is immutable: if a successful build for the same extension version produces different bytes, publishing fails instead of silently replacing it. Bump the extension version for a new product binary.
