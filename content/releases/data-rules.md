---
version: "0.6.0"
date: "2026-08-14"
headline: "Data Rules"
feature: true
summary:
  - "Case, separator and find & replace, applied to a whole set at once"
  - "Pin a field to exempt one sheet from a rule that's right about the rest"
  - "A rebuilt app icon, and a tidier app menu"
---

Every set of drawings turns up with somebody else's conventions baked into it.
One consultant sends every title in capitals. The next sends them in sentence
case. A sheet printed `S · 10` comes back as `S - 10`, which is roughly what the
scan says.

Some of it isn't house style at all. OCR will sometimes read a tight `S` as an
`8`, and when a set is lettered the same way throughout, that misread tends to
repeat, so you end up making the same correction on sheet after sheet.

Either way you are retyping, one row at a time, and that is the job you wanted to
stop doing.

Data Rules applies the fix to the whole set at once. Open the rail from Data
Rules in the toolbar, set the shape you want, and every file in the session
follows it, including the ones you add tomorrow.

## What you can set

Case, first: upper, lower, title or sentence, picked separately for sheet number
and sheet title. Then the separator, which normalizes the punctuation inside a
sheet number, so `A 101`, `A.101` and `A - 101` all come out however you chose.

Find and replace covers everything else, including the misreads. If this set came
back with `8` everywhere the drawings say `S`, one rule puts them all back. It
takes an optional regex and can be scoped to the number, the title, or both.

## Nothing gets overwritten

Nectar keeps the raw extracted value and applies your rules on the way out: to
the table, the output name, the rename and the export. Turn the master toggle off
and every file goes straight back to what was read off the sheet. You never have
to work out which copy is the real one.

It also means re-extraction can't undo your rules, and files you add later pick
them up on their own. There is no re-apply button to forget about.

## When a rule is right about the set and wrong about one sheet

This will happen, and that `8` to `S` rule is exactly how. It fixes ninety-four
sheets, then reaches the one whose number really does contain an 8 and mangles
it. Editing that value by hand gets you nowhere, because the rule fires again on
whatever you type.

So you can pin a single field on a single file. The pin tells the lens to look
away for that one value and leave what you typed alone. Everything else in the
set carries on following the rule.

## Also in this release

We rebuilt the app icon around the honey ribbon-N and cut separate crops for
macOS and Windows, so it looks native on both. The app menu picked up Account &
License, Check for updates, a theme toggle and a keyboard shortcut sheet. Three
of those had no entry point at all before.
