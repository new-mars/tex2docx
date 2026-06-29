### Installation

Clone this repository, then install it locally:

```bash
pip install .
```

For a user-local global install, `pipx install .` also works.

After installation, run:

```bash
tex2docx Example.tex
```

### Runtime requirements

- Pandoc must be installed and available on PATH.
- The `pandoc-xnos` filter must be installed and discoverable by Pandoc.
- If the default Chicago CSL file is not available from the source tree, the CLI will download and cache it on first use.
