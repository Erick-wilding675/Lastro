# Project Kickoff — Guided Document Generation

<!--
  THE STARTING POINT for a brand-new software project built with this template.
  This workflow tells the AI how to interview the user and produce the core
  Software Engineering documents, in order, saving each to the chosen storage.

  Golden rule: ONE document at a time. Interview → draft → get the user's
  sign-off → save → only then move to the next. Never invent facts to fill a
  gap — if you lack information to write a section safely, STOP and ask.
-->

> **Talent Graph — current status:** Step 0–3 done. Step 4 (Architecture + Matching Model) drafted — backend (Python/FastAPI), frontend (React), Neo4j integration, agent/function split, weights and explanation persistence all decided; only hosting is still open (depends on what the IBM ecosystem offers on hackathon day). Step 5 (Design Doc) not started. `harness.md` and `docs/edital-e-avaliacao.md` were pre-filled outside this flow because their content was already fixed (Erick's own stated framework; the hackathon's own rules) — everything else below still goes through the full interview.
>
> **Narrative rule (10/09, important for the pitch):** never describe Talent Graph as just "an explainable squad recommendation." It's a continuous management/learning/organizational-culture process; squad recommendation is one output of it, not the product's identity. See `ai.md` hard rule 10.
>
> **Known gap:** the hackathon scores "Arquitetura de Negócios & Custos" at 20% — none of the seven documents below covers a business model / cost document. Flag this during Step 1 or Step 4 and decide where it lives (see `docs/edital-e-avaliacao.md`).

## ⛔ How to run this — READ BEFORE DOING ANYTHING

This is an **interactive interview**, not a batch job. The failure mode to avoid:
reading this file and then generating every document in one go, inventing the
answers (especially the tech stack). **Do not do that.**

**The run protocol — non-negotiable:**

1. **One step per turn.** Do the current step, then **stop and wait** for the
   user. Never run ahead to the next document in the same turn.
2. **Ask, then WAIT.** For each step, ask that step's questions (in small
   batches — a wall of 15 questions is as bad as asking none). **End your turn
   and wait for the user's answers.** Do not draft the document until they reply.
3. **Never assume, never dictate.** You may *recommend* with rationale, but every
   decision the user hasn't made — **especially the tech stack, framework,
   hosting, and architecture** — must be **presented as options and chosen by
   the user.** Picking a stack for them is a bug, not a convenience. If unsure
   whether something is decided, ask.
4. **Get an explicit "approved"** on each drafted document before moving on.
   Silence is not approval.
5. **When in doubt, stop and ask.** Missing information is a reason to pause, not
   to invent.

If you catch yourself about to produce multiple documents at once, or writing a
stack/architecture choice the user never made — **stop and ask instead.**

---

## What this is

A step-by-step protocol for turning an idea into a documented software project.
You (the AI) act as a senior engineer + architect running a structured intake.
For Talent Graph, much of the raw material already exists in `Tese-Talent_Graph_IBM.pdf`
and `Resumo-Tecnico-Talent_Graph_IBM.pdf` — use it to make the interview faster
(don't re-ask what's already answered there), but still confirm scope decisions
for the hackathon MVP explicitly; don't silently adopt the Tese's long-term vision
as the MVP scope.

You produce **documents in a fixed order**, each building on the last:

| # | Document | Local template | Produces |
|---|---|---|---|
| 1 | **System Description** | [docs/system-description.md](../docs/system-description.md) | The wide-angle picture: what, who, why |
| 2 | **Software Requirements Specification (SRS)** | [docs/SRS.md](../docs/SRS.md) | What it must do + how it must behave |
| 3a | **Use Cases & User Flows** | [docs/use-cases.md](../docs/use-cases.md) | Actors, use cases, diagrams, workflows |
| 3b | **Data Model** | [docs/data-model.md](../docs/data-model.md) | Talent Model / Project Genome as entities, schema, types |
| 3c | **Wireframes** | [docs/wireframes.md](../docs/wireframes.md) | Low-fidelity screens per target device (skip if no UI — confirm first) |
| 4 | **Architecture + Matching Model** | [../architecture.md](../architecture.md) + [docs/ARD.md](../docs/ARD.md) + [docs/matching-model.md](../docs/matching-model.md) | Stack, services, data flow, infrastructure, matching logic |
| 5 | **Design Doc** | [docs/design-doc.md](../docs/design-doc.md) + [../ui_guidelines.md](../ui_guidelines.md) | Visual system, components, pitch material (if applicable) |

Documents 3a–3c are the **modeling phase** and are produced together, in that
sub-order, after the SRS is signed off.

---

## Ground rules (apply to every step)

1. **One document at a time, one step per turn.** Do not start — or draft — the
   next document until the current one is interviewed, drafted, reviewed by the
   user, and saved. Never emit several documents in a single turn.
2. **Interview first, write second — and WAIT.** Ask the step's questions, then
   end your turn and wait for answers. Do not draft from assumptions. Ask
   follow-ups whenever an answer is vague, contradictory, or incomplete.
