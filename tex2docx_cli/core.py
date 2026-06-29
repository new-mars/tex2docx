import datetime
import os
import shlex
import subprocess
from pathlib import Path
from shutil import copy2
from urllib.error import URLError
from urllib.request import urlopen

DEFAULT_CSL_URL = "https://raw.githubusercontent.com/jay-dennis/tex2docx/c4bfeb2c02f0abe05037549872d6fffd08ec97f5/pandoc/chicago-author-date.csl"

replace_these_things = {  # use this dictionary to automatically replace things in your .tex to prep it for conversion to .docx; for example,
    r"\some_command_that_needs_to_be_commented_out": r"%\some_command_that_needs_to_be_commented_out"
}


def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list


def tabularize_eqns(fin, eqn_ids, cleanup=True):
    eqn_lookups = ["equation"]
    table_fill = [r"\begin{tabular}{cc}", r" & ", r" \end{tabular}"]
    tempfile = fin.replace(".tex", "_temp.tex")
    fout = fin.replace(".tex", "_temp_out.tex")
    copy2(src=fin, dst=tempfile)
    with open(tempfile, "r") as fp:
        lines = fp.readlines()
    eqn_starts = []
    eqn_ends = []
    eqn_replace = []
    for e in eqn_lookups:
        eqn_start = r"\begin{" + e + r"}"
        eqn_end = r"\end{" + e + r"}"
        starts = [i for i, n in enumerate(lines) if eqn_start in n]
        ends = [i + 1 for i, n in enumerate(lines) if eqn_end in n]
        replace_flag = [False for i in range(len(starts))]
        for i in range(len(starts)):
            temp_eqn_lines = [j for j in range(starts[i], ends[i])]
            replace_eqn = False
            for id in eqn_ids.keys():
                label = r"\label" + id
                for j in temp_eqn_lines:
                    if label in lines[j]:
                        replace_eqn = True
            replace_flag[i] = replace_eqn
        eqn_starts = eqn_starts + starts
        eqn_ends = eqn_ends + ends
        eqn_replace = eqn_replace + replace_flag
    for i in range(len(eqn_starts)):
        if eqn_replace[i]:
            temp_eqn_lines = [j for j in range(eqn_starts[i], eqn_ends[i])]
            lines[temp_eqn_lines[0]] = lines[temp_eqn_lines[0]].replace(lines[temp_eqn_lines[0]], table_fill[0] + "\n" + lines[temp_eqn_lines[0]])
            for id in eqn_ids.keys():
                label = r"\label" + id
                temp_rep = False
                for j in temp_eqn_lines:
                    if label in lines[j]:
                        lines[j] = lines[j].replace(label, "")
                        temp_rep = True
                if temp_rep:
                    lines[temp_eqn_lines[-1]] = lines[temp_eqn_lines[-1]].replace(lines[temp_eqn_lines[-1]], lines[temp_eqn_lines[-1]] + table_fill[1] + label + "\n" + table_fill[2] + "\n")
    with open(fout, "wt") as fo:
        for line in lines:
            fo.write(line)
    if cleanup:
        os.remove(tempfile)
    return fout


def tex_label_ids(fin, id_flags=None, cleanup=True):
    label_flag = r"\label{"
    if id_flags is None:
        id_flags = ["eq:", "eqn:"]
    id_flags = [label_flag + e for e in id_flags]
    tempfile = fin.replace(".tex", "_temp.tex")
    copy2(src=fin, dst=tempfile)
    count = 0
    id_labels = []
    lookups = []
    id_labels2 = []
    ids = {}
    with open(tempfile) as fp:
        for line in fp:
            count += 1
            for a in id_flags:
                if a in line:
                    id_labels = id_labels + [line]
                    lookups = lookups + [a]
    for i in range(len(id_labels)):
        tempe = id_labels[i].split(lookups[i])
        tempe = tempe[1].split(r"}")
        id = tempe[0]
        id_labels2 = id_labels2 + [lookups[i] + id + "}"]
    id_labels2_unique = unique(id_labels2)
    if len(id_labels2) != len(id_labels2_unique):
        print("WARNING: non-unique labels detected")
    id_count = 0
    for e in id_labels2_unique:
        id_count += 1
        id = e.split(r"\label")
        ids[id[1]] = str(id_count)
    print(ids)
    if cleanup:
        os.remove(tempfile)
    return ids


