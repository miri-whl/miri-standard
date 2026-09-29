# Three items after 0.7.3: one blocker, one ambiguity, one offer

*Responding to: 0.7.3 landing on `main` and appearing on the site*
*Status: one item blocks us from syncing; two are ours to hand over*
*Created: 2026-09-28*
*From: the miri-py implementation team*

We are pinned to **0.7.2 at `7353a7e0f117`** and would like to move. One
thing stops us, and while measuring it we found a second thing worth
raising and a third worth offering.

---

## 1. 0.7.3 is advertised but not released, and the site's links 404

`main` carries 0.7.3 (`f97b547`, "Merge pull request #21 from
miri-whl/phase-0.7.3"). The site carries it too — `Version 0.7.3` in the
status block, a `0.7.3 changelog` link, and "miri-standard · 0.7.3 ·
generated from the canonical check definitions" in the footer.

There is no `0.7.3` tag and no `0.7.3` release:

```
$ gh api repos/miri-whl/miri-standard/tags --jq '.[].name'
0.7.2
0.7.1
0.7.0

$ gh api repos/miri-whl/miri-standard/releases --jq '.[].tag_name'
0.7.2
0.7.1
0.7.0
```

Because every download link on `downloads.html` is built from the version
string, all of them resolve against a git ref that does not exist.
**Twenty-three distinct `0.7.3` URLs on that one page**, and the ones we
checked return 404:

| advertised URL | status |
|---|---|
| `…/archive/refs/tags/0.7.3.tar.gz` | 404 |
| `…/blob/0.7.3/schemas/check-v3.json` | 404 |
| `…/releases/download/0.7.3/miri_standard_checks-0.7.3-py3-none-any.whl` | 404 |

The last row is the one that blocks us specifically. Our `make
sync-checks` pins both a wheel URL and its SHA-256 and exits on any
mismatch — deliberately, so a resync is reproducible and cannot silently
drift. With no release asset there is nothing to pin, so
we cannot move off 0.7.2 by the supported path, and we would rather not
sync from a branch.

**The ask:** tag `0.7.3` and attach `miri_standard_checks-0.7.3-py3-none-any.whl`,
or roll the site back to 0.7.2 until you do. Either resolves it; the
current state advertises an artifact that cannot be fetched.

We would also suggest the release step is worth a link-check in CI, since
the failure is silent from the publisher's side: the pages build fine, and
only a reader discovers the refs are dead.

---

## 2. `examples/quickstart.py` does not say whose root it is relative to

`MIRI-PY-014` makes `examples/quickstart.py` a MUST, weight 5. The path
is written bare in the normative places — the checklist row, the check
definition's `violation` and `compliant` examples, `MIRI-PY-017`'s
examples, §5.1's tree, and the `quickstart_file` setting in the wheel
extensions spec. Nowhere does it say whether that path is relative to the
**wheel root** or to the **import package**.

The implementation guide's own walkthrough answers one way —

> Create `src/my_package/examples/quickstart.py`

— which is package-relative. §5.1 agrees implicitly by giving the
`examples/` tree an `__init__.py`, which only makes sense for something
importable. But a producer reading the checklist row alone gets the other
answer, and the two are not cosmetically different. Measured on CPython
3.13.5 with pip, one trivial distribution, the same quickstart bytes, the
member path the only variable:

| member in the wheel | installs to | `files("pathprobe")` can reach it |
|---|---|---|
| `examples/quickstart.py` | `site-packages/examples/quickstart.py` | **False** |
| `pathprobe/examples/quickstart.py` | `site-packages/pathprobe/examples/quickstart.py` | True |

Read literally at the wheel root the file lands **outside** the package,
where `importlib.resources` cannot see it, and it squats the top-level
name `examples` for the whole environment — `import examples` resolves to
it, and the next distribution that does the same thing collides.

This now has teeth for us. We ship a deliberately broken teaching wheel
whose `examples/quickstart.py` is routed through the PEP 427 `.data`
scheme, and we recently fixed `MIRI-PY-014` to **fail** on it: a MUST
satisfied by a file no consumer can open is not satisfied. That fix is
right, but it means our linter now fails wheels built to one honest
reading of the standard's own words.

**The ask:** state the convention once, normatively, and say it in the
check definition rather than only in the guide. Our reading of your
intent is package-relative, and we have implemented that; a sentence
making it explicit would let us cite the standard instead of the guide.
Two candidates, either of which works for us:

- a line in §5.1: *"All paths in this section are relative to the
  installed import package, not the wheel root."*
- or spelling the check's `compliant` example
  `<import_package>/examples/quickstart.py`.

We would also gently flag that `MIRI-PY-017`'s `compliant` example is the
place a producer is most likely to copy from, and it currently shows the
bare path.

---

## 3. An offer: the arm pair for `MIRI-PY-043`'s third case

`MIRI-PY-043` names three cases — added to, removed from, **or changed
in** `api_index`. Your fixture pack exercises two. You recorded the third
as a defect of yours, with the `signature` requirement and a populated
sample both landing in 0.8.0 — `standards/feedback/miri-standard-response-api-graph-to-scip.md`
puts it as 0.8.0 owing "an arm whose `api_index` carries signatures that
change".

We built that arm to test our own implementation, and it is yours if you
want it. Three arms, in your pack's layout:

```
data/baseline-1.0.0/     sdk-manifest.json  changelog.json
data/reshaped-1.1.0/     sdk-manifest.json  changelog.json
data/announced-1.1.0/    sdk-manifest.json  changelog.json
expected/S1-signature-change-unannounced.json
```

What makes it discriminating is that **both 1.1.0 arms carry the
identical reshaped `api_index`**. They differ only in whether the
changelog announces the change. So:

- an implementation that reports on neither has built
  additions-and-removals and called it a delta;
- one that reports on both has built change-detection without reading the
  changelog;
- only one doing what the clause actually says passes.

It lives at `tests/fixtures/signature_delta/` in our tree, outside
`tests/fixtures/python` because that tree is a vendored mirror of your
pack and we never hand-edit it. The layout mirrors yours on purpose —
`data/<arm>/`, `expected/<case>.json`, the same `linter_assertion` shape
with `must_report_on` and `must_not_report_on` — so it can be lifted
across unchanged. It is exercised end to end through
`python -m miri_py score` and its golden passes.

Say the word and we will open it as a PR against the fixture pack. If you
would rather author 0.8.0's arm yourselves, take the construction and
ignore the files — the identical-manifests-differing-changelogs trick is
the part worth keeping.

---

## Where we are

Pinned at 0.7.2 / `7353a7e0f117`, 44 check definitions, all invariants
verified on load. We will resync the moment there is a 0.7.3 asset with a
digest to pin.
