#!/usr/bin/env python3
"""Narrow deterministic JSON envelope decoding for E011."""

import json

FENCE = chr(96) * 3


def loads(text: str):
    s = text.strip()
    try:
        return json.loads(s), None
    except json.JSONDecodeError:
        pass
    if not (s.startswith(FENCE) and s.endswith(FENCE)):
        raise json.JSONDecodeError("not a single JSON fence", s, 0)
    body = s[len(FENCE):-len(FENCE)].strip()
    if body[:4].lower() == "json":
        body = body[4:].lstrip()
    return json.loads(body), "outer_json_fence"
