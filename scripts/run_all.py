"""
Convenience script to run the full experiment pipeline:
  1. Run generation (with and without skills)
  2. Evaluate outputs
  3. Print comparison report

Usage:
  python scripts/run_all.py --model qwen2.5-coder:7b
  python scripts/run_all.py --model codellama:7b
  python scripts/run_all.py --model mistral:7b --condensed
"""

import argparse
import json
import sys
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

from run_experiment import run_experiment, load_tasks, check_ollama, OLLAMA_API
from evaluate import evaluate_run, print_report


PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def main():
    parser = argparse.ArgumentParser(description="Run full experiment pipeline")
    parser.add_argument(
        "--model",
        default="qwen2.5-coder:7b",
        help="Ollama model name (default: qwen2.5-coder:7b)",
    )
    parser.add_argument(
        "--condensed",
        action="store_true",
        help="Use condensed skills context",
    )
    parser.add_argument(
        "--tasks",
        nargs="*",
        help="Specific task IDs to run (default: all)",
    )
    args = parser.parse_args()

    print(f"Full Experiment Pipeline")
    print(f"Model: {args.model}")
    print(f"Ollama API: {OLLAMA_API}")
    print()

    # Check Ollama
    if not check_ollama(args.model):
        print(f"\nTo get started:")
        print(f"  1. Install Ollama: brew install ollama")
        print(f"  2. Start Ollama:   ollama serve")
        print(f"  3. Pull model:     ollama pull {args.model}")
        sys.exit(1)

    # Load and filter tasks
    tasks = load_tasks()
    if args.tasks:
        tasks = [t for t in tasks if t["id"] in args.tasks]

    # Step 1: Run experiment
    print(f"\n{'#'*60}")
    print(f"STEP 1: GENERATION")
    print(f"{'#'*60}")
    run_meta = run_experiment(args.model, tasks, use_condensed=args.condensed)

    # Step 2: Evaluate
    print(f"\n{'#'*60}")
    print(f"STEP 2: EVALUATION")
    print(f"{'#'*60}")
    run_file = RESULTS_DIR / f"run_{run_meta['run_id']}.json"
    summary = evaluate_run(run_file)
    print_report(summary)

    # Save evaluation
    eval_file = RESULTS_DIR / f"eval_{run_meta['run_id']}.json"
    with open(eval_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults: {run_file}")
    print(f"Evaluation: {eval_file}")


if __name__ == "__main__":
    main()
