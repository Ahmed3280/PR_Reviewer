import json
import os
import sys

# Make the project root importable so "from agents.X import ..." works
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.security import run_security_review
from agents.style import run_style_review
from agents.tests import run_test_review
from evals.dataset import DATASET
from evals.scorer import score

AGENT_FN = {
    "security": run_security_review,
    "style": run_style_review,
    "tests": run_test_review,
}

RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results.json")


def _f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "N/A"
    return f"{100 * numerator / denominator:.1f}%"


def _print_agent_block(agent: str, agent_results: list[dict]) -> None:
    bugs = [r for r in agent_results if r["should_find"]]
    cleans = [r for r in agent_results if not r["should_find"]]

    tp = sum(1 for r in bugs if r["caught"])
    fn = len(bugs) - tp
    fp = sum(1 for r in cleans if r["false_positive"])

    n_bugs = len(bugs)
    n_cleans = len(cleans)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / n_bugs if n_bugs > 0 else 0.0
    f1 = _f1(precision, recall)

    label = agent.capitalize() if agent != "tests" else "Test"
    print(f"\n{label} Agent ({len(agent_results)} cases: {n_bugs} bugs + {n_cleans} clean)")
    print(f"  True Positives:   {tp} / {n_bugs}   (caught bugs)")
    print(f"  False Negatives:  {fn} / {n_bugs}   (missed bugs)")
    print(f"  False Positives:  {fp} / {n_cleans}   (flagged clean code)")
    print(f"  Precision:        {_pct(tp, tp + fp)}")
    print(f"  Recall:           {_pct(tp, n_bugs)}")
    print(f"  F1 Score:         {f1 * 100:.1f}%")


def run_evals() -> list[dict]:
    total = len(DATASET)
    results = []

    for i, case in enumerate(DATASET):
        agent = case["expected_agent"]
        bug_type = case["bug_type"]
        print(f"Running case {i + 1}/{total} — {agent} — {bug_type}...")

        agent_fn = AGENT_FN[agent]
        response = agent_fn(case["diff"])

        result = score(response, case)
        result.update(
            {
                "case_id": i + 1,
                "expected_agent": agent,
                "bug_type": bug_type,
                "should_find": case["should_find"],
                "description": case["description"],
            }
        )
        results.append(result)

    return results


def print_summary(results: list[dict]) -> None:
    print("\n" + "=" * 30)
    print("EVALUATION RESULTS")
    print("=" * 30)

    for agent in ("security", "style", "tests"):
        agent_results = [r for r in results if r["expected_agent"] == agent]
        _print_agent_block(agent, agent_results)

    print("\n" + "-" * 30)
    print("OVERALL")

    all_bugs = [r for r in results if r["should_find"]]
    all_cleans = [r for r in results if not r["should_find"]]
    total_caught = sum(1 for r in all_bugs if r["caught"])
    total_fp = sum(1 for r in all_cleans if r["false_positive"])

    print(f"  Total bugs planted:  {len(all_bugs)}")
    print(f"  Total caught:        {total_caught}")
    print(f"  Overall recall:      {_pct(total_caught, len(all_bugs))}")
    print(
        f"  Overall FP rate:     {_pct(total_fp, len(all_cleans))}"
        f" ({total_fp}/{len(all_cleans)} clean diffs flagged)"
    )
    print("-" * 30)


def save_results(results: list[dict]) -> None:
    with open(RESULTS_PATH, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    print(f"\nFull results saved to {RESULTS_PATH}")


if __name__ == "__main__":
    results = run_evals()
    print_summary(results)
    save_results(results)
