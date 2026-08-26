---
name: copy-quality
description: Remove repetitive, generic AI-sounding copy and keep professional language natural, without touching approved wording or changing any factual claim. Use when writing or editing website copy, bios, project descriptions or summaries, or when text reads as machine-generated.
---

# Copy quality

Two constraints govern every edit here:

1. **Do not change meaning.** Improving a sentence must not add, remove or alter a
   factual claim. If a rewrite makes something stronger, it is a factual change.
2. **Do not touch approved wording.** Protected strings stay verbatim.
   Improving them is not your call.

Everything below is about the words between the facts.

## What makes copy read as machine-generated

**Empty openers and closers.** "In today's fast-paced digital landscape", "When it
comes to", "It's worth noting that", "At the end of the day". Delete them; the
sentence after is the sentence.

**Stacked adjectives with no content.** "Innovative, cutting-edge, comprehensive
solutions." Each word claims something and proves nothing. Replace the stack with the
one specific thing that is true.

**Symmetry.** Every paragraph the same length; every list exactly three items; every
sentence a subordinate clause followed by a main clause. Real writing is uneven.

**Hedged confidence.** "Can help you to potentially improve" — say what it does.

**The rule-of-three habit.** "Fast, reliable, and scalable." Fine once. Three times on
one page is a tell.

**Restating the heading.** A section titled "Experience" that opens "I have
experience in..." wastes the first line.

**Transitions that connect nothing.** "Moreover", "Furthermore", "Additionally"
between unrelated paragraphs.

**Self-description instead of description.** "This section outlines my approach to..."
Just outline it.

## Repetition to look for

- the same word opening several consecutive sentences or list items
- the same verb across every bullet ("Developed… Developed… Developed…")
- the same adjective on every project
- a phrase repeated across pages that should each say something different
- the same sentence in both the metadata description and the visible body — search
  engines see duplication, and readers see filler

Read the list items in sequence, on their own. Repetition is invisible in prose and
obvious in a list.

## What natural professional language looks like

- **Specific over general.** "Cut page weight from 2.1 MB to 380 KB" — but only if
  that number is supported. If it is not, say "reduced page weight" rather than
  inventing a figure.
- **Concrete verbs.** Built, migrated, rewrote, measured, fixed — not "leveraged",
  "utilised", "spearheaded".
- **Ordinary words.** Use, not utilise. Help, not facilitate. About, not regarding.
- **Varied sentence length.** A short one lands after two longer ones.
- **First person where the document is first person**, consistently. A bio that
  switches between "I" and "he" mid-page reads as assembled.
- **Active voice** unless the actor genuinely does not matter.

## Editing procedure

1. Read the whole piece before changing a word. Local edits produce local
   consistency and global drift.
2. Mark every protected string and every factual claim. Those are frozen.
3. Cut first. Most improvement is deletion. If a sentence can go without losing
   information, it goes.
4. Then rewrite what remains, one sentence at a time, keeping the claims identical.
5. Read the result aloud. The sentences you stumble over are the ones to fix.
6. Diff your version against the original and check every changed line for meaning
   drift — see `/dado-content-localization:content-diff-review`.

## For bilingual content

Both versions get the same treatment, each in its own language. Do not make one a
literal translation of the other's improved phrasing — natural in one language is
often stilted in the other. Substance stays identical; wording is per language.

## Report

```
Cut:        <n> words removed, <n> sentences deleted
Rewritten:  <before> -> <after>      [one line per non-trivial change]
Unchanged:  protected strings <list> — verbatim
Claims:     unchanged (verified line by line) | CHANGED: <what, and why>
Flagged:    <sentences where a rewrite would risk meaning — left alone for the user>
```

If a rewrite would improve the sentence but risk a claim, leave it and flag it. A
slightly clumsy true sentence beats an elegant false one.
