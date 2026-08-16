---
version: "0.6.0"
date: "2026-08-14"
headline: "Data Rules"
feature: true
summary:
  - "Apply your corrections and style preferences to every sheet number and title at once, and watch the table follow"
  - "One find & replace fixes a set-wide OCR misread; a pin spares the one sheet it would break"
---

Every drawing set arrives needing the same kind of cleanup. One consultant sets every title in full capitals. The next capitalizes the first word and calls it a day. A title block that prints `S · 10` comes through the scan as `S - 10`, when your file names need to read `S 10`.

Then there is the data that is simply wrong. OCR gets most sheets right, and then it reads a tight `S` as an `8`. The lettering that fooled it on one sheet fools it on the next, and the one after that, so a single misread runs the whole length of the set.

Either way you are correcting data, and that repair has looked the same for years: fix a cell, arrow down, fix the next one. Ninety-five rows, one at a time.

Data Rules does the whole set at once. You will find it in the toolbar; click **Data Rules** and a panel opens beside the file table. From then on the table itself is the live preview: change a setting and you watch every row respond. Set it once and every file in the session follows, including the ones you add next month.

## Case that knows the trade

Sheet numbers and sheet titles each get their own case setting: `Leave as-is`, `UPPERCASE`, `lowercase`, or `Title Case`.

Title Case is where the care went. Generic title casing looks at `HVAC PLAN` and proudly hands back `Hvac Plan`, which nobody has ever wanted on a drawing. Nectar's version knows the vocabulary: HVAC, MEP, RCP, ADA, NTS, RTU, AHU, VAV, GFCI, CMU, AFF, TYP, and UON stay uppercase, roman numerals stay roman, and `1ST FLOOR PLAN` comes out `1st Floor Plan` rather than `1St Floor Plan`. The acronym list is built in, and not editable yet.

## One separator across the set

No two clients punctuate a sheet number quite alike, and the scan adds opinions of its own. This rule settles the matter. Pick `Dash (A-101)`, `Dot (A.101)`, `Space (A 101)`, or `None (A101)` and every number falls in line: `S · 10` with Space becomes `S 10`, and `M101` with Dash becomes `M-101`. Suffixes survive, so `A-1.1` with Space comes out `A 1.1`. (`Leave as-is` is there too, for sets that already behave.)

It is picky on purpose. The rule only fires on values shaped like a real sheet number: letters, separator, digits. A client's custom number like `9240-86602-1` has no discipline letter, so it is left entirely alone. Your oddballs are safe.

## Find and replace, for everything else

The third rule is a list of find-and-replace entries. Nectar runs them top to bottom. Scope each one to `Sheet Number`, `Sheet Title`, or `Both fields`; it matches plain text by default, and a per-entry Regex toggle covers the occasions plain text cannot reach. `+ Add` grows the list; the trash icon prunes it.

This is the tool for that `8`. A mistake this consistent is exactly the kind a replacement can undo: one entry swapping `8` for `S` puts the whole set back the way the drawings actually read. A misread that shows up once, on one sheet, is still a hand edit. The ones that repeat stop being your job.

Two mechanics worth knowing. Replacements run last, after the case and separator rules, and they match case-insensitively, so an entry you typed in lowercase still fires after `UPPERCASE` has made its pass. And a half-typed regex does nothing at all until it becomes valid, so experimenting can never scramble the table.

## The one sheet where the 8 is real

A rule that confident will eventually be wrong. The `8` to `S` entry fixes ninety-four sheets, then reaches the one sheet whose `8` is genuine and turns `A801` into `A-S01`. Retyping the correct value gets you nowhere; the rule fires again on whatever you type, because that is its job.

So pin it. Wherever a rule is changing a field, a pin icon appears beside that field in the side panel. Click it and it turns amber; from then on the rules skip that one field on that one file, and what you typed stays put. The other ninety-four sheets keep their fix, and the panel's footer shows `· 1 pinned` in amber so the exception never goes missing.

## A draft until you press Apply

Everything in the panel is a draft. The table previews it instantly, but nothing is committed until you press **Apply**. **Revert** walks back to the last applied state, and **Reset** clears the rules entirely.

While the panel is open, any cell a rule has changed wears a dotted underline, and hovering it shows the original value. The footer keeps score with counts like `71/95 Sheet Number · 95/95 Sheet Title`, so you can tell whether a rule is reshaping the whole set or grazing three rows of it.

## Rules are a lens

Underneath all of this sits one decision we want you to know about: Nectar stores the raw extracted value, permanently, and applies your rules on the way out. To the table, to the output name, to the rename, to the export. The stored value itself never changes.

That is why you can relax. Flip the master switch off and every file instantly shows exactly what was read off the sheet. Re-extraction cannot undo your rules. Files added later pick the rules up the moment they land, with no re-apply button to forget, because nothing is ever applied to the stored data at all. And if you ever wonder which copy is the real one: there has only ever been one.