def tex_number_ref(fin, ids, label_prefix=None):
    tempfile = fin.replace(".tex", "_temp.tex")
    if len(ids) > 0:
        with open(fin) as fi:
            with open(tempfile, "wt") as fo:
                for line in fi:
                    for id, n in ids.items():
                        if id in line:
                            if label_prefix is None:
                                line = line.replace(r"\label" + id, "(" + n + ")")
                            else:
                                line = line.replace(r"\label" + id, label_prefix + n)
                            line = line.replace(r"\ref" + id, n)
                            line = line.replace(r"\eqref" + id, "(" + n + ")")
                    fo.write(line)
    else:
        tempfile = fin
    return tempfile


def prep_eqns(fin, id_flags=None, cleanup=True):
    if id_flags is None:
        id_flags = ["eq:", "eqn:"]
    ids = tex_label_ids(fin, id_flags=id_flags, cleanup=cleanup)
    midfile = tabularize_eqns(fin, ids, cleanup=cleanup)
    newfile = tex_number_ref(midfile, ids)
    if cleanup:
        os.remove(midfile)
    return newfile


def prep_figs(fin, id_flags=None, cleanup=True, label_prefix="Figure "):
    if id_flags is None:
        id_flags = ["fig:"]
    ids = tex_label_ids(fin, id_flags=id_flags, cleanup=cleanup)
    newfile = tex_number_ref(fin, ids, label_prefix=label_prefix)
    return newfile


def pref_file(file=None, fileout=None):
    timestamp = str(datetime.datetime.now()).replace(" ", "_").replace(".", "_").replace(":", "-")
    tempfile = "temp_" + timestamp + ".tex"
    if fileout is None:
        fileout = tempfile
    copy2(file, tempfile)
    with open(tempfile, "r") as f:
        Lines = f.readlines()
    count = 0
    for line in Lines:
        for a in replace_these_things.keys():
            if a in line:
                print("Commenting out certain commands...")
                print("Replacing some code...")
                line = line.replace(a, replace_these_things[a])
        Lines[count] = line
        count += 1
    print("Writing temporary file...")
    with open(fileout, "w") as f:
        f.writelines(Lines)
    return fileout


def _default_refs_path():
    refs_path = Path(__file__).resolve().parent / "refs.bib"
    if not refs_path.is_file():
        raise FileNotFoundError("Default refs.bib file is missing from the tex2docx package.")
    return refs_path


def _default_csl_path():
    source_path = Path(__file__).resolve().parent.parent / "pandoc" / "chicago-author-date.csl"
    if source_path.is_file():
        return source_path
    cache_dir = Path.home() / ".tex2docx"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "chicago-author-date.csl"
    if cache_path.is_file():
        return cache_path
    try:
        with urlopen(DEFAULT_CSL_URL) as response, cache_path.open("wb") as target:
            target.write(response.read())
    except URLError as exc:
        raise RuntimeError("Unable to download the default Chicago CSL file.") from exc
    return cache_path


def run_pandoc(file_in=None, file_out=None, refs=None, template=None, toc=True, header=None, ref_style=None):
    if file_out is None:
        file_out = file_in.replace(".tex", ".docx")
    refs_path = _default_refs_path() if refs is None else refs
    csl_path = _default_csl_path() if ref_style is None else ref_style
    pandoc_command = ["pandoc", file_in, "--standalone"]
    if header is not None:
        pandoc_command += ["-H", header]
    if template is not None:
        pandoc_command += ["--reference-doc", template]
    if toc:
        pandoc_command += ["--table-of-contents"]
    pandoc_command += ["--filter", "pandoc-xnos", "--bibliography", str(refs_path), "--csl", str(csl_path), "--citeproc", "-o", file_out]
    print("Running pandoc:")
    print(shlex.join([str(part) for part in pandoc_command]))
    subprocess.run(pandoc_command, check=True)


def tex2docx(filein=None, fileout=None, cleanup=False, refs=None, template=None, toc=True, header=None, ref_style=None):
    if fileout is None:
        fileout = filein.replace(".tex", ".docx")
    tempfile1 = prep_eqns(filein, cleanup=cleanup)
    tempfile2 = prep_figs(tempfile1, cleanup=cleanup)
    tempfile3 = prep_figs(tempfile2, id_flags=["tab:"], cleanup=cleanup, label_prefix="Table ")
    tempfile4 = pref_file(file=tempfile3)
    run_pandoc(file_in=tempfile4, file_out=fileout, refs=refs, template=template, toc=toc, header=header, ref_style=ref_style)
    if cleanup:
        print("Removing temporary files...")
        tempfiles = [tempfile1, tempfile2, tempfile3, tempfile4]
        for f in tempfiles:
            if os.path.isfile(f):
                os.remove(f)
    return None
