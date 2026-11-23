"""Build the two site pages from one source.

Usage (from the repository root):  python src/build.py
Reads   src/site.html          design and layout
        content/speakers.txt   speakers: name, institution, talk title, abstract
        content/program.txt    program: days, times, sessions, who speaks when
        content/posters.txt    posters: number, title, authors, institution, abstract
        src/img/               logos
Writes  index.html            page for all participants
        speakers-b663ff.html  page for invited speakers (adds the "Tour" tab and items marked
                              "Show: speakers page only"; never link it from index.html)
Set IBBRC_OUT=<folder>/ to build somewhere else (e.g. a preview).
On GitHub this runs by itself after every push (.github/workflows/build.yml).

Markers in src/site.html:
  {{TITLE}} {{BADGE}} {{STORE}} {{NTABS}}   text that differs per page (see EDITIONS below)
  {{SPEAKERS}} {{PROGRAM}} {{POSTERS}}      the content files above
  <!--@speakers--> ... <!--/@speakers-->    speakers page only (HTML)
  /*@speakers*/ ... /*/@speakers*/          speakers page only (CSS / JS)
  src="img/<file>"                          embedded as base64, so each page is a single file

If something in the content files is wrong, the build stops with a message naming the file and line,
and nothing is written (the site stays as it was).
"""
import base64, json, mimetypes, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))          # src/
REPO = os.path.dirname(ROOT)
OUT = os.environ.get("IBBRC_OUT") or REPO
CONTENT = os.path.join(REPO, "content")

EDITIONS = [
    {"file": "index.html", "speakers": False,
     "TITLE": "IBBRC 2027 Conference", "BADGE": "Preliminary", "STORE": "ibbrc27", "NTABS": "4"},
    {"file": "speakers-b663ff.html", "speakers": True,
     "TITLE": "IBBRC 2027 Speakers Edition", "BADGE": "Speakers edition · Preliminary", "STORE": "ibbrc27s", "NTABS": "5"},
]

BLOCK = re.compile(r"(<!--@speakers-->|/\*@speakers\*/)(.*?)(<!--/@speakers-->|/\*/@speakers\*/)", re.S)


class ContentError(SystemExit):
    pass


def failer(path):
    where = "content/" + os.path.basename(path)

    def fail(no, msg):
        at = ", line %d" % no if no else ""
        raise ContentError("\nERROR in %s%s: %s\nNothing was built; the site stays as it was.\n" % (where, at, msg))
    return fail


