---
name: LocalAISecurity
description: Strict Data Loss Prevention (DLP), air-gapped local isolation, secret sanitization, and secure AI/Python/Web development guardrails. Protects against secret leaks, unauthorized inbound/outbound data flow, unsafe model deserialization, prompt injection, and host exposure.
---

# LocalAISecurity: Air-Gap & Local AI Security Shield

When this skill is activated (e.g., user says *"enable it"*, *"เปิดโหมดความปลอดภัย"*, *"enable security"*, *"secure mode"*, or *"use LocalAISecurity"*), **you MUST strictly enforce all security protocols below on EVERY turn for the remainder of this session** until the user explicitly states to disable it.

---

## 1. Lifecycle & State Management

- **Status:** **ACTIVE** once invoked or enabled.
- **Duration:** Persists across all subsequent user requests and coding steps in the session.
- **Deactivation:** Only disable these constraints if the user explicitly says:
  `"disable security"`, `"ปิดโหมดความปลอดภัย"`, `"stop security"`, or `"disable LocalAISecurity"`.
- **Deactivation Output:** `[LocalAISecurity deactivated. Returned to standard development mode.]`

---

## 2. Pillar 1: Data Loss Prevention (DLP) & Secret Protection

1. **Zero Secret Exposure:**
   - **Never hardcode or output plain-text credentials**, API keys (OpenAI, Anthropic, HuggingFace, Google Gemini, AWS), access tokens, private keys, database connection strings, or `.env` content into code, chat responses, or commit files.
   - Automatically redact/mask any detected secrets in logs, terminal outputs, and artifacts (`[REDACTED_API_KEY]`, `[SECRET_HIDDEN]`).
   - Always load secrets via secure environment variables (`os.getenv()`, `python-dotenv`, `pydantic-settings`) and supply `.env.example` templates with empty placeholders only.

2. **Strict Repository Guardrails (`.gitignore` enforcement):**
   - Automatically ensure `.gitignore` contains critical exclusions before writing code:
     ```gitignore
     # Secrets & Configs
     .env
     .env.*
     *.pem
     *.key
     *.pfx
     
     # Proprietary Data & Models
     *.safetensors
     *.bin
     *.pt
     *.pth
     *.onnx
     *.csv
     *.parquet
     *.sqlite3
     *.db
     secrets/
     credentials/
     ```

3. **Proprietary Data & Context Shielding:**
   - Never leak local training datasets, proprietary system prompts, embeddings, or internal vector databases out of the local system.

---

## 3. Pillar 2: Air-Gap Boundaries & Network Isolation (No In/Out Leaks)

1. **Localhost Binding by Default:**
   - All local servers and web frameworks (FastAPI, Flask, Uvicorn, Gradio, Streamlit, Tornado) **MUST bind to `127.0.0.1` or `localhost`**.
   - **NEVER use `host="0.0.0.0"`** unless the user explicitly requests public exposure AND authentication/firewall rules are implemented.
   ```python
   # SECURE (Default):
   uvicorn.run("app:app", host="127.0.0.1", port=8000)
   
   # Gradio / Streamlit:
   demo.launch(server_name="127.0.0.1", share=False)
   ```

2. **Outbound Data Exfiltration Prevention:**
   - Disallow silent telemetry, analytics phone-home packages, and unverified third-party webhooks.
   - When calling local LLM runtimes (Ollama, LM Studio, vLLM, LocalAI), route requests strictly via `http://localhost:<port>` or `http://127.0.0.1:<port>`.
   - Never write code that sends prompts, completions, or local file payloads to unauthorized external URLs or unverified endpoints.

3. **Supply-Chain & Dependency Hardening:**
   - Guard against typo-squatting and unverified pip packages.
   - Enforce explicit, pinned versions in `requirements.txt` or `pyproject.toml`.
   - Never generate scripts with unsafe remote execution like `curl | bash` or unverified `Invoke-WebRequest | iex`.

---

## 4. Pillar 3: AI Model Safety & Secure Python Execution

1. **Safe Model Deserialization (Zero `pickle` Risk):**
   - **Never load untrusted `.pkl`, `.pt`, or `.pth` files with raw `pickle.load()`** (remote code execution vulnerability).
   - Use `safetensors` for neural network weights whenever possible:
     ```python
     from safetensors.torch import load_file
     weights = load_file("model.safetensors")
     ```
   - If `torch.load` is mandatory, enforce `weights_only=True`:
     ```python
     import torch
     weights = torch.load("model.pt", weights_only=True)
     ```

2. **Command & Shell Injection Prevention:**
   - Avoid `os.system()` and `eval()` / `exec()`.
   - When using `subprocess`, pass arguments as arrays/lists with `shell=False`:
     ```python
     # SECURE:
     subprocess.run(["ffmpeg", "-i", input_path, output_path], check=True, shell=False)
     ```

3. **Path Traversal & Local File Inclusion (LFI) Defense:**
   - Secure all file upload/download paths in web apps against `../` directory traversal:
     ```python
     from pathlib import Path
     base_dir = Path("./storage").resolve()
     target_path = (base_dir / filename).resolve()
     if not target_path.is_relative_to(base_dir):
         raise PermissionError("Access Denied: Path traversal detected.")
     ```

---

## 5. Pillar 4: Web AI Hardening & Prompt Defense

1. **Prompt Injection & Output Validation:**
   - Isolate untrusted user input from system instructions with structured delimiters (e.g., `<user_input>...</user_input>`).
   - Validate and sanitize model output before passing it to downstream tools, SQL queries, or bash executors.

2. **CORS & Web API Hardening:**
   - Never set `allow_origins=["*"]` on sensitive Web AI API endpoints. Restrict to specific local origin (e.g., `["http://localhost:3000"]`).
   - Enable security headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`).

---

## 6. Real-Time Code Review Checklist

Before finalizing any Python or Web AI code in this session, verify:
- [ ] No hardcoded tokens, passwords, or keys.
- [ ] Host is strictly `127.0.0.1` (no public `0.0.0.0` exposure).
- [ ] Safe deserialization used (`safetensors` or `weights_only=True`).
- [ ] No `shell=True` on dynamic input.
- [ ] Path traversal checks applied on file inputs.
- [ ] `.gitignore` protects secrets, keys, and model artifacts.

---

## 7. Immediate Confirmation on Activation

When this skill is first read/activated, output this confirmation line:
`🛡️ [LocalAISecurity Active] Air-gap isolation, DLP secret protection, and secure Local/Web AI guardrails enabled for this session. (Type 'disable security' to stop)`
