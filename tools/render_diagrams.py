#!/usr/bin/env python3
"""Render every ```mermaid fence in the specs to a committed SVG.

The markdown is the source of truth: GitHub renders the fence natively, and this script renders the
same source to an SVG the site inlines. Each SVG is keyed by a hash of its diagram source, so editing
a diagram produces a new key and a stale rendering can never be served for edited source.

Renderings are committed. CI therefore needs no browser and the published site makes no external
request — both properties this site already has and neither worth trading for a build-time convenience.
"""
import hashlib
import pathlib
import re
import shutil
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "website/static/diagrams"
THEME = REPO / "website/mermaid-theme.json"
FENCE = re.compile(r"```mermaid\n(.*?)\n```", re.S)

# Only these are scanned; a diagram in a doc the site does not render has nowhere to appear.
SOURCES = sorted(REPO.glob("standards/**/*.md"))


def key_of(src: str) -> str:
    return hashlib.sha256(src.strip().encode()).hexdigest()[:16]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    wanted, rendered, skipped = {}, 0, 0
    for md in SOURCES:
        for src in FENCE.findall(md.read_text()):
            wanted[key_of(src)] = (src, md.relative_to(REPO))

    for k, (src, origin) in sorted(wanted.items()):
        svg = OUT / f"{k}.svg"
        if svg.exists():
            skipped += 1
            continue
        mmd = OUT / f"{k}.mmd"
        mmd.write_text(src + "\n")
        cmd = ["npx", "-y", "@mermaid-js/mermaid-cli@11", "-i", str(mmd), "-o", str(svg),
               "-b", "transparent", "-c", str(THEME)]
        print(f"  rendering {k} from {origin}")
        r = subprocess.run(cmd, capture_output=True, text=True)
        mmd.unlink(missing_ok=True)
        if r.returncode != 0 or not svg.exists():
            print(f"FAILED {k}:\n{r.stdout[-800:]}{r.stderr[-800:]}", file=sys.stderr)
            return 1
        rendered += 1

    stale = [p for p in OUT.glob("*.svg") if p.stem not in wanted]
    for p in stale:
        print(f"  removing stale {p.name}")
        p.unlink()

    print(f"diagrams: {rendered} rendered, {skipped} already current, {len(stale)} stale removed "
          f"({len(wanted)} total)")
    return 0


if __name__ == "__main__":
    if not shutil.which("npx"):
        print("npx not found; mermaid-cli is required to render diagrams", file=sys.stderr)
        sys.exit(1)
    sys.exit(main())
