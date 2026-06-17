# PR Reviewer — Multi-Agent Code Review Tool

A multi-agent system built with LangGraph that automatically reviews
GitHub pull requests for security vulnerabilities, style issues,
and missing tests. Now includes a FastAPI backend and React frontend.

## Architecture

- **Security Agent** — finds vulnerabilities, injections, hardcoded secrets
- **Style Agent** — finds readability and maintainability issues
- **Test Agent** — finds missing or insufficient tests
- **Manager Graph** — orchestrates agents via LangGraph, synthesizes final verdict
- **FastAPI backend** (`api.py`) — exposes `POST /review` over HTTP
- **React frontend** (`frontend/`) — dark-themed UI for submitting PRs and reading results

## Setup

### 1. Clone and create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_google_api_key
GITHUB_TOKEN=your_github_token
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
```

---

## Running — CLI (original)

```bash
python main.py psf/requests 7471
```

## Running — Full Stack (API + UI)

Open **two terminals** from the project root:

```bash
# Terminal 1 — FastAPI backend (port 8000)
uvicorn api:app --reload --port 8000

# Terminal 2 — React frontend (port 5173)
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

Paste any GitHub PR URL, e.g.:

```
https://github.com/psf/requests/pull/7471
```

The review takes 30–60 seconds while three specialist agents run in sequence.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/health` | Returns `{"status": "ok"}` |
| `POST` | `/review` | Run agents on a PR |

**Request body:**
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
  "final_verdict": "..."
}
```
