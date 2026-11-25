# IBBRC 2027 conference website: instructions for Claude

You are helping update the website of the 10th International IBBRC Conference, "Brain–Body Plasticity",
Feb 23–25 2027, Safdie Hall, University of Haifa. Attendees read it on their phones during the conference.

- Page for all participants: https://ibbrc2027.github.io/
- Page for invited speakers only: https://ibbrc2027.github.io/speakers-b663ff.html. **Never link to it, mention it, or copy its address anywhere.**
- Repository: https://github.com/ibbrc2027/ibbrc2027.github.io (branch `main`). The repository is **public**.

These instructions are for any Claude: Claude Code (with a copy of the repository), or Claude in a chat/browser
that cannot change files itself. Read all of this before changing anything.

## What you update, and where

All content that changes lives in three plain-text files in `content/`. **These are the only files you edit.**

| What | File | Typical request |
|---|---|---|
| Speakers: name, institution, talk title, abstract | `content/speakers.txt` | "Here is X's abstract", "X's title changed" |
| Program: days, times, sessions, who speaks when | `content/program.txt` | "Session 4: Y replaces TBA", "lunch moves to 13:15", "update the program from the sheet" |
| Posters: number, title, authors, abstract | `content/posters.txt` | "Add these posters", "poster 12's title changed" |

Each file starts with a short explanation of its format (lines starting with `#`). Read it first.

### content/speakers.txt
```
== livneh
Name: Yoav Livneh
Institution: Weizmann Institute of Science
Title: Brain-body interactions: sensations and predictions in the insular cortex
Abstract:
The continuous dialog between brain and body is essential for physical and mental health. ...
```
- `== id`: lowercase letters, digits and hyphens. **Never change an existing id**: the program uses it.
- Fields in this order: `Name:`, `Institution:`, `Title:`, `Abstract:` (always last). Empty Title/Abstract show "to be announced".
- The abstract runs from the line after `Abstract:` until the next `==`. A blank line starts a new paragraph; single line breaks
  (for example, from a PDF) are joined automatically. Plain text only: no HTML, no Markdown.
- New speaker: add a block with a new id (usually the last name, e.g. `== cohen`). To give them a time, also put the id in `content/program.txt`.

