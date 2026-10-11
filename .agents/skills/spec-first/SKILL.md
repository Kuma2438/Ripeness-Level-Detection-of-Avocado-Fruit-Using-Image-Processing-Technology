---
name: spec-first
description: >-
  Use this skill BEFORE starting any non-trivial task in this workspace: writing or
  changing a Python script, data analysis/cleaning/transformation, creating a plan,
  or writing documentation. It makes the agent write a short spec, surface
  assumptions, and get user confirmation before doing the work. Skip only for
  one-line fixes or pure questions.
---

# Spec First

Goal: build the *right* thing. Understand the task fully and agree on "done" before working.

## Steps

1. **Explore context first** (don't ask what you can look up):
   - Read related files, existing scripts, data samples (`head`, schema, row count), and prior specs in `specs/`.
   - For data: inspect columns, dtypes, null counts, and a few sample rows.

2. **Write the spec** to `specs/<YYYY-MM-DD>-<short-slug>.md` using
   [spec_template.md](./resources/spec_template.md). Fill in only the sections
   that apply to the task type (Python / Data / Plan / Doc).

3. **List assumptions and open questions explicitly.** Each one must be either:
   - a question for the user, or
   - an assumption with the default you'll use if the user doesn't object.

4. **Ask the user to confirm** — present a short summary (goal, acceptance criteria,
   open questions). Ask questions in one batch; don't drip them. Do NOT start
   implementing until the user confirms or says "go".

5. **Update the spec** with the user's answers. Set `Status: Approved`.

6. **Implement**, following the spec. If you discover the spec is wrong or
   incomplete mid-way, stop, update the spec, and tell the user what changed and why.

7. **Finish with the `quality-gate` skill**, verifying every acceptance criterion in the spec.
   Then set `Status: Done` in the spec.

## Rules

- Acceptance criteria must be **checkable** (a command, a number, a file, a yes/no check) —
  not vague ("works well", "clean data").
- Keep specs short: ~1 page. A spec is a thinking tool, not a deliverable.
- Small follow-up changes can append a "Change log" entry to the existing spec instead of a new file.
