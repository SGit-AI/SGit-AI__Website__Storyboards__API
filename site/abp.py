#!/usr/bin/env python3
"""The agent behaviour policy page, from policies/abp.json (type abp/site/v1), as markdown: the page's body and its
twin are the same text. The same file is in SGit-AI__Website__Storyboards (admin/build/abp.py) and
SGit-AI__Website__Storyboards__API (site/abp.py), so a site that copies the shape copies one renderer.
Counts are computed from the rules, never typed."""

BARRIERS = [("none", "nothing in the way"), ("expectation", "a rule in prose, enforced by nobody"),
            ("setting", "a control in a file or switch the agent's own grant can change"), ("boundary", "enforced above the grant, out of the agent's reach")]


def _cell(s):
    return str(s or "").replace("|", "/").replace("\n", " ")


def _link(text, url):
    return f"[{_cell(text)}]({url})" if url else _cell(text)


def check(abp):
    """The data's own rules: a type, unique rule ids, a known barrier on every rule, something named as the enforcer."""
    errors = []
    if abp.get("type") != "abp/site/v1":
        errors.append("type is not abp/site/v1")
    ids = [r["id"] for r in abp.get("rules", [])]
    errors += [f"rule id {i} appears twice" for i in sorted(set(ids)) if ids.count(i) > 1]
    for r in abp.get("rules", []):
        if r.get("barrier") not in [b for b, _ in BARRIERS]:
            errors.append(f"{r.get('id')}: barrier {r.get('barrier')!r} is not one of none, expectation, setting, boundary")
        for k in ("rule", "why", "enforced_by"):
            if not r.get(k):
                errors.append(f"{r.get('id')}: no {k}")
    for k in ("site", "version", "as_at", "agents", "grant", "mandate", "rules", "layers"):
        if not abp.get(k):
            errors.append(f"no {k}")
    return errors


def markdown(abp):
    rules = abp["rules"]
    count = {b: sum(1 for r in rules if r["barrier"] == b) for b, _ in BARRIERS}
    strongest = next((b for b, _ in reversed(BARRIERS) if count[b]), "none")
    L = []
    L += ["This page is the site's agent behaviour policy, in the shape [riskmandate.ai](https://riskmandate.ai/abp.html) and [abp.sgit.ai](https://abp.sgit.ai/) define: "
          "the agents that work on the site, everything they **can** do (the grant), what they are **asked** to do (the mandate), and every rule with the **barrier** that "
          "actually stands in its way and what enforces it. It describes; it does not score. It is generated from "
          f"[policies/abp.json](https://github.com/{abp['repository']}/blob/dev/policies/abp.json) (also served as [abp.json](abp.json)), the same data a tool would read.", ""]
    L += ["| | |", "|---|---|",
          f"| Site | {abp['site']} |", f"| Behaviour policy | version {abp['version']}, as at {abp['as_at']} |", f"| Status | {_cell(abp['status'])} |",
          f"| Shape | `{abp['shape']}`, operated by {abp['operator']} |", f"| Agents | {len(abp['agents'])} |",
          f"| Rules | {len(rules)}: " + ", ".join(f"{count[b]} {b}" for b, _ in BARRIERS if count[b]) + " |",
          f"| Strongest barrier | {strongest} |"]
    if abp.get("twin"):
        L.append(f"| Twin | [{abp['twin']['site']}]({abp['twin']['abp']}), worked by the same agents, with its own behaviour policy |")
    L += ["", "## The agents", "", "| Agent | Runs as | Does | Reads at start | Leaves behind |", "|---|---|---|---|---|"]
    L += [f"| **{_cell(a['name'])}** ({_cell(a['kind'])}) | {_cell(a['runs_as'])} | {_cell(a['does'])} | {_cell(', '.join(a.get('reads_at_start', [])))} | {_cell(a.get('leaves'))} |" for a in abp["agents"]]
    L += ["", "## The structure in place", "", "Where a rule can live, from a sentence the agent reads to a rule the host enforces, and what this site has at each layer. "
          "A control bounds the agent only if it is enforced by something the agent's grant does not include.", "",
          "| Layer | Barrier | Here |", "|---|---|---|"]
    L += [f"| {_cell(l['layer'])} | {l['barrier']} | {_cell(l['here'])} |" for l in abp["layers"]]
    L += ["", "## The grant: what the agents can do", "", "Measured from the session's own tools, not from what it was told.", "",
          "| Capability | What | Undo | Note |", "|---|---|---|---|"]
    L += [f"| `{_cell(g['capability'])}` | {_cell(g['what'])} | {_cell(g.get('undo'))} | {_cell(g.get('note'))} |" for g in abp["grant"]]
    m = abp["mandate"]
    L += ["", "## The mandate: what they are asked to do", "", "**Want**", ""] + [f"- {x}" for x in m.get("want", [])]
    L += ["", "**Do not want**", ""] + [f"- {x}" for x in m.get("do_not_want", [])]
    if m.get("unstated"):
        L += ["", "**Not stated, and how it stands**", ""] + [f"- {x}" for x in m["unstated"]]
    L += ["", "## The rules, each with its barrier", "", "| Id | The rule | Barrier | Enforced by | Stronger at |", "|---|---|---|---|---|"]
    L += [f"| {_link(r['id'], r.get('detail'))} | {_cell(r['rule'])}. *{_cell(r['why'])}* | {r['barrier']} | {_cell(r['enforced_by'])} | {_cell(r.get('stronger_at')) or 'not named'} |" for r in rules]
    L += ["", "## The delta", "", f"The grant includes more than the mandate wants: every \"do not want\" above is something the agents can do. Of the {len(rules)} rules that stand in the way: "
          f"{count['boundary']} enforced out of the agents' reach (boundary), {count['setting']} by a control in a file or switch the agents can change (setting), "
          f"{count['expectation']} by being written down (expectation), {count['none']} by nothing.", ""]
    L += ["| Barrier | Means | Rules |", "|---|---|---|"] + [f"| {b} | {d} | {count[b]} |" for b, d in BARRIERS]
    L += ["", "## Where each rule maps to", "", "The same rule, or its nearest neighbour, elsewhere in the estate and in riskmandate.ai's catalogue. As rules are refactored to other sites, this is where the mapping is kept.", "",
          "| Id | Maps to |", "|---|---|"]
    L += [f"| {r['id']} | {_cell('; '.join(r.get('maps_to', [])) or 'nothing yet: this rule is new')} |" for r in rules]
    L += ["", "## The gaps", ""] + [f"- {g}" for g in abp.get("gaps", [])]
    L += ["", "## Adding this to another site", "", abp.get("copy_to_another_site", ""), "",
          "## What this is not", "", f"Not a score and not a judgement of the agents. It describes this deployment as at {abp['as_at']}; when the deployment changes, "
          "it is re-measured and its version moves, and the page is not edited to look as if it had always been so."]
    return "\n".join(L) + "\n"
