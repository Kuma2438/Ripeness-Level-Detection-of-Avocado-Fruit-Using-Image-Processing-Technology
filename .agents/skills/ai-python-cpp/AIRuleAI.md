# AI Development Rules — Python & C++

## Code Style
When modifying existing code, match the patterns already in the file.
If the file uses NumPy-style vectorized code, don't rewrite it as explicit loops.
If the file uses a specific tensor framework's idioms (PyTorch, JAX), don't mix in another framework's patterns.
Match the existing style, even if you'd do it differently.
Python: follow PEP 8, enforced via `ruff format` + `ruff check`. No manual style debates — the formatter is the source of truth.
C++: follow the project's `.clang-format`; if none exists, default to a documented style (e.g. Google C++ Style Guide) and stay consistent within a file.

## Abstractions
Do not create abstractions unless they reduce real, measurable complexity.
No interfaces/base classes with a single implementation.
No factory functions that produce one type.
No config objects for functions that take two arguments.
No wrapper classes that just delegate to another class or library call.
Three similar lines of code is better than a premature abstraction.
In C++: avoid template metaprogramming or CRTP unless the performance or type-safety win is measured and necessary. Prefer simple, readable code over "clever" generic code.

## Tests
Never modify existing tests unless the change intentionally updates the behavior they cover.
If a test fails after your change, that means YOUR change is wrong, not the test.
Fix your code to make the existing test pass.
For ML code: never adjust an assertion threshold, tolerance, or golden value just to make a test pass — investigate whether the model, data, or numerics actually changed and why.
Never mark a flaky or slow test as skipped to "get it green." Report it instead.

## Comments
Default to writing no comments.
Only add a comment when the WHY is non-obvious (e.g. a numerically unstable trick, a workaround for a library bug, a non-obvious algorithmic choice).
Never comment WHAT the code does — the code should say that.
Never reference the current task, ticket, or fix in a comment.
Docstrings are not comments: public functions, classes, and modules should have concise docstrings describing inputs, outputs, and side effects — especially shapes/dtypes for tensors and units for numeric values.

## Scope
Keep changes scoped to exactly what was requested.
Don't "improve" adjacent code, notebooks, or configs.
Don't refactor things that aren't broken.
Don't add features, flags, or CLI options that weren't asked for.
Don't retrain, re-tune, or change hyperparameters unless explicitly asked.

## Error Handling
Don't add error handling for scenarios that can't happen.
Trust internal function contracts and type hints.
Only validate at system boundaries: user input, API responses, file reads, model outputs, external data sources.
Python: raise specific exception types, never bare `except:`. Never silently swallow exceptions in data or training pipelines — a silently-corrupted batch is worse than a crash.
C++: never use raw pointers for ownership — use RAII (`unique_ptr`, `shared_ptr`, containers). Never ignore a return value that signals failure. Check array/tensor bounds only at trust boundaries, not on every internal hot-path access — but never silently truncate or wrap out-of-range values.

## Performance & Efficiency
Profile before optimizing — never guess at a bottleneck.
Python: vectorize with NumPy/PyTorch/Polars instead of explicit Python loops over data; avoid unnecessary `.item()`, `.cpu()`, or `.numpy()` calls that force synchronization or copies in tight loops.
Prefer batching over per-sample calls (data loading, model inference, DB/API calls).
Avoid unnecessary tensor copies, reshapes, or dtype casts — check `.contiguous()`/copy semantics before assuming an operation is free.
C++: prefer stack allocation and move semantics over unnecessary heap allocation and copies. Pass large objects by `const&`, not by value. Reserve container capacity when the size is known. Avoid premature micro-optimization that hurts readability without a measured gain.
Never introduce O(n²) or worse behavior in a path that's expected to scale — call this out explicitly if the only correct implementation is not linear.

