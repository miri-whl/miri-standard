#!/usr/bin/env python3
"""Generate the Miri Standard static site.

Thin renderer — everything it emits comes from real artifacts:
  content   standards/<target>/checks/*.yaml (schema: schemas/check-v1.json), docs/origin-story.md
  structure website/site.yaml (nav, targets, assets)
  markup    website/templates/*.html (Jinja2)
  look      website/static/css/tokens/*.css (vendored design tokens) + components.css

Usage: python3 tools/generate_site.py [--out site]
Requires: pyyaml, jinja2
"""
import argparse
import html
import pathlib
import re
import shutil
import sys

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

REPO = pathlib.Path(__file__).resolve().parent.parent
WEB = REPO / "website"
SEV_ORDER = ["LOW", "MINOR", "MEDIUM", "HIGH", "CRITICAL"]
SEV_TONE = {"LOW": "neutral", "MINOR": "neutral", "MEDIUM": "maintenance",
            "HIGH": "deprecated", "CRITICAL": "deprecated"}
TOKEN_ORDER = ["fonts.css", "colors.css", "typography.css", "spacing.css", "surfaces.css", "motion.css"]


def codeish(s):
    """Escape, then render `spans` as <code> — for strings from the check YAMLs."""
    out = html.escape(str(s))
    toks = out.split("`")
    if len(toks) % 2 == 0:
        return Markup(out)
    return Markup("".join(f"<code>{t}</code>" if i % 2 else t for i, t in enumerate(toks)))


# ---- tiny markdown renderer for docs/origin-story.md ----
def md_inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md_to_html(text):
    out = []
    # Pull fenced code blocks out first so blank lines inside them don't split the block.
    for chunk in re.split(r"(```.*?\n.*?\n```)", text, flags=re.S):
        if chunk.startswith("```"):
            body = chunk.split("\n", 1)[1].rsplit("```", 1)[0]
            out.append(f'<div class="codeblock"><pre><code>{html.escape(body.rstrip())}</code></pre></div>')
            continue
        _md_blocks(chunk, out)
    return "\n".join(out)


def _md_blocks(text, out):
    for block in re.split(r"\n\s*\n", text):
        lines = [l for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        first = lines[0]
        if first.startswith("### "):
            out.append(f"<h3>{md_inline(first[4:])}</h3>")
            lines = lines[1:]
        elif first.startswith("## "):
            out.append(f"<h2>{md_inline(first[3:])}</h2>")
            lines = lines[1:]
        elif first.startswith("# "):
            lines = lines[1:]  # document h1 is rendered by the page header
        if not lines:
            continue
        if lines[0].lstrip().startswith(">"):
            quote = " ".join(l.lstrip().lstrip(">").strip() for l in lines)
            out.append(f"<blockquote>{md_inline(quote)}</blockquote>")
        elif re.match(r"^\s*[-*] ", lines[0]):
            items = "".join(f"<li>{md_inline(re.sub(r'^\s*[-*] ', '', l))}</li>" for l in lines)
            out.append(f"<ul>{items}</ul>")
        elif re.match(r"^\s*\d+\. ", lines[0]):
            items = "".join(f"<li>{md_inline(re.sub(r'^\s*\d+\. ', '', l))}</li>" for l in lines)
            out.append(f"<ol>{items}</ol>")
        else:
            out.append(f"<p>{md_inline(' '.join(l.strip() for l in lines))}</p>")


def load_checks(meta):
    files = sorted((REPO / meta["dir"]).glob("*.yaml"))
    return [{"path": f, "doc": yaml.safe_load(f.read_text())} for f in files]


def category_rows(checks):
    """Interleave category header rows with check rows for the index table."""
    rows, last = [], None
    for c in checks:
        d = c["doc"]
        if d["category"] != last:
            last = d["category"]
            pts = sum(x["doc"]["weight"] for x in checks if x["doc"]["category"] == last)
            rows.append({"category": last, "points": pts})
        rows.append({"check": d})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="site")
    args = ap.parse_args()
    out = REPO / args.out

    site = yaml.safe_load((WEB / "site.yaml").read_text())
    env = Environment(loader=FileSystemLoader(WEB / "templates"),
                      autoescape=select_autoescape(["html"]))
    env.filters["codeish"] = codeish

    if out.exists():
        shutil.rmtree(out)
    (out / "checks").mkdir(parents=True)
    (out / "assets").mkdir()

    # stylesheet: vendored tokens in defined order, then the component layer
    css_dir = WEB / "static/css"
    css = "\n".join((css_dir / "tokens" / f).read_text() for f in TOKEN_ORDER)
    css += "\n" + (css_dir / "components.css").read_text()
    (out / "style.css").write_text(css)

    for img in site["assets"]:
        shutil.copy(REPO / "assets/img" / img, out / "assets" / img)

    # Publish the JSON Schemas so their $id URLs (miri-whl.github.io/schemas/…) resolve.
    schemas_out = out / "schemas"
    schemas_out.mkdir()
    for sch in sorted((REPO / "schemas").glob("*.json")):
        shutil.copy(sch, schemas_out / sch.name)

    targets = {}
    for target, meta in site["targets"].items():
        checks = load_checks(meta)
        musts = sum(1 for c in checks if c["doc"]["level"] == "MUST")
        targets[target] = {"meta": meta, "checks": [c["doc"] for c in checks], "musts": musts}

        d = out / "checks" / target
        d.mkdir()
        ctx = {"site": site, "root": "../../", "active": f"checks/{target}/index.html",
               "meta": meta, "sev_tone": SEV_TONE, "sev_order": SEV_ORDER}
        (d / "index.html").write_text(env.get_template("checks_index.html").render(
            **ctx, checks=[c["doc"] for c in checks], musts=musts, rows=category_rows(checks)))
        for i, c in enumerate(checks):
            doc = c["doc"]
            (d / f'{doc["id"]}.html').write_text(env.get_template("check.html").render(
                **ctx, target=target, check=doc,
                sev_num=SEV_ORDER.index(doc["severity"]["default"]) + 1,
                prev_id=checks[i - 1]["doc"]["id"] if i > 0 else None,
                next_id=checks[i + 1]["doc"]["id"] if i + 1 < len(checks) else None))

    (out / "index.html").write_text(env.get_template("home.html").render(
        site=site, root="", active="index.html", targets=targets))
    (out / "origin.html").write_text(env.get_template("origin.html").render(
        site=site, root="", active="origin.html",
        body=md_to_html((REPO / "docs/origin-story.md").read_text())))

    n = sum(len(t["checks"]) for t in targets.values())
    print(f"site generated: {out} — {n} check pages + {len(targets)} indexes + landing + origin")


if __name__ == "__main__":
    sys.exit(main())
