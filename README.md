# IBBRC 2027 conference website

10th International IBBRC Conference, "Brain–Body Plasticity", Feb 23–25 2027, University of Haifa.

- Page for all participants: https://ibbrc2027.github.io/
- Page for invited speakers (do not link it from the public page): https://ibbrc2027.github.io/speakers-b663ff.html

## Updating content

Everything that changes is in three simple text files in `content/`:
- **`content/speakers.txt`**: speakers (name, institution, talk title, abstract)
- **`content/program.txt`**: program (days, times, sessions, who speaks when)
- **`content/posters.txt`**: posters (number, title, authors, abstract)

Edit them on github.com (pencil ✏️ → Commit changes) or with Claude. The site rebuilds by itself in about 2 minutes.

- Guide in Hebrew: [EDITING.md](EDITING.md)
- Instructions for Claude: [CLAUDE.md](CLAUDE.md)

## How it is built

Both pages come from **one source**: `src/site.html` (design and layout) and the files in `content/`.

1. Edit a file in `content/`, or `src/site.html` (logos are in `src/img/`).
2. Commit and push. The GitHub Action `.github/workflows/build.yml` runs `python src/build.py` and commits the
   built `index.html` and `speakers-b663ff.html`. GitHub Pages updates within a minute or two.
   If the build finds a mistake, the Action fails (with the line number) and the live pages stay as they were.

To check locally: `python src/build.py` (Python 3, no packages).
Don't edit `index.html` or `speakers-b663ff.html` directly: the next build overwrites them.

Items marked `Show: speakers page only` in `content/program.txt` appear only on the speakers page.

Parts for the speakers page only are wrapped in `<!--@speakers-->…<!--/@speakers-->` (HTML) or `/*@speakers*/…/*/@speakers*/` (CSS/JS). Text that differs per page is set in `EDITIONS` in `src/build.py`.
