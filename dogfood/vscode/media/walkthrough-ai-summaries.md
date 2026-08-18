# AI summaries are optional

Local project memory works without AI summaries.

If you enable **AI Summaries**, explicitly saved source content may be sent to GitHub Copilot using the configured maintenance model. These summaries are navigation aids: they never replace the saved source evidence or your confirmed decisions.

## If Copilot CLI is not ready

1. [Install GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli) using the option for your platform.
2. Run `copilot login` in a terminal and complete GitHub sign-in.
3. Run **LLM Wiki: Check Setup and Health** again.

If your Copilot access comes from an organization or enterprise, its policy can disable Copilot CLI even when the executable is installed. LLM Wiki's zero-model health check reports executable presence separately from actual model-call readiness.
