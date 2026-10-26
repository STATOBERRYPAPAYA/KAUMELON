"""Build the 5-minute revision sheets and the revision hub list.

Each sheet is written once as a fragment in revision/_src/<book>/<NN-slug>.html:

    <!--
    num: 04
    title: Central Tendency I
    sub: One-line description under the title.
    chapter: central1.html          (page name inside the book)
    motto: A one-line closing thought.
    -->
    <section class="card c-green s3"> ... </section>
    ...

Run:  python scripts/build-revision.py
Then: node scripts/revision-pdf.cjs   (makes the A4 PDFs)
"""
import html
import json
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "revision" / "_src"

BOOKS = {
    "agstat": {
        "name": "Textbook of Agricultural Statistics",
        "short": "Agstat",
        "course": "STAT 3202",
        "url": "https://statoberrypapaya.github.io/TextbookofAgstat/",
        "authors": "Gopinath, Adarsh, Hisham &amp; Paul",
        "authors_full": "Dr. Pratheesh P. Gopinath · Dr. Adarsh V.S. · Mohammed Hisham M. · Dr. Manju Mary Paul",
        "chapters": [
            "Basics of statistics", "Official agricultural statistics", "Graphical representation",
            "Central tendency I", "Central tendency II", "Measures of dispersion",
            "Skewness and kurtosis", "Measures of association", "Regression analysis",
            "Probability", "Probability distributions", "Sample survey", "Hypothesis testing",
            "Large sample test", "Small sample tests", "Design of experiments", "Uniformity trials",
            "Analysis of variance", "Multiple comparison tests", "Single factor experiments",
            "Factorial experiments", "Analysis of covariance", "Missing plot analysis",
            "Data transformation",
        ],
    },
}

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · 5-minute revision · KAU Me-LON</title>
<meta name="description" content="Official 5-minute revision of Chapter {n}, {title}, from the {book} (KAU Me-LON).">
<meta name="robots" content="index, follow, max-snippet:160, max-image-preview:large, noai, noimageai">
<meta name="theme-color" content="#173c35">
<link rel="icon" href="../../images/logo.png">
<link rel="stylesheet" href="../assets/katex/katex.min.css">
<link rel="stylesheet" href="../assets/revision.css?v={cssVersion}">
<script defer src="../assets/katex/katex.min.js"></script>
<script defer src="../assets/katex/auto-render.min.js"></script>
<script defer src="../assets/revision.js"></script>
<script src="/assets/melon-tracker.js" defer></script>
</head>
<body>

<nav class="rv-bar" aria-label="Revision">
  <a class="back" href="../../revision.html">← All revision sheets</a>
  <span class="spacer"></span>
  {prev}{next}<a class="rv-btn" href="{slug}.pdf" download="MeLON-{short}-Ch{num}-{fileTitle}-5min.pdf">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12m0 0-5-5m5 5 5-5M5 21h14"/></svg>PDF</a>
</nav>

<main class="sheet">
  <header class="mast">
    <div class="num" aria-hidden="true">{num}</div>
    <div class="kicker">{book} · Chapter {n}</div>
    <h1>{title}</h1>
    <div class="sub">{sub}</div>
    <div class="badge"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2M9 2h6M12 2v3"/></svg>5-minute revision</div>
    <div class="authors">Textbook authors: <b>{authorsFull}</b></div>
    <div class="meta"><span class="chip">{course}</span><span class="chip">KAU Me-LON</span><span class="chip">Chapter revision</span><span class="brand"><img src="../assets/logo-128.png" alt="" width="26" height="26"><span><b>KAU Me-LON</b> · www.agrinoteskau.com · Dept. of Agricultural Statistics, College of Agriculture, Vellayani</span></span></div>
  </header>

  <aside class="quick-start" aria-label="Revision essentials">
    <p class="focus-label">THE IDEA TO KEEP</p><p class="focus-key">{key}</p>
    <div class="focus-pair"><p><b>Remember</b>{remember}</p><p><b>Apply it</b>{apply}</p></div>
    <p class="study-route">1 minute: key idea · 3 minutes: methods &amp; examples · 1 minute: test yourself</p>
  </aside>
  <div class="grid">
{body}
  </div>

  <div class="strip">
    <div class="motto">“{motto}”<small>Learn · Understand · Apply. Read the full chapter for worked examples and exercises.</small></div>
  </div>

  <footer class="sheet-foot">
    <span>Source: <i>{book}</i>, Ch. {n} · {authorsFull} · KAU Me-LON</span>
    <a class="read-full no-print" href="{chapterUrl}">Read the full chapter →</a>
    <span class="rights">© 2026 Department of Agricultural Statistics, College of Agriculture, Vellayani, KAU · www.agrinoteskau.com · Personal study only; no redistribution or AI use.</span>
  </footer>