3. **Never invent; never dictate decisions.** If the user hasn't decided
   something, ask — or record it as an **Open Question** rather than guessing.
   **Tech stack, frameworks, hosting, and architecture are the user's decisions**
   — present options with a recommendation and let them choose. Flag every
   assumption explicitly.
4. **Each doc builds on the prior ones.** Re-read the earlier documents (and the
   Tese/Resumo Técnico) before drafting; keep terminology, actor names, and
   entity names consistent — especially the Talent Model / Project Model /
   Matching Model vocabulary already fixed in the Tese.
5. **This project is Local Markdown — one copy.** The `.ai/**` file *is* the
   source of truth; there is no external store to sync.
6. **Diagrams are ASCII by default.** A plain ASCII/box sketch inside a fenced
   block is the standard — it renders everywhere, including in Obsidian.
7. **Register every document** in [docs/documents-hub.md](../docs/documents-hub.md)
   as soon as it is saved.
8. **Get an explicit "approved"** from the user before advancing. Offer to
   revise; do not assume silence is approval.

---

## Step 1 — System Description

**Goal:** a wide, non-technical description of the whole system so everyone
shares the same mental model before requirements are pinned down.

**Interview — ask the user, tailored to what the Tese already answers:**
- Confirm in one sentence what Talent Graph is *for this hackathon's MVP*
  (the Tese's long-term vision is broader than 12h of build — what's the slice?).
- Problem & value: the Tese already frames this well — confirm it's the framing
  to use, or adjust.
- Who are the users/actors for the MVP specifically? (the Tese's audience is
  broad — orgs, project leads, team members; who does the MVP actually serve?)
- Top 3–5 goals the MVP must achieve.
- Scope: what's genuinely buildable in 12h vs. what's narrative-only for the pitch?
- Constraints already fixed (beyond the 12h and the IBM stack)?
- What does success look like for the hackathon specifically (not the long-term
  vision)?

**Produce:** fill [docs/system-description.md](../docs/system-description.md).
Capture unknowns as Open Questions.

**Save & register**, get approval, then continue.

---

## Step 2 — Software Requirements Specification (SRS)

**Goal:** turn the description into concrete, testable requirements.

**Interview — ask the user:**
- Feature by feature, what will the MVP *do*?
- Which features are **must-have for the hackathon demo (MVP)** vs. **later (Post-MVP)**?
- Behavioural / non-functional needs — performance, availability, security &
  privacy (the Talent Model handles personal data — probe this specifically),
  scalability, accessibility.
- Hard constraints? What is explicitly **out of scope** for the 12h?

**Produce:** fill [docs/SRS.md](../docs/SRS.md).

**Save & register**, get approval, then continue to the modeling phase.

---

## Step 3 — Modeling phase

### 3a — Use Cases & User Flows

Interview only what the SRS didn't already answer. Produce [docs/use-cases.md](../docs/use-cases.md).

### 3b — Data Model

This is where the Talent Model and Project Genome (Tese, sections II–III) become
schema. Interview should confirm which fields make the MVP cut, not re-derive the
dimensions from scratch. Produce [docs/data-model.md](../docs/data-model.md).

### 3c — Wireframes

**First confirm whether the MVP has its own UI at all**, or is demonstrated
through watsonx Orchestrate / a notebook / an API + slides. Skip this step if
there's no UI. Produce [docs/wireframes.md](../docs/wireframes.md).

**Save & register** each modeling doc, get approval, then continue.

---

## Step 4 — Architecture + Matching Model

**Goal:** how the system is built, and how the Matching Model (Tese, section IV)
gets implemented for the MVP.

**Interview — ask the user (propose options; recommend, don't dictate):**
- Stack beyond watsonx Orchestrate + IBM Bob: language/framework, data stores,
  API style.
- Matching Model scope: Level 1 + 2 only, or Level 3 (portfolio) too?
- Initial weights for the scoring dimensions (the Tese is explicit these are
  hypotheses, not fixed).
- Hosting/infra realistic for a 12h build.

**Produce:**
- Fill [../architecture.md](../architecture.md).
- Fill [docs/matching-model.md](../docs/matching-model.md) — confirm/replace the
  `{{TBD}}` weights and scope already sketched there.
- Log each significant decision in [docs/ARD.md](../docs/ARD.md).

**Save & register**, get approval, then continue.

---

## Step 5 — Design Doc

**Goal:** visual system and pitch material — requires user decisions on look & feel.

Offer design-system options (Carbon/IBM is a natural fit given the ecosystem, but
don't assume it — ask). Produce [docs/design-doc.md](../docs/design-doc.md) and
[../ui_guidelines.md](../ui_guidelines.md).

**Save & register**, get approval.

---

## After kickoff

Once all documents are approved and saved:

1. Fill [../coding_conventions.md](../coding_conventions.md) from the architecture choices.
2. Seed the **Task Tracker** (`tasks/`) with the first implementation tasks and
   list them in [task-queue.md](task-queue.md). Name every task per the **Task
   Naming & Ordering** convention in [local-workflow.md](local-workflow.md).
3. Hand off to the normal build loop: pick tasks top-to-bottom per
   [local-workflow.md](local-workflow.md).

The project is now fully specified and ready to build.
