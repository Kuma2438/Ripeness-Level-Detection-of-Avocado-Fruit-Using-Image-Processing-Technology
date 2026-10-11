---
name: doc-craft
description: >-
  Use this skill when writing, updating, or maintaining project documentation,
  READMEs, CLI usage runbooks, or Architecture Decision Records (ADRs). Ensures
  docs match actual working code, verifies command examples, and logs technical
  trade-offs.
---

# Doc Craft: Reality-Synced Documentation & Decision Records

Ensures documentation is clear, accurate, and kept in sync with actual code and data behavior.

---

## Part 1: Reality-Synced Documentation & Runbooks

Never document theoretical code. Documentation must match executable reality.

### 1. Ground Truth Verification
- Before writing a command example, verify it runs (`python script.py --help` or run on sample input).
- Ensure all mentioned file paths, function signatures, and parameter flags actually exist in the codebase.
- Avoid broken links or placeholder copy (`TODO`, `<your-api-key-here>` without explanation).

### 2. Standard Runbook / README Structure
When documenting a tool, script, or pipeline, include:
1. **Overview & Purpose:** 1–2 sentences explaining what problem this script solves and who uses it.
2. **Prerequisites & Dependencies:** Required Python version and packages (e.g., `pip install -r requirements.txt`).
3. **Usage Examples:** Concrete, copy-pasteable terminal commands for common use cases:
   ```bash
   python process_data.py --input raw/data.csv --output cleaned/data.parquet
   ```
4. **Parameters Table:**
   | Flag / Option | Type | Default | Description |
   |---|---|---|---|
   | `--input`, `-i` | Path | *Required* | Path to input source file |
   | `--output`, `-o`| Path | `output.csv` | Destination path for processed data |
   | `--verbose` | Flag | `False` | Enable debug logging output |
5. **Expected Output:** Description of the generated files, schemas, or exit codes.
6. **Troubleshooting / FAQ:** 2–3 common error scenarios and how to resolve them.

---

## Part 2: Architecture Decision Record (ADR)

When making non-trivial technical or architectural decisions (e.g., choosing Polars vs Pandas, selecting SQLite vs JSON, restructuring pipeline storage):

Document the decision in `docs/decisions/<YYYY-MM-DD>-<decision-slug>.md` using this format:

```markdown
# ADR: [Decision Title]

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Deprecated
- **Context:** [What problem or requirement triggered this choice?]

## Considered Options
1. **Option A:** [Description]
2. **Option B:** [Description]

## Trade-off Analysis
| Criteria | Option A | Option B |
|---|---|---|
| Performance / Scalability | ... | ... |
| Complexity / Maintenance | ... | ... |
| Dependencies | ... | ... |

## Decision & Rationale
We chose **[Option X]** because [key reasons, e.g., zero external dependencies, native speed].

## Consequences
- **Positive:** [What do we gain?]
- **Negative / Risks:** [What limitations or trade-offs must we accept?]
```
