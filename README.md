# Multi-Agent PR Code Reviewer

A multi-agent system that automatically reviews GitHub pull requests using three specialist LangGraph agents running in parallel. Each agent focuses on one dimension of code quality, and a manager graph synthesizes their findings into a final verdict. The FastAPI backend runs in Docker on AWS EC2 and the React frontend is hosted on AWS S3.

> 🎥 **Demo Video:** https://www.linkedin.com/posts/ahm-akram_langchain-langgraph-generativeai-ugcPost-7473336860979916801-pypx/?utm_source=share&utm_medium=member_desktop&rcm=ACoAAEPWV-gBgHDP4p_62oLfgS-vqdy4iKActkQ

---

## What It Does

Paste any GitHub PR URL, and the system fetches the diff, runs three agents in parallel, and returns a structured verdict.

```
APPROVE  /  REQUEST CHANGES  /  COMMENT
```

Each agent is a specialist:

| Agent | Looks For |
|---|---|
| **Security** | SQL injection, hardcoded secrets, unsafe inputs, exposed credentials |
| **Style** | Bad naming, missing docstrings, overly complex methods, readability issues |
| **Tests** | New functions with no corresponding tests, untested critical paths |

---

## Architecture

```
GitHub PR URL
      ↓
  fetch diff  (auto-filters lock files, generated code)
      ↓
  ┌──────────────────────────────┐
  │         LangGraph Graph      │
  │                              │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
  │  │ Security │  │  Style   │  │  Tests   │  │  ← run in parallel
  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
  │       └─────────────┼─────────────┘         │
  │                     ↓                        │
  │              Verdict node                    │
  │        (manager synthesizes)                 │
  └──────────────────────────────┘
      ↓
  Final verdict + findings
      ↓
  FastAPI → React frontend
```

**Stack:**
- **LangGraph** - agent orchestration (StateGraph, parallel fan-out)
- **LangChain** - LLM abstractions, message types
- **Gemini 2.5 Flash** 
- **FastAPI** - REST backend with 90-second timeout cap
- **React** - dark-theme frontend (Vite)
- **Docker** - containerized for deployment
- **AWS** - EC2 (backend) + S3 (frontend)

---

## Evaluation

Evaluated on **34 test cases**: 25 injected bugs + 9 adversarial clean diffs.

| Agent | Precision | Recall | F1 |
|---|---|---|---|
| Security | 100% | 100% | **100%** |
| Style | 100% | 100% | **100%** |
| Tests | 85.7% | 85.7% | **85.7%** |
| **Overall** | — | **96%** | — |

**False positive rate:** 11.1% (1/9 clean diffs flagged)

**Methodology:** synthetic bug injection + adversarial clean cases + deterministic keyword scoring. Initial 100% results led to hardening the dataset, which exposed real failure modes. Prompt engineering iteration improved test agent F1 from 71.4% to 85.7%.

Run the eval yourself:
```bash
python evals/run.py
```

See [`evals/README.md`](evals/README.md) for full methodology.

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- A [Gemini API key](https://aistudio.google.com) (free tier)
- A [GitHub token](https://github.com/settings/tokens) with `public_repo` scope (optional — needed for high volume)

### 1. Clone and create virtual environment

```bash
git clone https://github.com/Ahmed3280/PR_Reviewer.git
cd PR_Reviewer
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and add your keys
```

```
GOOGLE_API_KEY=your_gemini_key
GITHUB_TOKEN=your_github_token  # optional
```

---

## Running

### CLI

```bash
python main.py psf/requests 7471
```

### Full stack (API + UI)

```bash
# Terminal 1 — FastAPI backend
uvicorn api:app --reload --port 8000

# Terminal 2 — React frontend
cd frontend && npm run dev
```

Open `http://localhost:5173` → paste any GitHub PR URL → click Review.

**Example PRs to try:**
```
https://github.com/psf/requests/pull/7471       # clean → APPROVE
https://github.com/pallets/flask/pull/5544       # missing tests → REQUEST CHANGES
https://github.com/django/django/pull/21496      # complex feature → REQUEST CHANGES
```

---

## Docker

```bash
# Build
docker build -t pr-reviewer .

# Run
docker run -d -p 8000:8000 \
  -e GOOGLE_API_KEY="your_key" \
  --name pr-reviewer \
  pr-reviewer

# Or pull from Docker Hub
docker pull ahmedakram2/pr-reviewer:latest
```

---

## API

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/review` | Run agents on a PR |

**Request:**
```json
{ "repo": "psf/requests", "pr_number": 7471 }
```

**Response:**
```json
{
  "repo": "psf/requests",
  "pr_number": 7471,
  "security_findings": "...",
  "style_findings": "...",
  "test_findings": "...",
  "final_verdict": "APPROVE — All checks passed..."
}
```

---

## Project Structure

```
├── agents/
│   ├── manager.py       # LangGraph StateGraph, parallel fan-out
│   ├── security.py      # Security specialist
│   ├── style.py         # Style specialist
│   └── tests.py         # Test coverage specialist
├── tools/
│   └── github.py        # GitHub diff fetcher + lock file filter
├── evals/
│   ├── inject.py        # Synthetic bug injector (6 bug types)
│   ├── dataset.py       # 34 test cases
│   ├── scorer.py        # Deterministic keyword scoring
│   ├── run.py           # Eval runner
│   └── README.md        # Methodology + results
├── frontend/            # React dark-theme UI (Vite)
├── api.py               # FastAPI backend
├── main.py              # CLI entrypoint
└── Dockerfile
```
