# Dogfood VSIX releases

This directory keeps the validated installable VS Code dogfood extension in Git so it can be transferred into environments where GitHub Actions artifacts are inconvenient to access.

## Current

- Versioned: `llm-wiki-dogfood-0.1.19.vsix`
- Stable convenience path: `llm-wiki-dogfood-latest.vsix`
- Extension version: `0.1.19`
- VSIX bytes: `138132`
- VSIX SHA-256: `5ad0aa719f1b104f1a2378ade2ba71fdf959e472a524f3f3ee39c91f41b5f787`
- Validated GitHub Actions build: run `32461723526`
- Validated build head: `71ba27537e39be36b2ba1709c68bc36c955c967c`

Both VSIX paths contain the exact artifact bytes emitted only after the `VS Code Dogfood` workflow has completed successfully on `main`, including the unpacked packaged Extension Host test.

## Install

In VS Code, open Extensions -> `...` -> **Install from VSIX...** and choose either file above. Open a trusted single-folder workspace, protect the configured project-memory directory from that Git repository, and run `LLM Wiki: Set Up Project Memory` to explicitly enable project memory for that workspace. `LLM Wiki: Check Setup and Health` is optional diagnostics and always makes **0 model calls / 0 state changes**.

AI summaries are optional and remain off until explicitly enabled for the workspace. Normal use is ordinary VS Code Agent conversation; users should not need to learn LLM Wiki tool names.

## Publishing rule

This directory is maintained by `.github/workflows/publish-vsix-in-repo.yml`. A versioned file is immutable: if a successful build for the same extension version produces different bytes, publishing fails instead of silently replacing it. Bump the extension version for a new product binary.
