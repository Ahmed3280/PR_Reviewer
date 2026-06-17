import sys
from agents.manager import build_graph
from tools.github import fetch_pr_diff

def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <repo> <pr_number>")
        print("Example: python main.py psf/requests 7471")
        sys.exit(1)

    repo = sys.argv[1]
    pr_number = int(sys.argv[2])

    print(f"\n{'='*50}")
    print(f"  PR Reviewer — {repo} #{pr_number}")
    print(f"{'='*50}\n")

    print("Fetching diff from GitHub...")
    diff = fetch_pr_diff(repo, pr_number)
    print(f"Got diff ({len(diff)} characters)\n")

    graph = build_graph()
    result = graph.invoke({"diff": diff})

    print(f"\n{'='*50}")
    print("  SECURITY FINDINGS")
    print(f"{'='*50}")
    print(result["security_findings"])

    print(f"\n{'='*50}")
    print("  STYLE FINDINGS")
    print(f"{'='*50}")
    print(result["style_findings"])

    print(f"\n{'='*50}")
    print("  TEST FINDINGS")
    print(f"{'='*50}")
    print(result["test_findings"])

    print(f"\n{'='*50}")
    print("  FINAL VERDICT")
    print(f"{'='*50}")
    print(result["final_verdict"])
    print()

if __name__ == "__main__":
    main()