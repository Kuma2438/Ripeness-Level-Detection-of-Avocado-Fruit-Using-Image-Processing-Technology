---
name: quality-gate
description: >-
  Use this skill BEFORE declaring any task complete in this workspace — Python
  scripts, data work, plans, or documentation. It runs automated checks and a
  structured self-review, fixes issues found, and reports what was verified and
  what risks remain. Never say "done" without passing this gate.
---

# Quality Gate

Goal: catch mistakes before the user does. Verify with evidence, not assumptions.

## Step 1 — Run the checks for each work type touched

### Python scripts
Use tools if installed (check with `python -m <tool> --version`); do NOT install
new packages without asking. Fall back to the next option if missing.
1. Syntax: `python -m py_compile <file>.py`
2. Lint/format: `ruff check .` and `ruff format --check .` (fallback: `python -m pyflakes`)
3. Types (if code has type hints): `mypy <file>.py` or `pyright`
4. Tests: `python -m pytest -q` if tests exist. If none exist for new logic, add at
   least one test for the main path and one for an edge case.
5. **Actually run the script** on a realistic sample input and inspect the output.
6. Self-review the diff for:
   - unhandled errors (missing files, empty input, bad types, network failures)
   - hardcoded paths/secrets → use args, `pathlib`, or env vars
   - leftover `print` debugging, commented-out code, unused imports
   - clear names, docstrings on public functions, `if __name__ == "__main__":` entry point
   - new dependencies listed in `requirements.txt` / `pyproject.toml`

### Data work
1. **Raw data untouched** — originals not overwritten; outputs written to a separate path.
2. **Shape check** — row counts before/after each major step; explain every change in rows
   (filters, joins, dedups). Unexpected row growth after a join = bug until proven otherwise.
3. **Integrity** — nulls per column, duplicates on the key, dtypes as expected,
   values in valid ranges/categories, dates parsed correctly, time zones consistent.
4. **Sanity** — totals/aggregates reconcile with the source; spot-check 3–5 rows end-to-end by hand.
5. **Reproducibility** — the result can be regenerated from raw data by a script
   (not manual edits); random seeds fixed; steps documented.
6. **Conclusions** — every claim is supported by a number shown; note sample size,
   caveats, and correlation ≠ causation.

### Plans
1. Every goal has a measurable success metric.
2. Steps are ordered, with dependencies and owners/resources noted.
3. Risks listed with mitigations; assumptions stated explicitly.
4. Feasible within stated constraints (time, budget, skills, tools).
5. Nothing in scope is missing; nothing out of scope crept in.

### Documentation
1. **Accuracy** — every command, path, function name, and number checked against the
   actual code/data. Run every code example.
2. **Audience fit** — no undefined jargon; prerequisites stated up front.
3. **Structure** — clear headings, purpose in the first paragraph, steps numbered.
4. **Links** — all relative links/file references resolve.
5. **Completeness** — covers setup, usage, inputs/outputs, and common errors where relevant.

## Step 2 — Verify acceptance criteria
If a spec exists in `specs/` (from the `spec-first` skill), check every acceptance
criterion one by one and mark it `[x]` with evidence (command output, number, file).

## Step 3 — Fix and re-run
Fix every issue found, then re-run the affected checks. Repeat until clean.
If something can't be fixed, don't hide it — report it.

## Step 4 — Report to the user
End with a short report in this format:

```
## Quality Gate Report
✅ Verified: <checks that passed, with key evidence e.g. "pytest 12 passed", "rows 10,432 → 10,430 (2 duplicates removed)">
🔧 Fixed during review: <issues found and fixed>
⚠️ Not verified / risks: <what couldn't be checked and why; remaining caveats>
```
