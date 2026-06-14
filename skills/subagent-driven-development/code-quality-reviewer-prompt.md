# Code Quality Reviewer Prompt Template

Use this template when dispatching a code quality reviewer subagent.

**Purpose:** Verify implementation is well-built (clean, tested, maintainable)

**Only dispatch after spec compliance review passes.**

```
Task tool (general-purpose subagent):
  Use template at requesting-code-review/code-reviewer.md

  WHAT_WAS_IMPLEMENTED: [from implementer's report]
  PLAN_OR_REQUIREMENTS: Task N from [plan-file]
  BASE_SHA: [commit before task]
  HEAD_SHA: [current commit]
  DESCRIPTION: [task summary]

  ADDITIONAL_CHECKS: |
    Verify TDD was actually followed, not just claimed:
    - Does every new behavior have a test?
    - Do the commits/report show the test existed and FAILED before the
      implementation (RED), not added afterward as an afterthought?
    - Are tests verifying real behavior, not mock behavior or the
      implementation's own shape (tests-after bias)?
    Flag as an Important issue if tests appear to be written after the code
    (passing-immediately tests prove nothing) or if TDD evidence is missing
    from the implementer's report.
```

**Code reviewer returns:** Strengths, Issues (Critical/Important/Minor), Assessment
