import tex2docx


def test_parser_accepts_input_output_and_toc_flag():
    parser = tex2docx.build_arg_parser()
    args = parser.parse_args(["input.tex", "-o", "out.docx", "--no-toc"])
    assert args.filein == "input.tex"
    assert args.fileout == "out.docx"
    assert args.toc is False


def test_main_forwards_arguments(monkeypatch):
    captured = {}

    def fake_tex2docx(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(tex2docx, "tex2docx", fake_tex2docx)
    rc = tex2docx.main(["input.tex", "-o", "out.docx", "--no-toc", "--cleanup"])
    assert rc == 0
    assert captured == {
        "filein": "input.tex",
        "fileout": "out.docx",
        "refs": None,
        "template": None,
        "toc": False,
        "header": None,
        "ref_style": None,
        "cleanup": True,
    }
