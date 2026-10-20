---
title: Storyboards get their own site, and their own API
date: 2026-10-20
status: the memo is the go ("So yeah, so let's build"); Part 2 is an agent draft, not yet read by Dinis
by: Dinis Cruz (voice memo, transcribed by otter.ai); the brief below drafted from it by the storyboards agent
summary: The voice memo that started storyboards.sgit.ai and api.storyboards.sgit.ai, in full, and the brief an agent drafted from it.
---

This brief has two parts. The first is the person's words, transcribed by otter.ai and published as transcribed (filler words and transcription slips included, nothing corrected). The second is what an agent read in them, written down so that it can be checked against the first. Where the second turns out to be wrong, the correction goes in `BRIEF-CORRECTIONS.md`, not here.

## Part 1: the transcript, in full

*"Storyboards.ai Development and API Strategy", 20 October 2026, about six minutes.*

**Dinis Cruz  0:00**

Okay, so this is now to create a new website and service, which is actually an interesting mashup again of a lot of work we're doing, and this is about creating a website to make, share, sell the what's it called the. The storyboards that we started to do, which actually are working really well. I'm actually really liking them. I think they're working quite nicely. Like, so, so let's create a website. And again, same with the other ones to have articles, to have this stuff, but also to have the commercialization and to have a public way to show them and to link them, and even like the whole thing of every every storyboard. Then we'll have the JSON version, the markup version, the semantic graph version. The it will have the even the JPEG version, so the SVG version, the animated version, like all sorts of different variations of it, and the thumbnail version, etc. that we can create, and and eventually I think we should allow people to create their own casts, their own stuff. But let's let's literally replicate what we have right now, which is already very powerful, and it's a good example of a good idea because he started on the the book, and then the the Gen ZX devs, sorry founders, and then moved Into the PKI, and now is moving into its own world, which is here. So, but this is also going to be the the time where we're going to start experimenting and doing side by side two repos. Also, because Cloud now supports multiple repos, so in a way, the agent that is going to build this, you now maintain two repos, which is actually to make sure that we we are a bit more streamlined than what we're doing with the newsroom at the moment because the newsroom has enough fully synchronised. So so there's basically two websites. There's going to be the website called Storyboards.ai, and then there's going to be the API. Storyboard Skit AI, and the logic would be the API is what gets used because all this has cores is get used by other websites by embedding and and basically I want to start hosting all sorts of of these storyboards because I think they are a really nice way to explain something, right? They kind of strips, right? Cartoon strips, but I think storyboards seems to be a nice sweet spot, even for briefs, right? I would like to expand, so I want to see how far can we push this. But let's connect. So basically, refactor stuff in, start making the the changes. Now, one of the things I would like to do on the API, and it's something that I've done a while back in terms of coding, where I kind of created this sort of very versioning way of coding, especially in JavaScript, and I would like us to do now that now here, which is basically you should have, you should use the file path as a way to version the JavaScript, and you should basically every time you do a release, you basically publish a new file, right? And this is okay because these are small, well, smaller JavaScript files, but the logic would be every release is kind of self-contained, and you you basically publish that as I think what we'll do is we'll we'll we'll do the releases on the major one instead of the minor one, so the minor one are basically you can overwrite any file you want, and then the major one is where you now have a different folder, and then so basically we freeze in a way the JavaScript the way it was before. So and we could use the same so v 04 slash v 0.14 slash, and that's that's the version that you have, right? And then you have all the files required for the API, and and then actually, I guess on this case, yeah, I think on this case, can you do that so that every because I don't think we're going to have a ridiculous amount of files, can you do that for every minor version? You also have a full folder, right? So, so basically, every time you do a release, you you actually update the what's it called? The the version, so that so basically every version is immutable. I think that's important, right?

**Dinis Cruz  5:08**

And then you put the hashes, you put the whole thing. So basically, every version that we publish fundamentally is immutable. Even like version, so you could have version one four slash version. So v1 four slash V 1.74 slash V 1.7 point 14 or 12 or one or whatever, and that's basically the the the version that somebody can use. And then when we do a release, it's basically in a way I think the logic should be that the next major versions of v 0.8 should be the exact same code or minimal changes from the last good 7x or the the crew and seven the previous version good release. So yeah, so let's build

**Unknown Speaker  6:02**

this

Transcribed by https://otter.ai

## Part 2: the brief, as an agent read it

**What.** Two sites, built side by side as two repositories by one agent:

| Site | Repository | What it is |
|---|---|---|
| storyboards.sgit.ai | SGit-AI/SGit-AI__Website__Storyboards | The place to make, share and (later) sell storyboards: a public home for every storyboard, articles about them, and the links to embed them |
| api.storyboards.sgit.ai | SGit-AI/SGit-AI__Website__Storyboards__API | The code that draws them, which other websites embed. "The API is what gets used" |

(The memo says "Storyboards.ai" and "Storyboard Skit AI"; the repositories' own READMEs name the hosts storyboards.sgit.ai and api.storyboards.sgit.ai, and those are the names used here.)

**Why.** The storyboards "are working really well". They began with the book, moved to gen-z-developers.sgit.ai, then to pki.sgit.ai, "and now is moving into its own world". They are "a nice way to explain something": cartoon strips, but a sweet spot "even for briefs". The aim is to see how far they can be pushed, and to host many more of them.

**Do first: replicate what exists.** "Let's literally replicate what we have right now, which is already very powerful." The 16 gen-z boards and the 7 pki boards, their casts, the deck, the grid, the script, the shelf and the model sheet, drawn by the same kit, before anything new.

**Every storyboard in every shape.** The JSON version, the markdown version, the semantic graph version, the JPEG version, the SVG version, the animated version, the thumbnail version.

**Later, not now.** People creating their own casts and their own storyboards; commercialisation.

**The versioning rule for the API.**

- Use the file path as the version: every release publishes a new folder with all the files the API needs, self-contained. These are small files, so a full copy per release is affordable.
- Every version, patch and minor included, gets its own full folder (the memo first proposes folders per major, then changes its mind: "can you do that for every minor version? ... every version is immutable. I think that's important").
- The shape of the path: `v0/v0.14/...`, `v1.4/v1.7/v1.7.14`, read here as `/vMAJOR/vMAJOR.MINOR/vMAJOR.MINOR.PATCH/`.
- "You put the hashes, you put the whole thing": every release carries the hash of every file.
- A new major starts as the exact code of the last good release of the previous major, or minimal changes from it.

**How it is worked.** Two repositories, one agent, kept in step on every change: "more streamlined than what we're doing with the newsroom at the moment", whose site and API are not fully synchronised.

**Done when.** Both sites are built from these words and the sgit.ai guidance for new sites (a brief published in full, a version on every push shown in the chrome, a gate, markdown twins and llms.txt, the participant disclosure), the existing storyboards play on storyboards.sgit.ai from a pinned, immutable release of api.storyboards.sgit.ai, and each storyboard is available in each shape the memo names.
