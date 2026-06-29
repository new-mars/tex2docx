# tex2docx Global CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make this repository installable as a global Windows-first Python CLI so users can run `tex2docx input.tex` after installation.

**Architecture:** Keep the conversion logic in a small importable core module, add an argparse-based `main()` entry point in the top-level compatibility module, and publish it through a `console_scripts` entry point named `tex2docx`. Packaging stays lightweight: Python handles installation and command wiring, while Pandoc and pandoc-xnos remain external runtime dependencies. The default Chicago CSL is resolved from the source tree when available and otherwise downloaded/cached on first use.

**Tech Stack:** Python standard library, setuptools via `pyproject.toml`, pytest for unit tests, Pandoc + pandoc-xnos at runtime.

---

### Task 1: Add installable package metadata and CLI entry point

**Files:**
- Create: `pyproject.toml`
- Create: `tex2docx_cli/__init__.py`
- Create: `tex2docx_cli/core.py`
- Create: `tex2docx_cli/refs.bib`
- Modify: `tex2docx.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
from tex2docx import build_arg_parser


def test_parser_accepts_input_output_and_toc_flag():
    parser = build_arg_parser()
    args = parser.parse_args(["input.tex", "-o", "out.docx", "--no-toc"])
    assert args.filein == "input.tex"
    assert args.fileout == "out.docx"
    assert args.toc is False
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_cli.py -q`
Expected: fail because `build_arg_parser` does not exist yet.

- [ ] **Step 3: Write the minimal implementation**

```python
import argparse


def build_arg_parser():
    parser = argparse.ArgumentParser(prog="tex2docx")
    parser.add_argument("filein")
    parser.add_argument("-o", "--fileout")
    parser.add_argument("--refs")
    parser.add_argument("--template")
    parser.add_argument("--header")
    parser.add_argument("--ref-style")
    parser.add_argument("--toc", dest="toc", action="store_true", default=True)
    parser.add_argument("--no-toc", dest="toc", action="store_false")
    parser.add_argument("--cleanup", action="store_true")
    return parser


def main(argv=None):
    args = build_arg_parser().parse_args(argv)
    tex2docx(
        filein=args.filein,
        fileout=args.fileout,
        refs=args.refs,
        template=args.template,
        toc=args.toc,
        header=args.header,
        ref_style=args.ref_style,
        cleanup=args.cleanup,
    )
    return 0
```

Implement the conversion helpers in `tex2docx_cli/core.py`, and have the root `tex2docx.py` module import/re-export them so existing imports still work.

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_cli.py -q`
Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml tex2docx.py tex2docx_cli tests/test_cli.py
git commit -m "feat: add installable tex2docx CLI"
```

### Task 2: Document installation and runtime prerequisites

**Files:**
- Modify: `readme.md`

- [ ] **Step 1: Add install instructions**

Add this section to `readme.md`:

    ## Installation

    ```bash
    pip install .
    tex2docx --help
    ```

    For a user-local global install, `pipx install .` also works.

    ## Runtime requirements

    - Pandoc must be installed and available on PATH.
    - The `pandoc-xnos` filter must be installed and discoverable by Pandoc.
    - If the default Chicago CSL file is not available from the source tree, the CLI downloads and caches it on first use.

- [ ] **Step 2: Verify the README renders cleanly**

Run: no command needed; just confirm the markdown blocks are balanced and the install commands match the new CLI.

- [ ] **Step 3: Commit**

```bash
git add readme.md
git commit -m "docs: add CLI installation instructions"
```

### Task 3: Smoke-test the CLI wiring

**Files:**
- Modify: `tex2docx.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Add a command-wiring test**

```python
import tex2docx


def test_main_forwards_arguments(monkeypatch):
    captured = {}

    def fake_tex2docx(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(tex2docx, "tex2docx", fake_tex2docx)
    rc = tex2docx.main(["input.tex", "-o", "out.docx", "--no-toc"])
    assert rc == 0
    assert captured["filein"] == "input.tex"
    assert captured["fileout"] == "out.docx"
    assert captured["toc"] is False
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_cli.py -q`
Expected: fail until `main()` exists and forwards parsed args.

- [ ] **Step 3: Implement the wiring**

Keep `main()` thin and return `0` after successful conversion. Preserve the existing `__main__` behavior by calling `raise SystemExit(main())`.

- [ ] **Step 4: Run the test and the help command**

Run:

```bash
pytest tests/test_cli.py -q
python -m tex2docx --help
```

Expected: tests pass; help shows `tex2docx` usage.

- [ ] **Step 5: Commit**

```bash
git add tex2docx.py tests/test_cli.py
git commit -m "test: cover tex2docx CLI wiring"
```