def read_lines(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read().splitlines()


def tidy_text(text):
    """A blank line starts a new paragraph; single line breaks become spaces."""
    paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", text.strip())]
    return "\n\n".join(p for p in paras if p)


def read_blocks(path, fields, id_pattern, id_hint):
    """Files made of blocks:  == id / Field: value ... / Abstract: (text until the next ==).
    fields: {"Name": "n", ...}; the field mapped to "ab" is the multi-line one and must come last."""
    fail = failer(path)
    lower = {k.lower(): (k, v) for k, v in fields.items()}
    allowed = ", ".join(fields)
    blocks, cur, in_text = {}, None, False
    for no, raw in enumerate(read_lines(path), 1):
        line = raw.rstrip()
        if line.lstrip().startswith("#"):                      # note, not shown
            continue
        if line.startswith("=="):                              # new block
            bid = line[2:].strip()
            if not re.fullmatch(id_pattern, bid):
                fail(no, '"== %s": %s' % (bid, id_hint))
            if bid in blocks:
                fail(no, '"== %s" appears twice' % bid)
            cur, in_text = bid, False
            blocks[bid] = {"_line": no}
            continue
        m = re.match(r"([A-Za-z]+)\s*:(.*)$", line)
        if in_text:                                            # inside the abstract: everything up to the next "=="
            if m and m.group(1).lower() in lower:
                fail(no, '"%s:" after "Abstract:" - Abstract must be the last field' % m.group(1))
            blocks[cur]["ab"] += "\n" + line
            continue
        if not line.strip():
            continue
        if cur is None:
            fail(no, 'text before the first "==" line (start notes with #)')
        if not m:
            fail(no, 'this line is not a field (allowed: %s)' % allowed)
        if m.group(1).lower() not in lower:
            fail(no, 'unknown field "%s:" (allowed: %s)' % (m.group(1), allowed))
        name, k = lower[m.group(1).lower()]
        if k in blocks[cur]:
            fail(no, '"%s:" appears twice in "== %s"' % (name, cur))
        blocks[cur][k] = m.group(2).strip()
        in_text = k == "ab"
    for b in blocks.values():
        if "ab" in b:
            b["ab"] = tidy_text(b["ab"])
    return blocks, fail


def read_speakers(path):
    blocks, fail = read_blocks(path, {"Name": "n", "Institution": "a", "Title": "t", "Abstract": "ab"},
                               r"[a-z][a-z0-9-]*", "the id must be lowercase letters/digits/hyphens, no spaces (e.g. == livneh)")
    out = {}
    for sid, s in blocks.items():
        if not s.get("n"):
            fail(s["_line"], 'speaker "%s" has no "Name:"' % sid)
        rec = {"n": s["n"], "a": s.get("a", "")}
        for k in ("t", "ab"):
            if s.get(k):
                rec[k] = s[k]
        out[sid] = rec
    return out


def read_posters(path):
    blocks, fail = read_blocks(path, {"Title": "t", "Authors": "au", "Institution": "a", "Abstract": "ab"},
                               r"[A-Za-z]?[0-9]+", "the poster number must be digits, or a letter + digits (e.g. == 12 or == A12)")
    out = []
    for no, p in blocks.items():
        if not p.get("t"):
            fail(p["_line"], 'poster %s has no "Title:"' % no)
        if not p.get("au"):
            fail(p["_line"], 'poster %s has no "Authors:"' % no)
        rec = {"no": no, "t": p["t"], "au": p["au"]}
        for k in ("a", "ab"):
            if p.get(k):
                rec[k] = p[k]
        out.append(rec)
    return out


TYPES = {"break": "break", "session": "session", "keynote": "keynote", "event": "plain", "social": "social"}
LINKS = {"posters": "#posters", "tour": "#social"}
SLOT_FIELDS = {"type": "k", "label": "kind", "title": "title", "speakers": "talks", "link": "link", "show": "show"}
TIME = re.compile(r"(\d{1,2}):(\d{2})")


def read_program(path, speakers):
    """content/program.txt -> list of days with slots (each slot may carry "_only": True)."""
    fail = failer(path)
    days, day, slot = [], None, None
    for no, raw in enumerate(read_lines(path), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("==="):
            parts = [p.strip() for p in line[3:].split("|")]
            if len(parts) != 3 or not re.fullmatch(r"\d{4}-\d\d-\d\d", parts[2]):
                fail(no, 'a day line looks like:  === Day 1 | Tue · Feb 23 | 2027-02-23')
            day = {"id": "d%d" % (len(days) + 1), "label": parts[0], "date": parts[1], "iso": parts[2], "slots": [], "_line": no}
            days.append(day)
            slot = None
            continue
        if line.startswith("--"):
            if day is None:
                fail(no, 'an item before the first "=== Day" line')
            t = line[2:].strip().replace(" ", "")
            m = re.fullmatch(r"(\d{1,2}:\d{2})(?:[–—-](\d{1,2}:\d{2}))?", t)
            if not m:
                fail(no, 'the time must look like  -- 10:00–11:40  or  -- 19:00')
            mins = [int(a) * 60 + int(b) for a, b in TIME.findall(t)]
            if any(x >= 24 * 60 for x in mins) or any(int(b) > 59 for _, b in TIME.findall(t)):
                fail(no, 'the time "%s" is not a real time' % t)
            if len(mins) == 2 and mins[1] <= mins[0]:
                fail(no, 'the item ends before it starts (%s)' % t)
            if day["slots"] and mins[0] < day["slots"][-1]["_start"]:
                fail(no, 'items must be in time order within the day (%s comes after %s)' % (t, day["slots"][-1]["t"]))
            norm = "%02d:%02d" % divmod(mins[0], 60) + ("–%02d:%02d" % divmod(mins[1], 60) if len(mins) == 2 else "")
            slot = {"t": norm, "_start": mins[0], "_line": no}
            day["slots"].append(slot)
            continue
        m = re.match(r"([A-Za-z]+)\s*:(.*)$", line)
        if slot is None:
            fail(no, 'text before the first "-- time" line of the day')
        if not m or m.group(1).lower() not in SLOT_FIELDS:
            fail(no, 'unknown line (allowed fields: Type, Label, Title, Speakers, Link, Show)')
        key, val = SLOT_FIELDS[m.group(1).lower()], m.group(2).strip()
        if key in slot:
            fail(no, '"%s:" appears twice in this item' % m.group(1))
        if key == "k":
            if val.lower() not in TYPES:
                fail(no, 'Type must be one of: %s' % ", ".join(TYPES))
            val = TYPES[val.lower()]
        elif key == "talks":
            ids = [x.strip() for x in val.split(",") if x.strip()]
            for x in ids:
                if x.upper() != "TBA" and x not in speakers:
                    fail(no, 'speaker id "%s" is not in content/speakers.txt (write TBA if unknown)' % x)
            val = [None if x.upper() == "TBA" else x for x in ids]
        elif key == "link":
            if val.lower() not in LINKS:
                fail(no, 'Link must be "posters" or "tour"')
            val = LINKS[val.lower()]
        elif key == "show":
            if val.lower() != "speakers page only":
                fail(no, 'Show can only be "speakers page only"')
        slot[key] = val
    if not days:
        fail(0, 'no days found (a day starts with  === Day 1 | Tue · Feb 23 | 2027-02-23)')
    for d in days:
        if not d["slots"]:
            fail(d["_line"], '%s has no items' % d["label"])
        for s in d["slots"]:
            if "k" not in s:
                fail(s["_line"], 'this item has no "Type:"')
            if not s.get("title") and not s.get("kind") and not s.get("talks"):
                fail(s["_line"], 'this item needs a Title, a Label or Speakers')
    return days


def program_for(days, speakers_page):
    out = []
    for d in days:
        slots = []
        for s in d["slots"]:
            if s.get("show") and not speakers_page:
                continue
            slots.append({k: s[k] for k in ("t", "k", "kind", "title", "talks", "link") if k in s and s[k] != ""})
        out.append({"id": d["id"], "label": d["label"], "date": d["date"], "iso": d["iso"], "slots": slots})
    return out


def js(value):
    return json.dumps(value, ensure_ascii=False, indent=0).replace("</", "<\\/")


def inline_images(html):
    def data_uri(m):
        path = os.path.join(ROOT, "img", m.group(1))
        mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
        with open(path, "rb") as f:
            return 'src="data:%s;base64,%s"' % (mime, base64.b64encode(f.read()).decode())
    return re.sub(r'src="img/([^"]+)"', data_uri, html)


def build(src, ed, data):
    html = BLOCK.sub(lambda m: m.group(2) if ed["speakers"] else "", src)
    for key in ("TITLE", "BADGE", "STORE", "NTABS"):
        html = html.replace("{{%s}}" % key, ed[key])
    html = html.replace("{{SPEAKERS}}", js(data["speakers"]))
    html = html.replace("{{PROGRAM}}", js(program_for(data["program"], ed["speakers"])))
    html = html.replace("{{POSTERS}}", js(data["posters"]))
    left = re.findall(r"\{\{[A-Z]+\}\}|@speakers", html)
    if left:
        raise SystemExit("unreplaced markers in %s: %s" % (ed["file"], sorted(set(left))))
    return inline_images(html)


if __name__ == "__main__":
    with open(os.path.join(ROOT, "site.html"), encoding="utf-8") as f:
        src = f.read()
    speakers = read_speakers(os.path.join(CONTENT, "speakers.txt"))
    data = {"speakers": speakers,
            "program": read_program(os.path.join(CONTENT, "program.txt"), speakers),
            "posters": read_posters(os.path.join(CONTENT, "posters.txt"))}
    pages = [(ed, build(src, ed, data)) for ed in EDITIONS]   # build everything before writing anything
    os.makedirs(OUT, exist_ok=True)
    for ed, html in pages:
        out = os.path.join(OUT, ed["file"])
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write(html)
        print("wrote", os.path.relpath(out, REPO), "(%d KB)" % (os.path.getsize(out) // 1024))
    print("%d speakers, %d program days, %d posters" % (len(speakers), len(data["program"]), len(data["posters"])))
