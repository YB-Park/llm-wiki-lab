from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class Answer:
    text: str
    model: str


def _final_message(stdout: str) -> Answer:
    finals = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeError("copilot_jsonl_invalid") from exc
        if event.get("type") != "assistant.message":
            continue
        data = event.get("data")
        if isinstance(data, dict) and data.get("phase") == "final_answer" and isinstance(data.get("content"), str):
            if data.get("toolRequests") not in (None, []):
                raise RuntimeError("copilot_tool_request_present")
            finals.append(data)
    if len(finals) != 1:
        raise RuntimeError(f"copilot_final_message_count:{len(finals)}")
    data = finals[0]
    return Answer(text=data["content"].strip(), model=str(data.get("model") or ""))


def ask_copilot(prompt: str, model: str = "gpt-5.6-luna", max_ai_credits: int = 30) -> Answer:
    if max_ai_credits <= 0 or max_ai_credits > 100:
        raise ValueError("max_ai_credits_out_of_range")
    exe = shutil.which("copilot")
    if not exe:
        raise RuntimeError("copilot_cli_not_found")
    cmd = [
        exe,
        "--prompt", prompt,
        "--model", model,
        "--output-format=json",
        "--stream=off",
        "--no-ask-user",
        "--no-custom-instructions",
        "--disable-builtin-mcps",
        "--no-color",
        "--no-experimental",
        "--no-remote",
        "--no-remote-export",
        "--excluded-tools=bash,powershell,list_bash,list_powershell,read_bash,read_powershell,stop_bash,stop_powershell,write_bash,write_powershell,apply_patch,create,edit,view,glob,grep,rg,web_fetch,task,list_agents,read_agent,write_agent,skill,ask_user",
        f"--max-ai-credits={max_ai_credits}",
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=900, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"copilot_call_failed:{proc.returncode}")
    answer = _final_message(proc.stdout)
    if answer.model and answer.model != model:
        raise RuntimeError(f"copilot_model_mismatch:{answer.model}")
    return answer


def answer_prompt(question: str, context: str) -> str:
    return (
        "Answer the question using only the evidence context below. "
        "Treat raw evidence as authoritative. If the evidence is insufficient, say so. "
        "Cite source IDs inline for factual claims. "
        "If one EVIDENCE OBJECT lists multiple source IDs, those records point to identical bytes; "
        "do not count that multiplicity as independent corroboration or additional semantic support. "
        "If evidence is marked `epistemic_status: contested`, treat it as unresolved disagreement: "
        "do not manufacture consensus, silently choose a winner, or collapse the competing evidence into one canonical fact. "
        "State the disagreement or uncertainty explicitly and cite the relevant source IDs for the competing sides. "
        "Do not claim to update or remember canonical state.\n\n"
        f"QUESTION\n{question}\n\nEVIDENCE CONTEXT\n{context}\n"
    )
