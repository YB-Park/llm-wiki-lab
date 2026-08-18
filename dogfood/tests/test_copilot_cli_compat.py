from __future__ import annotations

import unittest
from subprocess import CompletedProcess

from dogfood.llm_wiki import adapters


class CopilotCliCompatibilityTests(unittest.TestCase):
    def test_removed_optional_flags_are_omitted_when_installed_help_does_not_advertise_them(self):
        help_text = """
        --model=MODEL
        --output-format=FORMAT
        --stream=MODE
        --no-ask-user
        --no-custom-instructions
        --disable-builtin-mcps
        --no-color
        --no-experimental
        --no-remote
        --excluded-tools=TOOLS
        """
        cmd = adapters._copilot_command("copilot", "gpt-5.6-luna", 30, help_text)
        self.assertIn("--no-remote", cmd)
        self.assertFalse(any(arg.startswith("--max-ai-credits") for arg in cmd))
        self.assertNotIn("--no-remote-export", cmd)

    def test_optional_legacy_hardening_flags_are_used_when_installed_help_advertises_them(self):
        help_text = "--no-remote-export\n--max-ai-credits=CREDITS\n"
        cmd = adapters._copilot_command("copilot", "gpt-5.6-luna", 47, help_text)
        self.assertIn("--no-remote-export", cmd)
        self.assertIn("--max-ai-credits=47", cmd)

    def test_cli_argument_failure_is_classified_without_echoing_arbitrary_stderr(self):
        proc = CompletedProcess(
            args=["copilot"],
            returncode=1,
            stdout="",
            stderr="error: unknown option '--removed-flag' plus private local detail",
        )
        self.assertEqual(adapters._copilot_failure_code(proc), "copilot_cli_argument_error")

    def test_model_unavailable_failure_is_classified(self):
        proc = CompletedProcess(
            args=["copilot"],
            returncode=1,
            stdout="",
            stderr="Selected model is not available for this account",
        )
        self.assertEqual(adapters._copilot_failure_code(proc), "copilot_model_unavailable")


if __name__ == "__main__":
    unittest.main()
