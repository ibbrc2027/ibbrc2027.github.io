"""Build the two site pages from one source.

Usage (from the repository root):  python src/build.py
Reads   src/site.html (+ the images in src/img/)
Writes  index.html            page for all participants
        speakers-b663ff.html  page for invited speakers (adds the "Tour" tab; never link it from index.html)
Set IBBRC_OUT=<folder>/ to build somewhere else (e.g. a preview).

Markers in src/site.html:
  {{TITLE}} {{BADGE}} {{STORE}} {{NTABS}}   text that differs per page (see EDITIONS below)
  <!--@speakers--> ... <!--/@speakers-->    speakers page only (HTML)
  /*@speakers*/ ... /*/@speakers*/          speakers page only (CSS / JS)
  src="img/<file>"                          embedded as base64, so each page is a single file
"""
import base64, mimetypes, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))          # src/
REPO = os.path.dirname(ROOT)
OUT = os.environ.get("IBBRC_OUT") or REPO

EDITIONS = [
    {"file": "index.html", "speakers": False,
     "TITLE": "IBBRC 2027 Conference", "BADGE": "Preliminary", "STORE": "ibbrc27", "NTABS": "4"},
    {"file": "speakers-b663ff.html", "speakers": True,
     "TITLE": "IBBRC 2027 Speakers Edition", "BADGE": "Speakers edition · Preliminary", "STORE": "ibbrc27s", "NTABS": "5"},
]

BLOCK = re.compile(r"(<!--@speakers-->|/\*@speakers\*/)(.*?)(<!--/@speakers-->|/\*/@speakers\*/)", re.S)


def inline_images(html):
    def data_uri(m):
        path = os.path.join(ROOT, "img", m.group(1))
        mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
        with open(path, "rb") as f:
            return 'src="data:%s;base64,%s"' % (mime, base64.b64encode(f.read()).decode())
    return re.sub(r'src="img/([^"]+)"', data_uri, html)


def build(src, ed):
    html = BLOCK.sub(lambda m: m.group(2) if ed["speakers"] else "", src)
    for key in ("TITLE", "BADGE", "STORE", "NTABS"):
        html = html.replace("{{%s}}" % key, ed[key])
    left = re.findall(r"\{\{[A-Z]+\}\}|@speakers", html)
    if left:
        raise SystemExit("unreplaced markers in %s: %s" % (ed["file"], sorted(set(left))))
    return inline_images(html)


if __name__ == "__main__":
    with open(os.path.join(ROOT, "site.html"), encoding="utf-8") as f:
        src = f.read()
    os.makedirs(OUT, exist_ok=True)
    for ed in EDITIONS:
        out = os.path.join(OUT, ed["file"])
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(build(src, ed))
        print("wrote", os.path.relpath(out, REPO), "(%d KB)" % (os.path.getsize(out) // 1024))
