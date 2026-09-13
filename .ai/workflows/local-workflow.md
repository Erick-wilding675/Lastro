# Project Management Workflow (Local Markdown)

<!--
  How the assistant reads and updates project management (tasks + docs) for
  this project. Adapted from the Síntese Method's notion-workflow.md — this
  project uses Local Markdown only, no Notion/MCP.
-->

## Storage mode

This project stores its docs and tasks in: **Local Markdown**, inside this vault, versioned in the private `talent-graph` GitHub repository.

Every project has the same two collections:

- **Documents Hub** — one entry per document produced by `project-kickoff.md` → [`../docs/documents-hub.md`](../docs/documents-hub.md).
- **Task Tracker** — one entry per task → [`../../tasks/`](../../tasks/) folder, one `.md` file per task.

## Documents Hub

A Markdown table mirroring: Doc name · Category · Local file · Status · Last updated. See [`../docs/documents-hub.md`](../docs/documents-hub.md). The document bodies are the `.ai/docs/**` files themselves.

## Task Tracker

One `.md` file per task, in `tasks/` (repo root). Put the schema fields in YAML front-matter and name the file with the ordering prefix so the folder sorts correctly.

### Task Schema (front-matter)

```yaml
status: "Not started"   # Not started / In progress / To test / ReFix / Done / Postpone
assignee: ""
due: ""
priority: ""            # High / Medium / Low
type: ""                # 🐞 Bug / 💬 Feature request / 💅 Polish
phase: ""
```

### Status lifecycle

| Status | Meaning | Who moves it next |
|---|---|---|
| `Not started` | Specced, not begun. | The assistant, when it picks the task up. |
| `In progress` | Being worked on **right now**. Set this *before* touching code. | The assistant, when the work is done. |
| `To test` | Implemented; awaiting human verification. | Erick, after testing. |
| `ReFix` | Tested and **failed**. The problems are written in the task's **"After tests"** section. | The assistant, by fixing what's listed there. |
| `Done` | Implemented **and** verified. | — terminal. |
| `Postpone` | Deliberately parked. Record *why* and what would unblock it. | Erick, when it becomes relevant again. |

Only Erick moves a task to `ReFix` or `Done` after verification — the assistant never self-certifies a task as tested.

### The "After tests" section

```markdown
## After tests

- [ ] {{What broke, with steps to reproduce or the wrong output observed}}
```

## Task Naming & Ordering

Task titles are **prefixed so that an alphabetical sort equals execution order**:

```
[Phase X] Task name
```

- `X` is the phase number, zero-padded (`[Phase 01]`, `[Phase 02]`, …).
- For epics: `[Epic] Epic name` (the epic) and `[Epic name X] Task name` (its tasks).
- The **same prefix rule applies to the filename**: `[Phase 01] Task name.md` — so a directory listing of `tasks/` sorts into execution order.

## Working on a Task

1. **Fetch the task** file to read the spec and deliverables.
2. **Set status to `In progress`** before starting work — before touching any code.
3. **If the status was `ReFix`,** read the **"After tests"** section first. Fix those items and check them off.
4. **Check off deliverables** as you complete each one (`- [ ]` → `- [x]`) — only if the task has a Deliverables section.
5. **Set status to `To test`** once the work is complete. Erick verifies and moves it to `Done` or back to `ReFix`.

## Closing a Bug Task

Before moving a `🐞 Bug` out of `In progress`, record in the task's **Plan** section: Root Cause, Solution (files changed), Result. Set status to `To test`.
