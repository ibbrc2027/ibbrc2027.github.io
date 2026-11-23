# IBBRC 2027 conference website

10th International IBBRC Conference, "Brain–Body Plasticity", Feb 23–25 2027, University of Haifa.

- Page for all participants: https://lamado02.github.io/ibbrc2027/
- Page for invited speakers (do not link it from the public page): https://lamado02.github.io/ibbrc2027/speakers-b663ff.html

## How it is built

Both pages come from **one source**, `src/site.html`. Shared content (speakers, program, posters, venue) is written there once.

1. Edit `src/site.html` (logos are in `src/img/`).
2. Run `python src/build.py` (Python 3, no packages). It writes `index.html` and `speakers-b663ff.html`.
3. Commit and push. GitHub Pages updates the site within a minute or two.

Don't edit `index.html` or `speakers-b663ff.html` directly: the next build overwrites them.

Content in `src/site.html`:
- `SPK`: speakers (name, institution, talk title, abstract).
- `DAYS`: the program. A `null` talk shows as "Speaker TBA".

Parts for the speakers page only are wrapped in `<!--@speakers-->…<!--/@speakers-->` (HTML) or `/*@speakers*/…/*/@speakers*/` (CSS/JS). Text that differs per page is set in `EDITIONS` in `src/build.py`.
