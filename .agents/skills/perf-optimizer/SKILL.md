---
name: perf-optimizer
description: >-
  Use this skill when optimizing Python code, algorithms, or data pipelines for
  execution speed and memory efficiency. Identifies bottlenecks, audits Pandas
  anti-patterns (loops, iterrows), downcasts data types, introduces chunking,
  and profiles runtime and memory usage.
---

# Perf Optimizer: Python & Data Performance Engineering

Standard operating procedures for eliminating bottlenecks, minimizing RAM usage, and accelerating Python execution.

---

## 1. Measure First (Profile, Don't Guess)

Never optimize blindly. Always measure baseline before and after changes.

1. **Wall-Time Profiling:**
   - Use Python's `time.perf_counter()` or `timeit` for targeted execution timing.
   - For function-level bottlenecks, use `cProfile`:
     ```powershell
     python -m cProfile -s cumulative script.py
     ```
2. **Memory Footprint Inspection:**
   - Inspect DataFrame memory usage:
     ```python
     df.info(memory_usage="deep")
     ```
   - For overall process memory, trace allocations with standard library `tracemalloc`:
     ```python
     import tracemalloc
     tracemalloc.start()
     # code ...
     current, peak = tracemalloc.get_traced_memory()
     print(f"Peak memory: {peak / 10**6:.2f} MB")
     tracemalloc.stop()
     ```

---

## 2. Eliminate Data Anti-Patterns

### 1. Ban Iterative Row Loops in Pandas
- **Strictly Avoid:** `for index, row in df.iterrows():`, `.itertuples()`, or slow `.apply(axis=1)` where vectorized logic exists.
- **Replace With:**
  - Native vectorized series math: `df["total"] = df["qty"] * df["price"]`
  - NumPy boolean indexing: `np.where(condition, x, y)`
  - Dictionary mapping: `df["category"] = df["code"].map(mapping_dict)`

### 2. High-Performance GroupBy & Aggregations
- Filter rows *before* grouping, not after.
- Compute only needed columns: `df.groupby("dept")["salary"].mean()` instead of `df.groupby("dept").mean()["salary"]`.

---

## 3. Memory Optimization & Type Downcasting

Cut RAM consumption by up to 50–80%:

1. **Numeric Downcasting:**
   - Convert default 64-bit numbers to smaller footprints when range allows:
     ```python
     # Integers: int64 -> int32 or int16
     # Floats: float64 -> float32
     df["int_col"] = pd.to_numeric(df["int_col"], downcast="integer")
     df["float_col"] = pd.to_numeric(df["float_col"], downcast="float")
     ```
2. **Categorical Types:**
   - Convert repeated low-cardinality text columns (e.g., status, country, category) to `category`:
     ```python
     df["status"] = df["status"].astype("category")
     ```
3. **Explicit Garbage Collection:**
   - Delete large interim structures and trigger collection when processing massive stages:
     ```python
     del raw_data
     import gc; gc.collect()
     ```

---

## 4. Chunking & Streaming for Large Datasets

When data approaches or exceeds available system memory:

1. **Chunked Reading:**
   - Never load entire multi-gigabyte files at once. Process in manageable batches:
     ```python
     chunk_size = 50_000
     for chunk in pd.read_csv("large_file.csv", chunksize=chunk_size):
         process(chunk)
     ```
2. **Streaming Iterators:**
   - Use Python generator functions (`yield`) rather than accumulating large lists in memory.

---

## 5. Performance Report Standard

Always conclude performance optimization with an evidence card:
```
## Performance Optimization Report
⚡ Execution Time: <Before>s -> <After>s (<X>x speedup)
💾 Peak Memory: <Before>MB -> <After>MB (<Y>% reduction)
🔧 Key Changes: <e.g., replaced iterrows with vectorized np.where, downcasted float64 to float32>
```
