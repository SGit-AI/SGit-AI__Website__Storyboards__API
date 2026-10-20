---
title: A behaviour policy page, top level, on every site
date: 2026-10-20
status: the person's words in a session; acted on the same day
by: Dinis Cruz, in the Claude Code session that built both sites
summary: A top-level page on each site that captures its agent behaviour policy, the structure in place and the agents, to be added to every site and mapped as the policies are refactored across them.
---

The person's message, as typed into the session (a voice transcription, published unchanged):

> Can you also add a section, maybe top level section, I think that's quite important for ABPs, for the agent behavior policies, and where you start to capture the behavior policy that exists on this website and the structure we have in place and the agents, I think. And I think that's probably something that we'll probably add to every single website that we have. So we start to control it. And then, we, as we refactor some of these, you know, behavior policies to other sites, we then start mapping them, you know, to there. But yeah, make it a top level page.
>
> And yes push both repos to dev

## As the agent read it

| The words | Read as | Done in |
|---|---|---|
| "a top level section ... for the agent behavior policies" | a page in each site's top bar, at `/abp/` | storyboards.sgit.ai and api.storyboards.sgit.ai |
| "the behavior policy that exists on this website and the structure we have in place and the agents" | the agents, the layers of control from a prompt to a host rule, the grant, the mandate, every rule with its barrier and what enforces it, and the gaps | `policies/abp.json` in each repository, rendered by one renderer |
| "add to every single website that we have" | written as data with a type (`abp/site/v1`) and a renderer another site can copy | the page's last section says how |
| "as we refactor some of these behavior policies to other sites, we then start mapping them" | each rule names where it maps to: the riskmandate.ai catalogue, other sites' rules | the "Where each rule maps to" table |
| "So we start to control it" | each rule that was only prose and could be checked cheaply now is: imported storyboards by hash (ABP-SB-002), briefs unchanged on dev (ABP-SB-006), no third-party request from the kit (ABP-SB-009) | the build, CI, the test harness |