### content/program.txt
```
=== Day 2 | Wed · Feb 24 | 2027-02-24

-- 11:40–13:00
Type: session
Label: Session 4
Speakers: chen, TBA, blinder, jammal
```
- A day starts with `=== Day N | Ddd · Mmm DD | YYYY-MM-DD`. An item starts with `-- HH:MM–HH:MM` (or one time, `-- 19:00`). Items are in time order.
- `Type:` break (thin grey line) | session (card with speakers) | keynote (cyan stripe) | event (plain card) | social (light-blue card).
- `Label:` the small blue caption (Session 3, Keynote, Plenary). `Title:` e.g. Brain-Body Psychiatry, Lunch.
- `Speakers:` speaker ids from `content/speakers.txt`, in talk order, separated by commas. `TBA` for an unknown speaker.
- `Link: posters` / `Link: tour`. `Show: speakers page only` hides an item on the public page (tour, speakers' dinner).
- A speaker who cancels: replace their id with `TBA` in the program (keep their block in speakers.txt, or ask whether to remove it).

### content/posters.txt
```
== 12
Title: Interoceptive signals shape memory consolidation
Authors: First Author, Second Author
Institution: University of Haifa
Abstract:
Text of the abstract...
```
- `== number`: the poster/board number (digits, or a letter + digits like `A12`). Title and Authors are required.
- While the file has no posters, the Posters tab says they will be listed later.

## Updating the program from the Google Sheet

The organizers keep a working program in a **private Google Sheet**. Use it **only when the maintainer or Rika asks**
("update the program from the sheet"). Never make the sheet public and never write its link in this repository.
1. Read the sheet (through a Google Drive/Sheets connection, or ask the person to paste its contents or give you an export).
2. Compare it with `content/program.txt` and `content/speakers.txt` and **list the differences** for the person in plain words
   (e.g. "Session 4: Asya Rolls instead of TBA", "Day 3: coffee break 14:40–15:00 is new").
3. **Wait for a clear OK**, then change only the approved items.
4. The sheet contains internal notes (who confirmed, who cancelled, who will ask whom, chair suggestions, countries).
   **None of that goes on the site.** Only confirmed program items do. If the sheet says someone hasn't confirmed or "will be asked", ask before listing them.
5. If a name in the sheet is spelled differently or is a first name only, match it to the existing speaker id, and ask if unsure.

## How to reply (important)
The people you help are not technical and won't read long answers. Keep every reply short: it should take about 10 seconds to read.
- **When you're done**, start with ✅ (done) or ❌ (not done), then say exactly what is now on the site, quoted, in plain words. For example:
  > ✅ Added to the site. Gali Umschweif, talk title: "Peritraumatic MDMA attenuates the development of traumatic fear memories"
- **Before you change anything**, if you worked out the changes yourself (from an email, an attachment or the sheet), list them in short
  lines and ask "OK?". If the request already says exactly what to change, just do it.
- At most about 5 lines. Don't use technical words (commit, push, build, Action, clone, repository, Python), commands, file paths, or a log
  of the steps you took. Don't mention problems you solved yourself or things that don't matter (for example, Python missing when the
  GitHub check passed).
- Only if the person must do something (sign in to GitHub, answer a question, fix a mistake), say exactly what to do in one or two lines.

## Rules (for every change)
1. **Don't invent anything.** Copy names, titles, times and abstracts exactly as given. If something is missing or unclear,
   leave it empty / TBA and tell the person you're helping what's missing.
2. **No personal details on the site or in the commit message**: no phone numbers, private emails, addresses, forwarded email text,
   or internal notes. Only what attendees should see.
3. **Change only what the request is about.** Don't reorder, reformat or "fix" other entries.
4. **Don't touch anything else**: not `src/` (design, layout, logos), not `index.html` / `speakers-b663ff.html` (generated automatically),
   not `.github/`. If a request needs a design change, tell the person to ask the site maintainer (GitHub: Lamado02).
5. If the request is ambiguous (two people with the same name, a time that clashes, a title that doesn't match the abstract), ask first.

### Commit message
One line, in English, saying what changed, with no personal details. For example:
`Abstract added: Yoav Livneh`, `Program: Session 4 speaker added (Asya Rolls)`, `Program: Day 3 coffee break added`, `Posters 1-24 added`.

## How to make the change

### A. If you can edit files and run git (Claude Code)
1. `git pull` first (others edit this site too).
2. Edit only the file(s) in `content/`.
3. Check: `python src/build.py`. If something is wrong, it prints `ERROR in content/<file>, line N: ...`. Fix it before committing.
   (You may commit the rebuilt `index.html` / `speakers-b663ff.html` too, or leave them: GitHub rebuilds them anyway.)
4. Commit with a message as above and `git push`.

### B. If you cannot change files yourself (chat in the browser)
Give the person you're helping the exact text to paste, and these steps:
1. Open the file on GitHub (signed in), for example
   https://github.com/ibbrc2027/ibbrc2027.github.io/blob/main/content/speakers.txt
   (or `.../content/program.txt`, `.../content/posters.txt`).
2. Click the pencil ✏️ ("Edit this file") at the top right of the file.
3. Find the right place (Ctrl+F) and paste or change the text.
4. Click the green **Commit changes...** button, write the commit message (as above), and click **Commit changes**.

## After the change: check it went live
- GitHub rebuilds the site by itself (the "Build site" job). It takes about 2 minutes.
- In the repository, open the **Actions** tab. ✓ green = done. ✗ red = there was a mistake: open the run and read the line that starts
  with `ERROR` (it names the file and the line), fix it the same way, and commit again. While it's red, the site simply stays as it was.
  Nothing breaks.
- Then open https://ibbrc2027.github.io/ on a phone (refresh) and check.

## For the maintainer (more technical)
- `src/site.html`: design and layout. `src/build.py` merges it with `content/*.txt` (as `{{SPEAKERS}}`, `{{PROGRAM}}`, `{{POSTERS}}`) and writes both pages
  (logos embedded). Speakers-page-only parts of the layout: `<!--@speakers-->…<!--/@speakers-->` and `/*@speakers*/…/*/@speakers*/`.
- `.github/workflows/build.yml` runs the build on every push to `content/` or `src/` and commits the pages.
- Brand colors: navy `#193445`, cyan `#0BB5E5`, light cyan `#A3F0FC`.
