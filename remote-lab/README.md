# Remote research lab

Purpose: run synthetic/public `llm-wiki-lab` experiments on GitHub Actions using GitHub Copilot CLI with the model pinned to `gpt-5.6-luna`.

## Boundary

- No corporate source material, credentials, logs, paths, or proprietary prompts.
- `GITHUB_TOKEN` authentication only for the default lab path; no long-lived PAT is required.
- Workflow permissions are least-privilege: repository contents are read-only plus `copilot-requests: write` for Copilot requests.
- The runner rejects any model other than `gpt-5.6-luna`.
- Each request carries a per-response AI-credit cap and the lab has a hard repository-side maximum.
- Raw synthetic responses and OTel stay in short-lived Actions artifacts; normal logs print only a sanitized handoff.
- OTel message-content capture is disabled.
- Copilot tools and built-in MCPs are disabled for the initial text-in/text-out lab path.

## Trigger

Updating `remote-lab/request.json` triggers `.github/workflows/remote-lab.yml` on the default branch. `workflow_dispatch` is also available for manual testing.

The first supported request kind is `smoke`. It performs exactly one fictional transport/authentication call and expects a fixed ASCII signal. New experiment kinds must add their own frozen validation and budget rules before use.

## Cost discipline

Do not reduce a scientifically required sample just to save credits. Instead prefer deterministic preprocessing, duplicate-prompt reuse, model-call-free validation, preflight before scored runs, and reuse of existing failed artifacts where methodologically valid.

A new high-volume experiment should first estimate expected calls/tokens and compare them with the remaining Copilot allowance. Do not silently escalate to another model or increase the credit guard.
