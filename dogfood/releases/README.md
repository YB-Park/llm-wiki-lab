# Dogfood VSIX releases

This directory keeps a small checked-in copy of the installable VS Code dogfood extension so it can be transferred into environments where GitHub Actions artifacts are inconvenient to access.

## Current

- Versioned: `llm-wiki-dogfood-0.1.11.vsix`
- Stable convenience path: `llm-wiki-dogfood-latest.vsix`
- Extension version: `0.1.11`
- VSIX SHA-256: `615362c52340f704d839530187ce1b0975ed111b2296d2b91e31b903e9bfcc5a`
- Validated GitHub Actions build: run `31994083799`, artifact `9276280377`
- Validated build head: `538c7cd2c641770366fe27350c8debae2a0813bc`

The repository changes after that validated build only affected documentation / completed E021-E022 experiment bookkeeping; `compare 538c7cd2...main` contained no shipped extension product-code changes when this copy was published.

## Install

In VS Code, open Extensions -> `...` -> **Install from VSIX...** and choose either file above. Then open a trusted workspace and run `LLM Wiki: Doctor (Zero Model Calls)` before realistic dogfood.

## Publishing rule

Keep the versioned file immutable. When the dogfood extension version changes, add a new versioned VSIX and repoint `llm-wiki-dogfood-latest.vsix` to the exact same Git blob. Record the validated Actions run and SHA-256 here. Do not use an unvalidated local package as the repo copy.
