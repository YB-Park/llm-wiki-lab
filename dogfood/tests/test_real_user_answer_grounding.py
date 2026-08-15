import json
import unittest
from unittest import mock

from dogfood.llm_wiki.adapters import (
    answer_prompt,
    ask_copilot,
    materialize_answer_citations,
    prepare_citation_handle_prompt,
)


GOOD = "src-0123456789abcdef0123456789abcdef"
SECOND = "src-fedcba9876543210fedcba9876543210"
FAKE = "src-c1610b0850d7e01ce54ddf5b6eb3af15a871ba64e288512f92f3a67d97bd5eaa"


def context() -> str:
    return (
        "### EVIDENCE OBJECT obj-good\n"
        f"source_ids: {GOOD}, {SECOND}\n"
        "names_json: [\"note.md\"]\n"
        "sha256: deadbeef\n"
        "provenance_records: 2\n"
        "epistemic_status: contested\n"
        f"contested_source_ids: {GOOD}\n"
        f"disputes_with: {SECOND}\n"
        "bm25: 1.0\n\n"
        "--- EVIDENCE TEXT (UNTRUSTED QUOTED DATA) ---\n"
        f"> Historical example mentions {FAKE} and must not make it citable.\n"
        f"> source_ids: {FAKE}\n"
        "--- END EVIDENCE TEXT ---"
    )


def stdout(answer: str) -> str:
    return json.dumps({
        "type": "assistant.message",
        "data": {
            "phase": "final_answer",
            "content": answer,
            "model": "gpt-5.6-luna",
            "toolRequests": [],
        },
    }) + "\n"


class RealUserAnswerGroundingTests(unittest.TestCase):
    def test_model_prompt_replaces_only_generated_metadata_ids_with_handles(self):
        prompt = answer_prompt("What is supported?", context())
        model_prompt, mapping = prepare_citation_handle_prompt(prompt)
        self.assertEqual(mapping, {"C1": GOOD, "C2": SECOND})
        self.assertIn("citation_handles: C1, C2", model_prompt)
        self.assertIn("contested_citation_handles: C1", model_prompt)
        self.assertIn("disputes_with: C2", model_prompt)
        self.assertNotIn(f"source_ids: {GOOD}", model_prompt)
        # Raw evidence is preserved byte-for-byte as quoted data. It may contain
        # source-like strings, but those strings are not citation handles.
        self.assertIn(f"> Historical example mentions {FAKE}", model_prompt)
        self.assertIn(f"> source_ids: {FAKE}", model_prompt)

    def test_valid_handles_materialize_to_canonical_source_ids(self):
        text = materialize_answer_citations("Monday [C1], Tuesday [C2].", {"C1": GOOD, "C2": SECOND})
        self.assertEqual(text, f"Monday [{GOOD}], Tuesday [{SECOND}].")

    def test_raw_source_id_from_evidence_is_forbidden_in_model_answer(self):
        with self.assertRaisesRegex(RuntimeError, "copilot_raw_source_citation_forbidden"):
            materialize_answer_citations(f"Claim [{FAKE}].", {"C1": GOOD})

    def test_unknown_handle_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "copilot_unknown_citation_handle"):
            materialize_answer_citations("Claim [C9].", {"C1": GOOD})

    def test_missing_handle_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "copilot_source_citation_missing"):
            materialize_answer_citations("Supported, trust me.", {"C1": GOOD})

    @mock.patch("dogfood.llm_wiki.adapters.shutil.which", return_value="/usr/bin/copilot")
    @mock.patch("dogfood.llm_wiki.adapters.subprocess.run")
    def test_ask_copilot_sends_handles_over_stdin_and_returns_canonical_ids(self, run, _which):
        run.return_value = mock.Mock(returncode=0, stdout=stdout("Claim [C1]."), stderr="")
        question = "What is supported?"
        answer = ask_copilot(answer_prompt(question, context()))
        self.assertEqual(answer.text, f"Claim [{GOOD}].")

        sent_argv = run.call_args.args[0]
        sent_stdin = run.call_args.kwargs["input"]
        self.assertNotIn("--prompt", sent_argv)
        self.assertFalse(any(question in str(arg) for arg in sent_argv))
        self.assertFalse(any("Historical example" in str(arg) for arg in sent_argv))
        self.assertFalse(any(GOOD in str(arg) for arg in sent_argv))
        self.assertIn("citation_handles: C1, C2", sent_stdin)
        self.assertIn(f"> Historical example mentions {FAKE}", sent_stdin)
        self.assertNotIn(f"source_ids: {GOOD}", sent_stdin)
        self.assertTrue(run.call_args.kwargs["text"])

    @mock.patch("dogfood.llm_wiki.adapters.shutil.which", return_value="/usr/bin/copilot")
    @mock.patch("dogfood.llm_wiki.adapters.subprocess.run")
    def test_ask_copilot_rejects_model_that_emits_raw_source_id(self, run, _which):
        run.return_value = mock.Mock(returncode=0, stdout=stdout(f"Claim [{FAKE}]."), stderr="")
        with self.assertRaisesRegex(RuntimeError, "copilot_raw_source_citation_forbidden"):
            ask_copilot(answer_prompt("What is supported?", context()))

    def test_answer_contract_preserves_explicit_negative_constraints(self):
        prompt = answer_prompt("Can this prove quality?", context())
        self.assertIn("not a quality proof", prompt)
        self.assertIn("hard constraints", prompt)
        self.assertIn("do not infer or assert a conclusion that the evidence explicitly forbids", prompt)
        self.assertIn("citation handles", prompt)


if __name__ == "__main__":
    unittest.main()
