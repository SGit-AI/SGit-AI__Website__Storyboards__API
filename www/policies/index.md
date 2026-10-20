# Policies

> The agent behaviour policies this repository runs under, and how each is enforced.

*Source: <https://api.storyboards.sgit.ai/policies/index.html>.*

---

The rules an agent working on this code must follow, each written in the shape of riskmandate.ai's Agent Behaviour Policy (what the agent may reach, what it is mandated to do, the gap between the two and the barriers in place), and each enforced by something that runs, not only by being read.

- [Code immutability](code-immutability.html) (ABP-SB-001, in force from repository v0.2.0; written by the storyboards agent from Dinis Cruz's words, not yet read by him): Code in a published release folder is never changed, by any agent, for any reason. The behaviour policy for that one line, in riskmandate.ai's shape, and the hooks, gate and CI that enforce it.
