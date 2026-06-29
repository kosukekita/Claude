---
name: loop-evaluator
description: Use when an agent (often you) is about to judge its OWN output — deciding whether code/a fix/a PR is good enough to merge, ship, or stop on — especially inside an automation or loop where a weaker model judges round after round. Symptoms: "the tests are green so it's fine", "I wrote it so I know it's right", "it's a small diff", "we've succeeded N times so drop the check". Use whenever a generator is about to grade itself.
---

# Loop Evaluator — Separate the One Who Writes from the One Who Judges

## Overview

An agent asked to grade what it just produced **praises it confidently, even when the
quality is plainly mediocre.** This is not a smarts problem — it is grading one's own
homework. The author sees the chain of self-persuasion that led to the code, not the
result. Inside a loop the flaw compounds: every "is this good enough?" decided by the
agent that just wrote it makes the loop nod at itself, drifting further from real quality
each round.

**Core principle:** Tuning an independent skeptic is far more tractable than making a
generator critical of its own work. So don't try to fix the modest author — swap in a
separate evaluator. (Borrowed from GANs: one network builds, one picks faults.)

## The four steps that grow a loop's ability to say "no"

1. **Separate generation from judgment structurally.** A different agent reviews — not
   the same agent in a "now review yourself" turn. See `.claude/agents/loop-reviewer.md`.
2. **Tune the evaluator into a skeptic.** Default stance: *assume the code is broken until
   proven otherwise.* Do not praise. Swap the underlying model too — the same model with
   new instructions keeps its blind spots.
3. **Make it verify by ACTING, not reading.** "Does this look right" → "I ran it, here is
   the output / I clicked the button, here is the screenshot." For web/UI use the chrome MCP.
4. **Hand the final say to a fresh model.** Completion is decided by an independent check
   (a fresh, often smaller/faster model judging an explicit stop condition), not the one
   doing the work. This is the maker–checker principle (decades old in banking: whoever
   enters a large transfer and whoever approves it must differ).

> A loop's floor is its evaluator. The generator's level decides what a loop *can* produce;
> the evaluator's level decides what it *will not* produce. Put your engineering effort here.

## How to apply in this environment

- **Independent agent:** spawn the `loop-reviewer` subagent (Agent tool) — its definition
  lives at `agents/loop-reviewer.md` under this repo. A Workflow can call it per finding with
  `agentType: 'loop-reviewer'` if the Workflow tool is available.
- **Different vendor entirely:** delegate the review to Codex (`codex-consult` skill) so the
  judge shares none of your context or blind spots — the strongest form of independence. The
  git-sync hook audit that produced these skills did exactly this: Codex + an adversarial
  workflow, cross-checked.
- **Acting, not reading:** the reviewer runs tests and pastes real output; for UI it drives
  the page via the `claude-in-chrome` or `chrome-devtools-mcp` MCP and screenshots the result.
- **Adversarial verify pattern:** for each finding, spawn N skeptics prompted to REFUTE it;
  keep it only if a majority fail to refute. Diversity of lens (correctness / security /
  does-it-reproduce) beats N identical refuters.
- **Calibrate the evaluator before trusting it:** an evaluator need not be perfect — it only
  needs failure modes *uncorrelated* with the generator's. Prove it catches real, known bugs
  first, then trust it to gate.
- **Don't over-gate, either:** the discipline is "never delete the gate", not "make the gate
  ever-heavier until the loop can't move". Match gate cost to risk — full independent review
  for high-risk diffs (auth, billing, migrations, deletes); cheap machine gates (CI/lint/type)
  for genuinely low-risk ones (docs, typos). A loop frozen by infinite gating is its own failure.

This skill is the loop layer of the "check that can say no". For a single-task review against
a plan, use `requesting-code-review`; to gate your own success claims with evidence, use
`verification-before-completion`. This skill is when the *judge is structurally the wrong
agent* — i.e. the generator is about to judge itself.

## Rationalizations — and why each one fails

