# Task Queue

Sequential task list. Process **top to bottom** — only start the next task after the current one is fully complete and committed.

> **Running tasks in parallel?** This queue is sequential by default. If a batch of tasks is demonstrably independent, each concurrent agent MUST get its own git worktree and branch. See [parallel-agents.md](parallel-agents.md).

> **Ordering:** tasks are named `[Phase X] Task name` (or `[Epic name X] Task name` for epics) per [local-workflow.md](local-workflow.md), so listing them **alphabetically by title yields execution order**. Keep this list in that order.

## How to process

For each task file below:

1. **Fetch** the task file to read the spec and deliverables.
2. **If the task status is `ReFix`:** find the **"After tests"** section — work on the problems described there.
3. **Follow [local-workflow.md](local-workflow.md)** to work on it (set status, implement, update deliverables/plan).
4. **Commit** all changes with a conventional commit message once the task is done.
5. **Mark the task as handled** below by changing `- [ ]` to `- [x]`. Note this tracks *your* pass through the queue — the task itself lands on `To test`, and only Erick promotes it to `Done`.
6. **Move to the next task.**

## Tasks

<!-- Seeded after kickoff (see project-kickoff.md → "After kickoff"). One line per task file, e.g.: -->
<!--
- [ ] tasks/[Phase 01] Task name.md
-->
