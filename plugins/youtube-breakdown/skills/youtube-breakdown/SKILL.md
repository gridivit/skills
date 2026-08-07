---
name: youtube-breakdown
description: Use when a YouTube link appears in the conversation (youtube.com/watch, youtu.be, /shorts, /embed, or a bare 11-character video id) and the user wants to know what is in the video - what it is about, what the author says or argues, a breakdown, chapters, notes, key points, a retelling, or a summary. Applies even when the request is as short as "what is this about?", "worth watching?", or just the bare link with no question at all. Also applies when the user asks to compare, fact-check, or pull specific claims out of a video.
---

# YouTube Breakdown

## Core principle

The breakdown is built from the transcript and nothing else. No transcript, no breakdown.

The description, chapter list, comments, and whatever you happen to remember about a famous video are
**not** sources. They produce a confident retelling of a video you never read, which is the single
worst outcome here and is indistinguishable from the real thing to the reader.

Metadata may **identify** the video - title, channel, duration - and never supplies its content. A
title from the page is fine in the source line; a claim from the page is not.

## Getting the transcript

Use the `youtube-transcript` MCP server. Two tools, in this order:

1. `list_transcript_languages(url)` - one line per track: `<code> - <name> (manual|auto-generated)`.
2. `get_transcript(url, language)` - the full transcript as plain text.

The tool name may carry a server prefix that varies per install (`mcp__youtube-transcript__get_transcript`,
`mcp__youtube-transcript-dev__get_transcript`). Match on the tool name, not the prefix.

**Always call `list_transcript_languages` first.** `get_transcript` silently falls back to English
when the language you asked for does not exist - you get a transcript, it is just not the one you
requested, and nothing in the result says so.

Track choice: prefer a **manual** track over an auto-generated one in the same language. Prefer the
language the video was actually spoken in over a translated track - translated auto-subs lose the
author's terminology. Most videos offer exactly one auto-generated track and there is nothing to
choose - that is the normal case, not a degraded one. Take it and note it in the source line.

If the server is not installed or every call fails, say exactly that and stop. Install info:
<https://github.com/gridivit/mcp-youtube-transcript>

## Hard rules

These are the failures observed in testing. They are not negotiable.

- **No transcript means no breakdown.** If the fetch fails, is refused, or the video has no
  subtitles, say so plainly, name the reason, and stop. Distinguish the two cases - the tooling never
  reached YouTube, versus the video genuinely has no subtitle track - because the user can only fix
  the first. Anything you go on to offer must not be shaped like the breakdown: no numbered chapters
  about the channel, the creator, or the topic assembled from search results and memory. That reads as
  a breakdown of the video no matter what the disclaimer above it says.
- **A guess about why the transcript is missing is still a claim about the video.** "It is probably
  just music, so there is nothing to transcribe" is exactly the move this skill exists to prevent.
- **Report the track you actually used**, not the one you asked for. Compare the result against what
  `list_transcript_languages` returned.
- **The author's claims and your opinions never share a voice.** Everything in the chapters is what
  the author said. Your own assessment - that it is outdated, wrong, or contradicted elsewhere - goes
  under a separate heading at the end, or nowhere. The author's *own* hedging, irony, and emphasis are
  part of what they said: carrying a figure over as a joke the speaker made, rather than as a forecast
  they issued, is accuracy, not commentary.
- **Never invent a timestamp.** The transcript carries no timing information. If the user wants
  timecodes, say they are not in the transcript and offer the video's own chapter markers as a
  separate lookup.

## Output contract

Produce these parts, in this order, in the language the user is writing in. Keep the author's terms,
product names, and quoted phrasing in the original language.

1. **Source line.** Title, track used (`ru manual` / `en auto-generated`), rough transcript length in
   words - eyeball it, it is not worth a tool call.
2. **One sentence** on what the video is, overall.
3. **Numbered chapters.** One chapter per topic shift in the transcript - roughly one per 3-6 minutes
   of video. A 60-minute talk yields 12-20 chapters. Each chapter is a `##` heading that states the
   author's point rather than labelling the topic ("Training is lossy compression of the internet",
   not "About training"), followed by:
   - what the author claims;
   - the specifics they use to back it - numbers, names, examples, demos, analogies - carried over
     rather than paraphrased away;
   - any caveat or hedge the author makes themselves.
4. **Bottom line.** What the author is arguing across the whole video.
5. **Garbled in the transcript** (only if applicable) - see below.

A chapter that survives without its numbers and examples was compressed too far. The specifics *are*
the content; the topic label is not.

## Auto-generated tracks garble names and terms

Auto-subs reliably mangle proper nouns and jargon, sometimes inverting meaning. Real examples from one
transcript: `reversal course` was *reversal curse*, `Llama 270b` was *Llama 2 70B*, `Chachi PT` and
`chbt` were *ChatGPT*, `merily feifer` was *Mary Lee Pfeiffer*, `mistol` was *Mistral*, `rhf` was
*RLHF*.

Reconstruct from context when the intended term is unambiguous, and use the corrected form in the
breakdown. When a name or figure matters and you are **not** confident, write it as heard and flag it.
List anything you could not resolve under **Garbled in the transcript** at the end, so the reader knows
which spellings to verify rather than trusting them.

## When not to use

A YouTube URL in the conversation is not always a request to break down the video. Skip this skill when
the link is incidental to some other task - adding it to a README, fixing a broken link, scraping a
list of URLs, styling an embed. Handle the actual task instead.

## Common mistakes

| Mistake | What to do |
|---|---|
| Fetch failed, so the answer was built from the description and memory | Say the fetch failed and stop |
| Asked for `ru`, reported `ru`, actually received the English fallback | Check `list_transcript_languages`, report the real track |
| Short question ("what's this about?") answered with a short blob | The contract does not change with the phrasing of the ask |
| Long video compressed into 4 broad blocks | Chapters follow topic shifts, not a fixed budget |
| Numbers, names, demos dropped as "detail" | Those are the content - keep them |
| "This talk is outdated" written in the author's voice | Own assessment goes in its own section |
| Timestamps attached to chapters | The transcript has none - do not invent them |
