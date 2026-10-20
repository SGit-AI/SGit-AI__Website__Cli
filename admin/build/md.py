#!/usr/bin/env python3
"""A small Markdown renderer, copied from pki.sgit.ai (admin/build/md.py, itself from newsroom.sgit.ai), with
the changes this site needed to carry the CLI repository's documents verbatim:

  · code spans are lifted out before any other inline rule runs, so `**kwargs` or `a_b_c` inside backticks
    stays literal (the CLI documents are full of both);
  · table cells split on pipes outside code spans, and `\\|` is a literal pipe, so a command table that
    shows `a | b` keeps its columns;
  · bold may contain italic, and <br> in a table cell (the CLI documents' habit) is a line break;
  · block quotes render their contents as markdown, so a quoted "Revised 2026-10-10" notice that holds a
    numbered list stays a list;
  · fences may be indented (a code block inside a list item), headings go to six levels, and `<https://…>`
    is an autolink.

    from md import render, front_matter
    meta, body = front_matter(text)      # flat front matter: key: value, and key: [a, b] lists
    html = render(body)

Everything is escaped first; only the markup this file makes survives, so a document cannot carry HTML into
a page.
"""
import html
import re

_CODE = re.compile(r"(`+)(.+?)\1")
_INLINE = [
    (re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)"), lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy">'),
    (re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)"), lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>'),
    (re.compile(r"&lt;(https?://[^\s&]+)&gt;"), lambda m: f'<a href="{m.group(1)}">{m.group(1)}</a>'),
    (re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*"), lambda m: f"<b>{m.group(1)}</b>"),
    (re.compile(r"&lt;br\s*/?&gt;"), lambda m: "<br>"),
    (re.compile(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])"), lambda m: f"<i>{m.group(1)}</i>"),
    (re.compile(r"(?<![\w])_([^_\n]+)_(?![\w])"), lambda m: f"<i>{m.group(1)}</i>"),
]


def front_matter(text):
    """Split `---\\nkey: value\\n---` off the top. Values: strings, or [a, b] lists. Returns (meta, body)."""
    meta = {}
    if not text.startswith("---"):
        return meta, text
    end = text.find("\n---", 3)
    if end < 0:
        return meta, text
    for line in text[3:end].strip().splitlines():
        if ":" not in line or line.startswith("#"):
            continue
        k, v = line.split(":", 1)
        v = v.split("  #")[0].strip()
        if v.startswith("[") and v.endswith("]"):
            meta[k.strip()] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        else:
            meta[k.strip()] = v.strip("'\"")
    return meta, text[end + 4:].lstrip("\n")


def inline(s):
    codes = []

    def lift(m):
        codes.append(f"<code>{html.escape(m.group(2).strip(), quote=False)}</code>")
        return f"\x00{len(codes) - 1}\x00"
    s = _CODE.sub(lift, s)
    s = html.escape(s, quote=False)
    for rx, fn in _INLINE:
        s = rx.sub(fn, s)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], s)


def split_cells(line):
    """Cells of a table row: split on | outside code spans; \\| is a literal pipe."""
    cells, cur, in_code = [], "", False
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    i = 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur += "|"; i += 2
            continue
        if c == "`":
            in_code = not in_code
        if c == "|" and not in_code:
            cells.append(cur.strip()); cur = ""
        else:
            cur += c
        i += 1
    cells.append(cur.strip())
    return cells


def render(text):
    out, para, lst, code, table, quote = [], [], None, None, None, []

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_list():
        nonlocal lst
        if lst:
            tag, items = lst
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            lst = None

    def flush_table():
        nonlocal table
        if table:
            head, rows = table[0], table[1:]
            thead = ("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead>") if any(head) else ""
            out.append('<div class="tablewrap"><table>' + thead + "<tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>")
            table = None

    def flush_quote():
        if quote:
            out.append("<blockquote>" + render("\n".join(quote)) + "</blockquote>")
            quote.clear()

    def flush_all():
        flush_para(); flush_list(); flush_table(); flush_quote()

    for raw in text.splitlines():
        line = raw.rstrip()
        if code is not None:
            if line.strip().startswith("```") and len(line) - len(line.lstrip()) <= code[2]:
                lang, lines, _ = code
                out.append(f'<pre><code class="lang-{html.escape(lang)}">' + html.escape("\n".join(lines)) + "</code></pre>")
                code = None
            else:
                code[1].append(raw[code[2]:] if raw[:code[2]].strip() == "" else raw)
            continue
        if line.lstrip().startswith("```") and not quote:
            flush_all()
            indent = len(line) - len(line.lstrip())
            code = (line.strip()[3:].strip() or "text", [], indent)
            continue
        if quote and line.startswith(">"):
            quote.append(line[1:][1:] if line[1:2] == " " else line[1:])
            continue
        if not line.strip():
            if quote:
                flush_quote()
            flush_all()
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush_all(); n = len(m.group(1))
            text_ = m.group(2).strip()
            a = re.search(r"\s*\{#([a-z0-9-]+)\}$", text_)
            if a:
                text_ = text_[:a.start()]
            slug = a.group(1) if a else re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text_).lower()).strip("-")[:60]
            out.append(f'<h{n} id="{slug}">{inline(text_)}</h{n}>')
            continue
        if re.match(r"^(-{3,}|\*{3,})$", line):
            flush_all(); out.append("<hr>")
            continue
        if line.startswith("|"):
            cells = split_cells(line)
            if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c) and any(cells):
                continue
            flush_para(); flush_list(); flush_quote()
            table = (table or []) + [cells]
            continue
        if line.startswith(">"):
            flush_para(); flush_list(); flush_table()
            quote.append(line[1:][1:] if line[1:2] == " " else line[1:])
            continue
        m = re.match(r"^\s*[-*+]\s+(.*)$", line)
        if m:
            flush_para(); flush_table(); flush_quote()
            if lst and lst[0] == "ul":
                lst[1].append(m.group(1))
            else:
                flush_list(); lst = ("ul", [m.group(1)])
            continue
        m = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if m:
            flush_para(); flush_table(); flush_quote()
            if lst and lst[0] == "ol":
                lst[1].append(m.group(1))
            else:
                flush_list(); lst = ("ol", [m.group(1)])
            continue
        if lst and line.startswith("  "):
            lst[1][-1] += " " + line.strip()
            continue
        flush_list(); flush_table(); flush_quote()
        para.append(line.strip())
    if code is not None:
        lang, lines, _ = code
        out.append(f'<pre><code class="lang-{html.escape(lang)}">' + html.escape("\n".join(lines)) + "</code></pre>")
    flush_all()
    return "\n".join(out)