## Scalability & Reliability
Design for the data size and load the system will actually see, not the toy example — but don't over-engineer for scale that isn't planned either.
Make operations idempotent wherever possible (safe to retry: data ingestion, checkpoint writes, job submission).
Long-running jobs (training runs, batch pipelines) must checkpoint and resume, not restart from scratch on failure.
Pin dependency versions (lockfiles) so runs are reproducible; never leave a floating `>=` version on a core numerical or ML dependency.
Seed all sources of randomness explicitly when reproducibility matters (Python `random`, NumPy, framework RNG, data shuffling).
Fail fast and loudly on bad input or NaN/Inf in numeric pipelines — don't let corrupted data silently propagate downstream.

## Stack (defaults — override with project specifics if given)
- **Python**: 3.12+
- **Package manager**: `uv` (not pip/poetry directly)
- **Lint/Format**: `ruff` (replaces flake8, black, isort)
- **Type checking**: `pyright` for editor/day-to-day, `mypy` in CI for broader plugin support
- **Testing**: `pytest` + `pytest-cov`
- **ML/data**: PyTorch (or the framework already in the repo), NumPy, Polars/Pandas
- **C++ standard**: C++20 unless the project pins an older standard
- **C++ build**: CMake
- **C++ testing**: GoogleTest / Catch2
- **C++ formatting/linting**: `clang-format` + `clang-tidy`

## Project Structure
- `src/` or package dir — library code
- `scripts/` — one-off or CLI entry points, not imported by the library
- `notebooks/` — exploration only; nothing production-critical should live only in a notebook
- `tests/` — mirrors the source tree
- `configs/` — YAML/JSON/TOML configs for experiments and pipelines, not hardcoded constants in code
- C++: separate `include/` (public headers) from `src/` (implementation); one class per file pair unless tightly coupled.

## Naming Conventions
- Python files/functions/variables: `snake_case`; classes: `PascalCase`; constants: `SCREAMING_SNAKE_CASE`
- C++ files: match project convention (commonly `snake_case.cpp/.hpp`); classes: `PascalCase`; functions/variables: project convention, stay consistent within the file
- Test files: `test_*.py` / `*_test.cpp`, mirroring the source file name
- Tensors/arrays: name variables with shape or meaning hints when not obvious (`logits`, `batch_size`, not `x1`, `tmp`)

## Imports & Dependencies
Prefer absolute imports within a package.
Don't add a new dependency for something a few lines of code can handle.
Don't add a new dependency when an existing one already covers the use case.
Any new heavy dependency (a new ML framework, a new serialization format) should be flagged explicitly, not added silently.
C++: prefer the standard library over a third-party dependency when it's sufficient; justify any new external library in the summary of changes.

## Data & Model Handling
Never commit large binary artifacts (datasets, model checkpoints, weights) directly to git — use the project's existing artifact/storage mechanism (DVC, LFS, object storage) if one exists; flag it if none does.
Never silently change a model's architecture, loss function, or preprocessing without calling it out — these are behavior changes, not implementation details.
Keep training/inference code path parity: a preprocessing change made for training must be reflected in inference, and vice versa.
Log and version experiment configs alongside results; don't leave "which config produced this" ambiguous.

## Verification
After making changes, run these before reporting done:
- Python: `pytest`, `ruff check`, `ruff format --check`, `pyright` (or `mypy`)
- C++: build with warnings-as-errors, run `ctest`, run `clang-tidy`
If any fail, fix the issue first — don't report done with a known failure.

## Security
Never commit `.env` files, API keys, tokens, or credentials.
Never log sensitive data (raw user input, PII, secrets) — including inside model prompts/responses that get logged for debugging.
Never put secrets in comments, test fixtures, or example configs.
Validate any input that reaches a model prompt, a shell command, or a raw SQL string — treat model-generated output as untrusted input if it flows into another system.

## Git
Use conventional commit format: `type(scope): description`.
Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`.
Keep commits focused on one change.
Don't mention AI or "generated" in commit messages.

## Communication
When done, explain what you changed and why in 2-3 sentences.
If you found something unexpected (a bug, a data issue, a numerical instability), mention it — don't fix it silently unless it's in scope.
If you made a judgment call (a chosen batch size, a tolerance value, a data structure trade-off), explain your reasoning.
If a performance or scalability trade-off was made, state it explicitly rather than leaving it implicit.
