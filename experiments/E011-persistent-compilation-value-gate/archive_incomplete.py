#!/usr/bin/env python3
"""Archive one incomplete E011 infrastructure attempt without deleting it."""

import argparse
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RUN=ROOT/"runs"/"stage-1a-v0"


def main():
    p=argparse.ArgumentParser(); p.add_argument("synthetic_call"); a=p.parse_args(); label=a.synthetic_call
    if label.startswith("build-"): src=RUN/"build"/label[len("build-"):]
    elif label.startswith("answer-"): src=RUN/"answers"/label[len("answer-"):]
    else: raise SystemExit("E011-ARCHIVE unsupported_call_label")
    if not src.exists(): raise SystemExit("E011-ARCHIVE source_not_found")
    root=RUN/"incomplete"; root.mkdir(parents=True,exist_ok=True); n=1
    while (root/f"{label}.attempt{n:02d}").exists(): n+=1
    dst=root/f"{label}.attempt{n:02d}"; shutil.move(str(src),str(dst))
    print(f"E011-ARCHIVE status=OK synthetic_call={label} attempt={n:02d} preserved=yes")


if __name__=="__main__": main()
