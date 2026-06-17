import httpx
import os
from dotenv import load_dotenv

load_dotenv()

SKIP_FILES = [
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "Pipfile.lock",
    ".min.js",
    ".min.css",
    ".map",
    "dist/",
    "build/",
    ".pb.go",
    ".generated.",
]

def filter_diff(diff: str) -> str:
    chunks = diff.split("diff --git")
    filtered = [c for c in chunks
                if not any(pattern in c for pattern in SKIP_FILES)]
    return "diff --git".join(filtered)

def fetch_pr_diff(repo: str, pr_number: int) -> str:
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "Authorization": f"Bearer {token}" if token else ""
    }
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

    response = httpx.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code}")

    return filter_diff(response.text)