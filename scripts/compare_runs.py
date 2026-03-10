"""
Compare evaluation results across multiple models/runs.

Usage:
  python scripts/compare_runs.py results/eval_*.json
"""

import argparse
import json
import sys
from pathlib import Path


def load_eval(filepath: str) -> dict:
    with open(filepath) as f:
        return json.load(f)


def print_comparison(evals: list[dict]):
    """Print a side-by-side comparison of multiple evaluation runs."""

    print(f"\n{'='*90}")
    print("CROSS-RUN COMPARISON")
    print(f"{'='*90}")

    # Header
    print(f"\n{'Model':<30s} {'Condition':<18s} {'Composite':>10s} {'USWDS':>10s} {'Structure':>10s} {'A11y':>10s}")
    print("─" * 90)

    for ev in evals:
        model = ev.get("model", "unknown")
        for condition in ["without_skills", "with_skills"]:
            if condition not in ev:
                continue
            data = ev[condition]
            label = "without skills" if condition == "without_skills" else "WITH SKILLS"
            print(
                f"{model:<30s} {label:<18s} "
                f"{data['avg_composite']:>10.3f} "
                f"{data['avg_uswds_classes']:>10.3f} "
                f"{data['avg_html_structure']:>10.3f} "
                f"{data['avg_accessibility']:>10.3f}"
            )

        if "deltas" in ev:
            d = ev["deltas"]
            print(
                f"{'':.<30s} {'DELTA':.<18s} "
                f"{d['composite']:>+10.3f} "
                f"{d['uswds_classes']:>+10.3f} "
                f"{d['html_structure']:>+10.3f} "
                f"{d['accessibility']:>+10.3f}"
            )
        print()

    # Per-difficulty breakdown
    print(f"\n{'='*90}")
    print("BY DIFFICULTY")
    print(f"{'='*90}")

    for ev in evals:
        model = ev.get("model", "unknown")
        print(f"\n  {model}")
        for condition in ["without_skills", "with_skills"]:
            if condition not in ev:
                continue
            label = "without" if condition == "without_skills" else "WITH"
            tasks = ev[condition].get("per_task", [])

            by_difficulty = {}
            for t in tasks:
                diff = t.get("difficulty", "unknown")
                by_difficulty.setdefault(diff, []).append(t["composite_score"])

            for diff in ["easy", "medium", "hard"]:
                scores = by_difficulty.get(diff, [])
                if scores:
                    avg = sum(scores) / len(scores)
                    print(f"    {label:>7s} | {diff:<8s}: {avg:.3f}  (n={len(scores)})")

    print(f"\n{'='*90}")


def main():
    parser = argparse.ArgumentParser(description="Compare evaluation runs")
    parser.add_argument("eval_files", nargs="+", help="Evaluation JSON files to compare")
    args = parser.parse_args()

    evals = []
    for f in args.eval_files:
        if not Path(f).exists():
            print(f"Warning: {f} not found, skipping")
            continue
        evals.append(load_eval(f))

    if not evals:
        print("No valid evaluation files found.")
        sys.exit(1)

    print_comparison(evals)


if __name__ == "__main__":
    main()
