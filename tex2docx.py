"""Compatibility wrapper and CLI entry point for tex2docx."""

import argparse

from tex2docx_cli.core import (
    pref_file,
    prep_eqns,
    prep_figs,
    run_pandoc,
    tabularize_eqns,
    tex2docx,
    tex_label_ids,
    tex_number_ref,
    unique,
)


def build_arg_parser():
    parser = argparse.ArgumentParser(
        prog="tex2docx",
        description="Convert a LaTeX .tex file to a Word .docx file using pandoc.",
    )
    parser.add_argument("filein", help="Input .tex file")
    parser.add_argument("-o", "--fileout", help="Output .docx file")
    parser.add_argument("--refs", help="Bibliography file passed to pandoc")
    parser.add_argument("--template", help="Reference DOCX template")
    parser.add_argument("--header", help="Pandoc header file")
    parser.add_argument("--ref-style", dest="ref_style", help="CSL reference style")
    toc_group = parser.add_mutually_exclusive_group()
    toc_group.add_argument("--toc", dest="toc", action="store_true", default=True, help="Include a table of contents")
    toc_group.add_argument("--no-toc", dest="toc", action="store_false", help="Do not include a table of contents")
    parser.add_argument("--cleanup", action="store_true", help="Remove temporary files after conversion")
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


if __name__ == "__main__":
    raise SystemExit(main())
