# Parallel Agents — Isolation with Git Worktrees

<!--
  How to run MORE THAN ONE agent at a time in this repository without agents
  overwriting each other's work. The rule is simple: parallel work happens in
  separate git worktrees, never in the same checkout.

  Golden rule: one agent = one worktree = one branch. Sequential work stays in
  the main checkout — don't create a worktree for work that isn't parallel.
-->

## ⛔ The rule

**Never run two agents concurrently in the same working directory.**

If work is going to be done in parallel — you are spawning subagents, Erick asked
for several tasks "at the same time", or a second agent is already running in
this repo — **each agent MUST work inside its own git worktree, on its own
branch.**

Why: agents share one filesystem. Two agents editing the same checkout produce
half-applied edits, clobbered files, a `git status` that mixes unrelated
changes, and commits that capture another agent's work-in-progress.

**When NOT to use a worktree:** a single agent doing one task at a time. Stay in
the main checkout; worktrees add setup cost for no benefit — and in a 12h
hackathon window, that cost matters.

---

## Decision check — before spawning parallel work

1. **Will more than one agent write files at the same time?** No → main checkout. Yes → continue.
2. **Are the tasks truly independent** (different files, no shared migration, no ordering dependency)? No → sequence via [task-queue.md](task-queue.md). Yes → continue.
3. **Give each agent its own worktree.**

Read-only agents (search, review, audit — no writes) do **not** need a worktree.

---

## Protocol

```
main checkout  ──┬── .worktrees/feat-a   (agent A, branch feat/a)
                 └── .worktrees/feat-b   (agent B, branch feat/b)
```

### 1. Create one worktree per parallel agent

```bash
git fetch origin
git worktree add -b feat/task-a .worktrees/feat-task-a origin/main
```

- Branch name follows [`../coding_conventions.md`](../coding_conventions.md): `feat/`, `fix/`, `chore/`, `infra/`.
- Base off the shared base branch (`origin/main`), never off another agent's branch.
- Keep worktrees under `.worktrees/` at the repo root, git-ignored.

### 2. Brief each agent explicitly

Its absolute worktree path, its branch name, the exact scope of its task, and that it must never touch another agent's branch or the main checkout while parallel work is in flight.

### 3. Each agent commits on its own branch

### 4. Integrate sequentially, then clean up

```bash
git merge --no-ff feat/task-a
git worktree remove .worktrees/feat-task-a
git branch -d feat/task-a
```

---

## Shared state that worktrees do NOT isolate

| Shared resource | Risk | Handling |
|---|---|---|
| Dependencies (`node_modules`, `.venv`) | Not copied into a new worktree | Install per worktree |
| `.env` / local secrets | Untracked → missing in the worktree | Copy into each worktree |
| Dev server / DB ports | Two agents binding the same port | Distinct port per agent |
| Local database, seeds | Concurrent migrations corrupt shared state | One database per worktree, or serialise |
| Task tracker statuses (`tasks/`) | Duplicate/conflicting status updates | One agent per task |

If two tasks contend for anything above and it can't be split, they are **not** independent — run them sequentially.

---

## Checklist

- [ ] Parallel work is genuinely independent (else: sequence it).
- [ ] One worktree + one branch per writing agent, based on `origin/main`.
- [ ] `.worktrees/` is git-ignored.
- [ ] Each agent briefed with its path, branch, and scope.
- [ ] Shared resources (ports, DB) split or serialised.
- [ ] Branches integrated one at a time; worktrees removed after.