</main>
</body>
</html>
"""


COMBINED = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{book} · 5-minute revision (all chapters) · KAU Me-LON</title>
<meta name="description" content="All official 5-minute revision sheets for the {book}, in one readable page (KAU Me-LON).">
<meta name="robots" content="index, follow, max-snippet:160, max-image-preview:large, noai, noimageai">
<meta name="theme-color" content="#173c35">
<link rel="icon" href="../../images/logo.png">
<link rel="stylesheet" href="../assets/katex/katex.min.css">
<link rel="stylesheet" href="../assets/revision.css?v={cssVersion}">
<script defer src="../assets/katex/katex.min.js"></script>
<script defer src="../assets/katex/auto-render.min.js"></script>
<script defer src="../assets/revision.js"></script>
<script src="/assets/melon-tracker.js" defer></script>
</head>
<body class="reader" id="top">

<nav class="rv-bar" aria-label="Revision">
  <a class="back" href="../../revision.html">← Revision</a>
  <span class="spacer"></span>
  <label class="jump"><span class="sr-only">Go to chapter</span>
    <select data-jump aria-label="Go to chapter">
      <option value="">Go to chapter…</option>
{options}
    </select>
  </label>
  <a class="rv-btn" href="all-chapters.pdf" download="MeLON-{short}-All-Chapters-5min.pdf">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12m0 0-5-5m5 5 5-5M5 21h14"/></svg>All PDF</a>
</nav>

<header class="reader-head">
  <p class="reader-kicker">KAU Me-LON · Chapter revisions</p>
  <h1>{book}</h1>
  <p>All {count} chapters in one window. Scroll through, or jump to a chapter from the menu.</p>
</header>

{mains}

<a class="to-top no-print" href="#top" aria-label="Back to top">↑</a>
</body>
</html>
"""


def combined(book, mains):
    options = "\n".join(f'      <option value="ch-{n:02d}">{n:02d} · {html.escape(t)}</option>' for n, t, _ in mains)
    return COMBINED.format(cssVersion=hashlib.sha256((ROOT / "revision/assets/revision.css").read_bytes()).hexdigest()[:12], book=book["name"], short=book["short"], count=len(mains), options=options,
                           mains="\n\n".join(m for _, _, m in mains))


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--(.*?)-->\s*(.*)", text, re.S)
    meta = dict(
        (k.strip(), v.strip())
        for k, v in (line.split(":", 1) for line in m.group(1).strip().splitlines() if ":" in line)
    )
    return meta, m.group(2).rstrip()


def build():
    hub_lists = {}
    for book_id, book in BOOKS.items():
        src_dir = SRC / book_id
        out_dir = ROOT / "revision" / book_id
        out_dir.mkdir(parents=True, exist_ok=True)
        sheets = sorted(src_dir.glob("*.html"))
        parsed = [(p.stem, *parse(p)) for p in sheets]
        focus = json.loads((src_dir / "focus.json").read_text(encoding="utf-8"))
        ready = {}
        mains = []
        for i, (slug, meta, body) in enumerate(parsed):
            n = int(meta["num"])
            section_number = iter(range(1, 100))
            body = re.sub(r'(<span class="n">)\d+(</span>)', lambda match: match.group(1) + str(next(section_number)) + match.group(2), body)
            prev = (f'<a class="rv-btn ghost nav-step" href="{parsed[i-1][0]}.html" aria-label="Previous chapter">‹</a>'
                    if i > 0 else "")
            nxt = (f'<a class="rv-btn ghost nav-step" href="{parsed[i+1][0]}.html" aria-label="Next chapter">›</a>'
                   if i < len(parsed) - 1 else "")
            page = TEMPLATE.format(
                cssVersion=hashlib.sha256((ROOT / "revision/assets/revision.css").read_bytes()).hexdigest()[:12],
                **{k: html.escape(v) for k, v in focus[n-1].items()},
                title=meta["title"], n=n, num=f"{n:02d}", sub=meta["sub"], motto=meta["motto"],
                slug=slug, prev=prev, next=nxt, body=body,
                fileTitle=re.sub(r"[^A-Za-z0-9]+", "-", html.unescape(meta["title"])).strip("-"),
                book=book["name"], authorsFull=book["authors_full"], short=book["short"], course=book["course"], authors=book["authors"],
                chapterUrl=book["url"] + meta["chapter"],
            )
            (out_dir / f"{slug}.html").write_text(page, encoding="utf-8")
            ready[n] = slug
            main = page[page.index('<main class="sheet">'):page.index("</main>") + 7]
            mains.append((n, meta["title"], main.replace('<main class="sheet">', f'<main class="sheet" id="ch-{n:02d}">', 1)))
        if mains:
            (out_dir / "all-chapters.html").write_text(combined(book, mains), encoding="utf-8")
        items = []
        for n, title in enumerate(book["chapters"], 1):
            if n in ready:
                items.append(f'    <li class="rv-ch ready"><a href="revision/{book_id}/{ready[n]}.html">'
                             f'<span class="rv-n">{n:02d}</span><span class="rv-t">{title}</span>'
                             f'<span class="rv-go">Read · PDF →</span></a></li>')
            else:
                items.append(f'    <li class="rv-ch soon"><span class="rv-n">{n:02d}</span>'
                             f'<span class="rv-t">{title}</span><span class="rv-go">Coming soon</span></li>')
        hub_lists[book_id] = (len(ready), len(book["chapters"]), "\n".join(items))
        print(f"{book_id}: {len(ready)} of {len(book['chapters'])} sheets built")

    hub = ROOT / "revision.qmd"
    text = hub.read_text(encoding="utf-8")
    for book_id, (done, total, items) in hub_lists.items():
        text = re.sub(rf'(<ol class="rv-list" data-book="{book_id}">\n).*?(\n  </ol>)',
                      lambda m: m.group(1) + items + m.group(2), text, flags=re.S)
        text = re.sub(rf'(<p class="rv-count" data-book="{book_id}">).*?(</p>)',
                      lambda m: m.group(1) + (f"All {total} chapters ready" if done == total
                                              else f"{done} of {total} chapters ready · more added through the semester")
                      + m.group(2), text)
    hub.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    build()
