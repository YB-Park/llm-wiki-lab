# Dogfood VSIX releases

This directory is maintained by `.github/workflows/publish-vsix-in-repo.yml` so validated VSIX bytes can be transferred through the Git repository when GitHub Actions artifacts are inconvenient to access.

The publisher runs only after the **VS Code Dogfood** workflow succeeds on a `main` push. It downloads that exact validated artifact, then writes:

- `llm-wiki-dogfood-<version>.vsix` — immutable versioned copy;
- `llm-wiki-dogfood-latest.vsix` — stable convenience path;
- this README with byte size, SHA-256, source run, and source commit.

A successful build for an already-published version must have identical bytes; otherwise publishing fails instead of silently replacing the versioned file.

The first connector-based binary upload attempt was removed because its request payload was truncated before GitHub stored it. Do not use direct connector blob upload for VSIX binaries; let the validated Actions artifact publish itself.
