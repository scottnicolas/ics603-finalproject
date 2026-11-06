---
name: pr-diagram
description: Use when a pull request is ready to open, is being opened, or an open pull request's description needs a new or updated change diagram.
---

# PR diagram

Add exactly one code-grounded Mermaid diagram of the change to the pull request description.

## Procedure

1. Read the repository's `AGENTS.md` **Changes** section, the current pull request title and body, and the diff against its base branch.
2. Choose a sequence diagram for interactions or a flowchart for component or process structure.

**Diagram contract:** Use at most eight boxes total (sequence participants or flowchart nodes); every box names a file or function in the pull request diff; verify every arrow against code at that pull request revision; keep labels and notes plain text on one line.

3. Preserve the existing `## Summary`, `## Test plan`, checklist states, and all other prose verbatim. Replace any existing Mermaid diagram block(s) with one diagram, or append a `## Change diagram` section with one fenced `mermaid` block if none exists.
4. Update the pull request description with `gh pr edit <number> --body-file <path>` using the complete revised body.
5. Read the body back with `gh pr view <number> --json body` and confirm there is exactly one diagram, the preserved prose is unchanged, and the diagram follows the Diagram contract.
