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
case. A sheet that was printed `S · 10` comes back from OCR as `S - 10`, which is
honestly what the scan says.

Nectar read all of those correctly. They just aren't in your house style, and
retyping them one row at a time is the job you wanted to stop doing.

Data Rules applies your formatting to the whole set at once. Open the rail from
Data Rules in the toolbar, set the shape you want, and every file in the session
follows it, including the ones you add tomorrow.

## What you can set

Case, first: upper, lower, title or sentence, picked separately for sheet number
and sheet title. Then the separator, which normalizes the punctuation inside a
sheet number, so `A 101`, `A.101` and `A - 101` all come out however you chose.
And for the genuinely one-off stuff, find and replace takes an optional regex and
can be scoped to the number, the title, or both.

## Nothing gets overwritten

Nectar keeps the raw extracted value and applies your rules on the way out: to
the table, the output name, the rename and the export. Turn the master toggle off
and every file goes straight back to what was read off the sheet. You never have
to work out which copy is the real one.

It also means re-extraction can't undo your rules, and files you add later pick
them up on their own. There is no re-apply button to forget about.

## When a rule is right about the set and wrong about one sheet

This will happen. A rule fixes ninety-four sheets and mangles the ninety-fifth.
Editing that one value by hand gets you nowhere, because the rule fires again on
whatever you type.

So you can pin a single field on a single file. The pin tells the lens to look
away for that one value and leave what you typed alone. Everything else in the
set carries on following the rule.

## Also in this release

We rebuilt the app icon around the honey ribbon-N and cut separate crops for
macOS and Windows, so it looks native on both. The app menu picked up Account &
License, Check for updates, a theme toggle and a keyboard shortcut sheet. Three
of those had no entry point at all before.
