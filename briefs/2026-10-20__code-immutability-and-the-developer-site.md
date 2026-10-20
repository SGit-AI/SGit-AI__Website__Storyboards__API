---
title: Code immutability, as a behaviour policy, and the API site as the developer site
date: 2026-10-20
status: the person's words in a session, after both sites went live; acted on the same day
by: Dinis Cruz, in the Claude Code session that built both sites
summary: Point releases without code releases are fine; the API site becomes the full developer site; code in a versioned path is immutable, written as an Agent Behaviour Policy and run as a hook.
---

The person's message, as typed into the session (a voice transcription, published unchanged), in answer to whether the API repository should keep a version that moves without a code release:

> Now, I think it's okay to have point releases that don't have code releases. So you could, let's say, for example, you change the content or change some information on the API website. By the way, the API website should have also a full-blown website, because that's where I think... See, that would make sense to be the website where you have all of the explanation about the code, about the API. So that makes sense to have everything to do with the code itself, where the main CLI is about the functionality, about everything. So we can geek out, even like I think, yes, so that's where the API usage or information should live on that website, right? So in a way, the API makes sense to be a full-on developer-friendly website, which basically means that in this example, you can make changes to the API.cli that don't change the code. We just need to keep track of what are the latest releases, fundamentally. And the releases every time you touch the code. So basically, what it is, and this should have a rule, is that the code is immutable. So that's important. So the code, as soon as you have a code in the file path, that code could not be changed. So we need to have a rule for that. In fact, we need to have an agent behavior policy for that. And actually, can you read riskmandate.ai if you don't have a policy already? And because this is one of the projects we're working on, and we should actually create a policy that is on code immutability, which is exactly what we have here. So we should have a policy which should run as a hook, and we should also have both a policy normal and then a hook policy that basically gives the instructions, and let's see how it works, that code should never be changed. Which makes sense with our design, correct?

## As the agent read it

| The words | Read as | Done in |
|---|---|---|
| "point releases that don't have code releases" | keep the two numbers: the repository's `version` moves on every push, the kit's `release` only when code changes | `tools/version.json`; [the release process](https://api.storyboards.sgit.ai/engineering/release-process.html) |
| "a full-on developer-friendly website" | everything about the code lives on api.storyboards.sgit.ai: guides, reference, a live gallery, internals, the patches as diffs, every release with its diff, tests, CI, policies; storyboards.sgit.ai stays about what the storyboards are and do | the site, v0.2.0 |
| "the main CLI", "the API.cli" | the main site and the API site (the transcription's word for "site") | |
| "the code is immutable ... as soon as you have a code in the file path" | a release folder is protected from the moment it exists, pushed or not | [ABP-SB-001](https://api.storyboards.sgit.ai/policies/code-immutability.html) |
| "an agent behavior policy ... read riskmandate.ai" | written in riskmandate.ai's and abp.sgit.ai's shape: mandate, grant, delta, barriers | the same |
| "a policy normal and then a hook policy that basically gives the instructions" | the prose page (an expectation on its own) and its compiled half, the JSON the hooks apply, with the instructions printed at session start and in every refusal | `policies/code-immutability.policy.json`, `.claude/hooks/code_immutability.py` |
| "let's see how it works" | tests that drive the hooks with real tool calls and real commits, refusals and allowed twins | `tests/test_policy.py` |