Captured from baseline runs (agents under deadline / sunk-cost / "user said it's fine"
pressure). These are the words a generator reaches for to grade itself softly. When you
hear yourself say one, that is the signal to bring in the independent evaluator.

| Rationalization | Reality |
|---|---|
| "Tests are green locally, so it's fine." | Local green is the **weakest** guarantee: the tests may be insufficient or wrong, CI differs, uncovered paths exist. Green from the author's own hands isn't an *evaluation* — generation and judgment are still the same agent. |
| "The user said 'review it yourself and merge if fine'." | That is **conditional** delegation — "if you've confirmed it's fine" — not permission to skip the confirming step. The author-as-reviewer setup violates separation itself. |
| "I wrote it, so I understand it / it's only a 120-line diff." | **Author bias.** A bug you missed while writing, you miss again while reviewing — same blind spot. Small diff ≠ small impact (120 lines of auth can escalate every user's privileges). Line count never licenses less skepticism. |
| "Deadline in 1 hour — no time to wait for another agent or a human." | Deadline pressure is the classic trigger. "Only 1 hour" is not a reason to drop the gate — it's a reason to make the gate efficient (parallel checks, split safe/risky parts, renegotiate with risk stated). If you truly can't, **stop and escalate** — don't ship unverified. |
| "We've succeeded N times, so drop the human checkpoint / auto-merge now." | **Survivorship bias + distribution shift.** All N successes happened *with the checkpoint in place*; they say nothing about safety once it's removed. Removing it changes the population of failure modes. Keep at least one human checkpoint. |
| "Auto-merge saves time." | The loop's inputs (CI/issues/commits) are an **attack surface** — a poisoned issue can drive a prompt-injection auto-merge. Human review is the main defense; auto-merge is irreversible and feeds the next round's input (compounding failure). Gain speed by *staging* (low-risk only, multiple machine gates, opt-in, capped), not by deleting the gate. |
| "CLAUDE.md says be obedient, so I should comply with removing the safety valve." | This is an **engineering risk judgment**, a different layer from obedience. Complying means letting the requester (the generator side) hold the stop decision too — the opposite of handing the stop check to a fresh independent judge. Obedience is satisfied by stating the risk and offering a safety-valve-preserving alternative. |
| "We've had no runaway yet, so add budget caps later." | "Not observed" ≠ "safe" — no history is expected on first launch. The cost (tokens, rate exhaustion, irreversible side effects) **completes before detection**, so "add it after a problem" is structurally impossible. Cap before shipping. |
| "Caps are a hassle; ship first." | Cost asymmetry: a cap is cheap and reversible; an unattended runaway is unbounded and irreversible. Right before unattended launch is the **only** correct time to set the ceiling. Tune the values later; start strict. |
| "While it's succeeding, extra guards are overhead." | The succeeding you observe is *guards-on* behavior; it says nothing about guards-off. Because rare-but-catastrophic failure is asymmetric, a cheap guard is always justified. Guards are released by **risk asymmetry**, never by a success streak. |
| "The evaluator is also an LLM, so it'll be wrong too — why trust it?" | It need not be perfect, only **uncorrelated** with the generator. A judge with different failure modes improves the expected outcome (the whole point of GAN / maker-checker). So make it a different model or vendor, and calibrate it on real known bugs before trusting it. "Imperfect" is not "useless". |
| "Quality here is subjective / can't be machine-checked, so there's no gate to place." | A fuzzy stop condition is a reason to **keep the human checkpoint**, not to drop the gate. Formalize what you can (build passes, no regression) into auto-gates; route what you can't into an inbox for a human. "Subjective" routes to a person, it does not route to auto-approve. |

## Red flags — STOP and bring in an independent evaluator

- You are about to approve/merge/stop on something **you generated**.
- The review is "me, in a follow-up turn" rather than a different agent/model.
- The evidence is "it should pass" / "this looks right" — not pasted run output.
- A loop has run many turns and **never once said "no"** to itself (statistically impossible
  for real work → proof no real check exists).
- You're reaching for any row in the table above.

**All of these mean: separate the judge, default it to doubt, make it act, let a fresh model decide.**
