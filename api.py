from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio

from agents.manager import build_graph
from tools.github import fetch_pr_diff

load_dotenv()

app = FastAPI(title="PR Reviewer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReviewRequest(BaseModel):
    repo: str
    pr_number: int


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/review")
async def review(request: ReviewRequest):
    try:
        diff = await asyncio.to_thread(fetch_pr_diff, request.repo, request.pr_number)
    except Exception as e:
        msg = str(e)
        if "404" in msg:
            raise HTTPException(status_code=404, detail="PR not found — check the repo and PR number.")
        elif "429" in msg:
            raise HTTPException(status_code=429, detail="GitHub rate limit exceeded. Try again in a minute.")
        else:
            raise HTTPException(status_code=502, detail=f"GitHub API error: {msg}")

    graph = build_graph()

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(graph.invoke, {"diff": diff}),
            timeout=90
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Review timed out. This PR is too large. Try a smaller PR with fewer files changed."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review pipeline failed: {str(e)}")

    return {
        "repo": request.repo,
        "pr_number": request.pr_number,
        "security_findings": result["security_findings"],
        "style_findings": result["style_findings"],
        "test_findings": result["test_findings"],
        "final_verdict": result["final_verdict"],
    }