---
name: loop-engineering
description: Use when designing, building, or reviewing a self-running loop / automation that runs an agent over and over without a human in the inner cycle — a scheduled triage, an overnight sweep, a /loop or /goal, a cloud routine, or a pipeline that opens PRs on its own. Use before shipping such a loop to check it has all five moves and isn't one of the five failure shapes. Trigger phrases: 自走ループ, ループを作る, 毎朝動かす, スケジュール実行, loop engineering, /loop, /goal, automation, cron agent, overnight loop.
---

# Loop Engineering — Build Loops That Run Themselves (and Can Be Stopped)

## Overview

Loop engineering is one floor above the harness: the harness arms a single agent run;
the loop makes it run **over and over** on its own. You stop being the human clock inside
the loop and become the person who designs the loop.

**Core principle:** Loops make generation nearly free; **judgment becomes the scarce
resource.** The hard part is never building the loop — it's putting something inside it
that can say "no". The same loop, built by two people, yields opposite outcomes; the
difference is one or two checkpoints.

> The cost of a mistake scales with the number of turns it survives before someone catches
> it — and a loop is, by construction, a machine for maximizing that number. Everything below
> exists to shorten the distance between a mistake and its discovery.

## The five moves of one turn

Drop any one and the loop won't turn, or turns in place.

| Move | What it does | Runs on (part) |
|---|---|---|
| **Discovery** | Find this turn's work *on its own* (read CI/issues/commits) — don't hand it a list | a **skill**, not a wall of cron text |
| **Handoff** | Hand the task off, isolated, so parallel agents don't collide | a **worktree** per task |
| **Verification** | Swap in another agent to say "no" — the hardest, least-skippable move | **sub-agents** (generator ≠ judge) |
| **Persistence** | Write state *outside* the conversation so tomorrow resumes | **memory** on disk (markdown/board) |
| **Scheduling** | Make it turn round after round | **automations** (timer/trigger) |

The sixth part, **connectors** (MCP), decides the loop's radius of vision — issue tracker,
DB, staging API, Slack.

## The five ways a loop goes wrong (each is one move skipped)

- **Nodding loop** (verification skipped): writes code, same agent declares it good,
  accumulates plausible mistakes at machine speed. *Tell:* never once said "no" in hundreds
  of turns. → Fix with **loop-evaluator** (generator/evaluator split).
- **Amnesiac loop** (persistence skipped): forgets what it did; each morning starts over.
  *Tell:* no cumulative progress. → state file on disk.
- **Manual loop** (scheduling skipped): four good moves but a human runs it by hand and
  forgets. *Tell:* last run was the demo day. → a real timer/event trigger.
- **Blind loop** (discovery skipped): human still hands it the work each morning. *Tell:*
  you still spend the morning deciding what it should do. → teach discovery into a skill.
- **Tangled loop** (handoff skipped): parallel agents edit the same dir, edits collide.
  *Tell:* fine with one agent, breaks the first morning five run at once. → one worktree per task.

## First-loop checklist (the first two decide if it runs; the last four decide if it stays safe)

| Element | Ask yourself |
|---|---|
| Discovery source | What does it read on a timer? (CI / issues / commits / inbox) |
| State file | Which disk file holds the cross-round memory? |
| **Evaluator** | Is there an **independent** check that can say "no"? (→ loop-evaluator) |
| Isolation | Does each parallel agent get its own worktree? |
| Token cap | Did you set a per-run / per-day / max-retry ceiling **before** shipping? |
| Human review | Which step pauses for you — rather than auto-ing all the way through? |

Beginners ship with only the first two and get a loop nobody watches and nobody can stop.
A first loop is better small — but with the "no"-saying check and the human review point
fully installed.

## A complete first loop, annotated

```yaml
# 1. SCHEDULING — a real trigger (cloud so the lid can close)
on: { schedule: [ cron: '0 6 * * *' ] }    # 06:00 daily
# 2. DISCOVERY — a skill, not a wall of text
run: claude --skill morning-triage
# 3. PERSISTENCE — the skill writes ./state/triage.md and commits it back
# 4. HANDOFF — one worktree per finding
#    for finding in $(parse ./state/triage.md):
#        claude --worktree "fix/$finding" --goal "tests pass and lint clean" "draft a fix for $finding"
# 5. VERIFICATION — /goal's stop check after each turn + a loop-reviewer agent picks holes
# 6. HUMAN REVIEW — PRs opened, never auto-merged; anything uncertain lands in ./inbox/
```

The discovery skill's own headings should map to the five moves, plus one heading the loop
**cannot infer** and you must write in by hand:

```
## Stop (the boundary you keep for yourself)
Never merge. Never delete. Anything you're less than confident about goes to ./inbox/
for a human, not into a PR.
```

## Scheduling: local vs cloud (follows mechanically from one question)

Is the work glued to the local machine, or can it leave?

| | Machine on? | Session open? | Min interval | Sees local files? |
|---|---|---|---|---|
| **Cloud** (Routines / CI cron) | no | no | ~1h | no |
| **Desktop** scheduled task | yes | no | ~1 min | yes |
| **/loop** | yes | yes | ~1 min | yes |

Must check a local dev server every minute → local. Should scan issues at 3am and open PRs →
cloud/CI (laptops get their lids closed). A mature loop uses both: local for tight inner
checks, cloud for the overnight sweep. **Do not** mistake local rerun ("run a few extra
rounds while I'm here") for true autonomy ("run while I'm not"). `/loop` reruns on an
interval; `/goal` runs until a condition is met (judged by a fresh model — see loop-evaluator).

## The four silent debts — and the guard for each

They run up while the loop runs, sound no alarm, reinforce each other, and come due at once.

| Debt | What accrues | Guard |
|---|---|---|
| **Verification debt** | unverified output between "runs" and "right" | an independent evaluator (loop-evaluator) |
| **Comprehension rot** | code you didn't write outpaces your mental map | read a **sample daily**, force yourself to explain each change |
| **Cognitive surrender** | you stop having an opinion, take whatever it hands back | one human checkpoint — the loop can execute, it cannot **decide** |
| **Token blowout** | helpers + retries spin idle all night → a surprise bill | hard caps set **before** shipping (per-run, per-day, max-retry) |

## Grow it safely

Add parallelism **last**, after the checks are proven. Increase what it discovers before
increasing how much it does in parallel. Prove the evaluator catches real mistakes before
trusting it to gate many agents. A loop earns the right to run more agents by first
demonstrating it can stop a single bad one. (Stripe's 1,300-PR/week pipeline is the
*endpoint* of this path, not the entry — its reliability comes from years of hardening
deterministic gates, not from a bigger model.)

## The posture that decides the outcome

Build the loop, but build it like someone who intends to **stay the engineer**, not just
the person who presses go. A loop is a faithful multiplier of whatever you bring: bring
understanding and it amplifies understanding; bring laziness and it amplifies laziness.
Two loops 90% identical in code differ by one or two checkpoints — and those decide whether,
six months out, you stand on top of the loop or are hollowed out by it.
