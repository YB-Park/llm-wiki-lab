# Dogfood VSIX releases

This directory keeps the validated installable VS Code dogfood extension in Git so it can be transferred into environments where GitHub Actions artifacts are inconvenient to access.

## Current

- Versioned: `llm-wiki-dogfood-0.1.11.vsix`
- Stable convenience path: `llm-wiki-dogfood-latest.vsix`
- Extension version: `0.1.11`
- VSIX bytes: `90561`
- VSIX SHA-256: `ddd798f5bd5a2ed1587f23a93dd5fdf612408d66cbd3ef4398dc5e6c5f109abf`
- Validated GitHub Actions build: run `32086377938`
- Validated build head: `7c8259ee7d1eb785bbea5830b413890ee79dfe5f`

Both VSIX paths contain the exact artifact bytes emitted only after the  workflow has completed successfully on , including the unpacked packaged Extension Host test.

## Install

In VS Code, open Extensions -> `...` -> **Install from VSIX...** and choose either file above. Then open a trusted workspace and run `LLM Wiki: Doctor (Zero Model Calls)` before realistic dogfood.

## Publishing rule

This directory is maintained by `.github/workflows/publish-vsix-in-repo.yml`. A versioned file is immutable: if a successful build for the same extension version produces different bytes, publishing fails instead of silently replacing it. Bump the extension version for a new product binary.
