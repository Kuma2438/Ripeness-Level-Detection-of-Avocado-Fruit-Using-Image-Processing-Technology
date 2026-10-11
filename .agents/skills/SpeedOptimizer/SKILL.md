---
name: SpeedOptimizer
description: Full-stack performance planning and acceleration engine for Python backends, Web frontends, Local AI inference (quantization, VRAM, batching), and Vector/SQL databases. Enforces profiling, interactive hybrid planning, user trade-off selection, and benchmarked execution.
---

# SpeedOptimizer: Software, Web & Local AI Performance Engine

When this skill is activated (e.g., user says *"optimize it"*, *"speed up"*, *"เปิดโหมด optimize"*, *"boost performance"*, *"make it faster"*, or *"use SpeedOptimizer"*), **you MUST strictly follow the 4-Phase Performance Engineering Protocol below** on EVERY turn for the remainder of this session until explicitly deactivated.

---

## 1. Lifecycle & State Management

- **Status:** **ACTIVE** once invoked or enabled.
- **Duration:** Persists across all subsequent user requests in the session.
- **Deactivation:** Only disable these constraints if the user explicitly says:
  `"stop optimize"`, `"ปิดโหมด optimize"`, `"disable SpeedOptimizer"`, or `"exit optimize"`.
- **Deactivation Output:** `[SpeedOptimizer deactivated. Returned to standard development mode.]`

---

## 2. The 4-Phase Optimization Protocol (Never Skip Planning)

```mermaid
flowchart LR
    A["Phase 1: Profile & Diagnostic"] --> B["Phase 2: Hybrid Interactive Plan"]
    B --> C["Phase 3: User Trade-off Decision"]
    C --> D["Phase 4: Execution & Benchmark"]
```

### Phase 1: Deep Profiling & Root-Cause Diagnosis
Never guess bottlenecks or apply blind refactors.
1. Inspect the codebase, profiles, or run non-intrusive lightweight benchmarks to identify the true hot paths:
   - **CPU / Compute Bound:** High loop complexity, unvectorized loops, synchronous blocking operations.
   - **Memory / VRAM Bound:** Large model weight footprint, memory leaks, uncompressed tensors, lack of generator streaming.
   - **I/O & Network Bound:** Slow database queries, N+1 query problems, non-async HTTP calls, missing caching.
   - **Frontend & Rendering:** Oversized JavaScript bundles, excessive re-renders, uncompressed assets, blocking scripts.

---

### Phase 2 & 3: Hybrid Interactive Planning (Plan Artifact + User Choice)
Before making intrusive code modifications:

1. **Create a Performance Plan Artifact** (`performance_plan.md`) summarizing:
   - **Current Baseline / Bottleneck Analysis:** What is slowing things down and why.
   - **Proposed Optimization Tiers:**
     - **Tier 1 (Safe / Quick Wins):** Zero-risk optimizations (caching, query indexing, async conversions, asset minification).
     - **Tier 2 (Architectural / Algorithmic):** Restructuring data pipelines, batching, multiprocessing, Web Worker offload.
     - **Tier 3 (Aggressive / High-Impact Trade-offs):** Model quantization (FP16 -> INT8/INT4/GGUF), lossy compression, architectural re-write.
   - **Estimated Performance Gain & Trade-offs:** Latency vs. RAM/VRAM vs. Accuracy/Quality.

2. **Present Choices to the User**:
   - Ask the user which optimization tiers or specific strategies they want to prioritize before executing changes.

---

### Phase 4: Domain-Specific Execution & Best Practices

#### A. Local AI & Model Inference Optimization
- **Quantization & Formats:** Switch heavy FP32/FP16 models to GGUF (Q4_K_M, Q5_K_M), AWQ, or INT8/INT4 for dramatic VRAM/RAM savings and faster token generation.
- **Inference Accelerators:** Leverage `onnxruntime-gpu`, TensorRT, `vLLM` PagedAttention, or `llama.cpp` AVX/GPU offloading.
- **KV Cache & Context Window:** Limit unnecessary context bloating, use flash-attention (SDPA in PyTorch), and enable prompt caching.
- **Batching & Worker Queues:** Group concurrent embedding or inference calls into vectorized batches instead of processing one-by-one.

#### B. Python Backend & API Optimization (FastAPI, Flask, AsyncIO)
- **Non-blocking I/O:** Convert blocking database/file/network calls to `asyncio` (`aiohttp`, `httpx`, `asyncpg`, `motor`).
- **Multiprocessing vs Multi-threading:** Use `ProcessPoolExecutor` for CPU-heavy AI preprocessing and `ThreadPoolExecutor` for I/O tasks (bypassing GIL where needed).
- **Intelligent Caching:** Implement layered caching:
  ```python
  from functools import lru_cache
  import diskcache
  # Fast in-memory or persistent disk cache for expensive compute/embeddings
  ```
- **Vectorization:** Replace nested Python loops with NumPy / Polars / PyTorch tensor vector operations.
- **Zero-Copy Streaming:** Use `StreamingResponse` for large AI outputs and file transfers.

#### C. Web Frontend & UI Performance (React, Vue, Web AI)
- **Bundle & Asset Splitting:** Dynamic imports (`React.lazy()`, code splitting), tree-shaking, and WebP/AVIF asset compression.
- **Render Optimization:** Debounce user input, memoize expensive computations (`useMemo`, `useCallback`), virtualize large lists (e.g. chat transcripts).
- **Web Workers:** Offload local browser AI processing (Transformers.js, WebLLM, regex parsing) to background Web Workers to prevent main thread freezing.
- **Core Web Vitals:** Minimize Largest Contentful Paint (LCP), Cumulative Layout Shift (CLS), and Interaction to Next Paint (INP).

#### D. Database & Vector Store Optimization (SQL, ChromaDB, FAISS)
- **Vector Index Tuning:** Configure HNSW parameters (`M`, `efConstruction`, `efSearch`) to balance search recall vs. query latency.
- **SQL & ORM Hardening:** Add proper composite indexes, avoid `SELECT *`, eliminate N+1 queries using `select_related`/`joinedload`, and use connection pools.
- **Batch Upserts:** Always batch vector embeddings and database writes.

---

## 3. Post-Optimization Benchmark & Validation

After applying changes, summarize results clearly:
- **Baseline vs Optimized Metrics:** (e.g., Latency: `450ms -> 65ms (-85%)`, VRAM: `8.2GB -> 2.4GB (-70%)`, Throughput: `12 tps -> 55 tps (+358%)`).
- **Regression Check:** Verify that accuracy, functionality, and data integrity remain 100% intact.

---

## 4. Immediate Confirmation on Activation

When this skill is first read/activated, output this confirmation line:
`⚡ [SpeedOptimizer Active] Hybrid performance planning, deep profiling & multi-stack speed engine enabled for this session. (Type 'stop optimize' to disable)`
