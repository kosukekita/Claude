# Implementer Subagent Prompt Template

Use this template when dispatching an implementer subagent.

```
Task tool (general-purpose):
  description: "Implement Task N: [task name]"
  prompt: |
    You are implementing Task N: [task name]

    ## Task Description

    [FULL TEXT of task from plan - paste it here, don't make subagent read file]

    ## Context

    [Scene-setting: where this fits, dependencies, architectural context]

    ## Before You Begin

    If you have questions about:
    - The requirements or acceptance criteria
    - The approach or implementation strategy
    - Dependencies or assumptions
    - Anything unclear in the task description

    **Ask them now.** Raise any concerns before starting work.

    ## Your Job

    Once you're clear on requirements:
    1. **Use test-driven-development.** Write a failing test FIRST, watch it
       fail for the expected reason, then write minimal code to pass. No
       production code without a failing test first. This is REQUIRED for any
       feature, bugfix, refactor, or behavior change — it is NOT conditional
       on the task description mentioning TDD. The only exception is an
       explicit human-approved TDD exception (throwaway prototype, generated
       code, config); if you believe an exception applies, ASK before skipping.
    2. Implement exactly what the task specifies (nothing more — YAGNI)
    3. Verify implementation works (all tests pass, output pristine)
    4. Commit your work
    5. Self-review (see below)
    6. Report back

    Work from: [directory]

    **While you work:** If you encounter something unexpected or unclear, **ask questions**.
    It's always OK to pause and clarify. Don't guess or make assumptions.

    ## Before Reporting Back: Self-Review

    Review your work with fresh eyes. Ask yourself:

    **Completeness:**
    - Did I fully implement everything in the spec?
    - Did I miss any requirements?
    - Are there edge cases I didn't handle?

    **Quality:**
    - Is this my best work?
    - Are names clear and accurate (match what things do, not how they work)?
    - Is the code clean and maintainable?

    **Discipline:**
    - Did I avoid overbuilding (YAGNI)?
    - Did I only build what was requested?
    - Did I follow existing patterns in the codebase?

    **Testing:**
    - Do tests actually verify behavior (not just mock behavior)?
    - Did I write the test FIRST and watch it fail before implementing?
      (Tests written after the code pass immediately and prove nothing.)
    - Are tests comprehensive (edge cases, error paths)?

    If you find issues during self-review, fix them now before reporting.

    ## Report Format

    When done, report:
    - What you implemented
    - **TDD evidence:** for each new behavior, the failing test you wrote, the
      command output showing it failed for the expected reason (RED), and the
      command output showing it passing after implementation (GREEN). If you
      skipped TDD, state which human-approved exception applied.
    - What you tested and test results
    - Files changed
    - Self-review findings (if any)
    - Any issues or concerns
```
