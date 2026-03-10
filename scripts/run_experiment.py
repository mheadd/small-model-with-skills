"""
Run the USWDS HTML generation experiment.

This script runs a set of USWDS HTML generation tasks against a smaller LLM,
both with and without the USWDS skills context, and saves the outputs for
evaluation.

Requires: Ollama running locally with the target model pulled.
Usage:  python scripts/run_experiment.py --model qwen2.5-coder:7b
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from skills_context import build_skills_context, build_condensed_context, build_custom_context


PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_FILE = PROJECT_ROOT / "prompts" / "tasks.json"
RESULTS_DIR = PROJECT_ROOT / "results"

OLLAMA_API = os.environ.get("OLLAMA_API_URL", "http://localhost:11434")

SYSTEM_PROMPT_BASE = """You are an expert frontend developer specializing in U.S. government websites.
When asked to generate HTML, produce complete, valid HTML code using the
U.S. Web Design System (USWDS) v3. Output ONLY the HTML code wrapped in
a single code block. Do not include explanations outside the code block."""

SYSTEM_PROMPT_WITH_SKILLS = """You are an expert frontend developer specializing in U.S. government websites.
When asked to generate HTML, produce complete, valid HTML code using the
U.S. Web Design System (USWDS) v3. Output ONLY the HTML code wrapped in
a single code block. Do not include explanations outside the code block.

You have access to the following USWDS reference documentation. Use it to
ensure your HTML uses the correct CSS classes, component structures, design
tokens, and accessibility patterns:

{skills_context}"""


def check_ollama(model: str) -> bool:
    """Verify Ollama is running and the model is available."""
    try:
        resp = requests.get(f"{OLLAMA_API}/api/tags", timeout=5)
        resp.raise_for_status()
        available = [m["name"] for m in resp.json().get("models", [])]
        # Check for exact match or partial match (model name without tag)
        for name in available:
            if model in name or name.startswith(model):
                return True
        print(f"Model '{model}' not found. Available models: {available}")
        return False
    except requests.ConnectionError:
        print(f"Cannot connect to Ollama at {OLLAMA_API}. Is it running?")
        return False


def generate(model: str, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> dict:
    """Call the Ollama API to generate a response."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 4096,
        },
    }

    start = time.time()
    resp = requests.post(f"{OLLAMA_API}/api/chat", json=payload, timeout=600)
    resp.raise_for_status()
    elapsed = time.time() - start

    data = resp.json()
    return {
        "content": data["message"]["content"],
        "model": data.get("model", model),
        "total_duration_ns": data.get("total_duration", 0),
        "eval_count": data.get("eval_count", 0),
        "elapsed_seconds": round(elapsed, 2),
    }


def extract_html(text: str) -> str:
    """Extract HTML content from a response that may contain code fences."""
    # Try to extract from ```html ... ``` blocks
    if "```html" in text:
        parts = text.split("```html")
        if len(parts) > 1:
            code = parts[1].split("```")[0]
            return code.strip()
    # Try generic ``` blocks
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 3:
            return parts[1].strip()
    # Return as-is if no code fences
    return text.strip()


def load_tasks() -> list[dict]:
    """Load the task prompts from the JSON file."""
    with open(PROMPTS_FILE, "r") as f:
        return json.load(f)


def run_single_task(
    model: str,
    task: dict,
    condition: str,
    system_prompt: str,
    results_subdir: Path,
) -> dict:
    """Run a single task and save results."""
    task_id = task["id"]
    print(f"  [{condition}] Running task: {task_id} - {task['name']}...", end=" ", flush=True)

    result = generate(model, system_prompt, task["prompt"])
    html_content = extract_html(result["content"])

    # Save the raw response
    raw_file = results_subdir / f"{task_id}_raw.md"
    with open(raw_file, "w") as f:
        f.write(result["content"])

    # Save extracted HTML
    html_file = results_subdir / f"{task_id}.html"
    with open(html_file, "w") as f:
        f.write(html_content)

    print(f"done ({result['elapsed_seconds']}s)")

    return {
        "task_id": task_id,
        "task_name": task["name"],
        "condition": condition,
        "model": result["model"],
        "elapsed_seconds": result["elapsed_seconds"],
        "eval_count": result["eval_count"],
        "html_length": len(html_content),
        "raw_file": str(raw_file.relative_to(PROJECT_ROOT)),
        "html_file": str(html_file.relative_to(PROJECT_ROOT)),
    }


def run_experiment(model: str, tasks: list[dict], use_condensed: bool = False,
                   include_custom: bool = False) -> dict:
    """Run the full experiment: all tasks with and without skills context."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_id = f"{model.replace(':', '_').replace('/', '_')}_{timestamp}"

    # Prepare results directories
    without_dir = RESULTS_DIR / "without_skills" / run_id
    with_dir = RESULTS_DIR / "with_skills" / run_id
    without_dir.mkdir(parents=True, exist_ok=True)
    with_dir.mkdir(parents=True, exist_ok=True)

    if include_custom:
        custom_dir = RESULTS_DIR / "with_custom_skill" / run_id
        custom_dir.mkdir(parents=True, exist_ok=True)

    # Build skills context
    if use_condensed:
        skills_ctx = build_condensed_context()
        print(f"Using condensed skills context ({len(skills_ctx):,} chars)")
    else:
        skills_ctx = build_skills_context()
        print(f"Using full skills context ({len(skills_ctx):,} chars)")

    system_with_skills = SYSTEM_PROMPT_WITH_SKILLS.format(skills_context=skills_ctx)

    custom_ctx = None
    system_with_custom = None
    if include_custom:
        custom_ctx = build_custom_context()
        system_with_custom = SYSTEM_PROMPT_WITH_SKILLS.format(skills_context=custom_ctx)
        print(f"Using custom skill context ({len(custom_ctx):,} chars)")

    all_results = []

    # Run WITHOUT skills
    print(f"\n{'='*60}")
    print(f"CONDITION: WITHOUT SKILLS")
    print(f"{'='*60}")
    for task in tasks:
        result = run_single_task(model, task, "without_skills", SYSTEM_PROMPT_BASE, without_dir)
        all_results.append(result)

    # Run WITH skills
    print(f"\n{'='*60}")
    print(f"CONDITION: WITH SKILLS")
    print(f"{'='*60}")
    for task in tasks:
        result = run_single_task(model, task, "with_skills", system_with_skills, with_dir)
        all_results.append(result)

    # Run WITH CUSTOM SKILL (if enabled)
    if include_custom:
        print(f"\n{'='*60}")
        print(f"CONDITION: WITH CUSTOM SKILL")
        print(f"{'='*60}")
        for task in tasks:
            result = run_single_task(model, task, "with_custom_skill", system_with_custom, custom_dir)
            all_results.append(result)

    # Save run metadata
    run_meta = {
        "run_id": run_id,
        "model": model,
        "timestamp": timestamp,
        "num_tasks": len(tasks),
        "skills_context_mode": "condensed" if use_condensed else "full",
        "skills_context_chars": len(skills_ctx),
        "custom_skill_chars": len(custom_ctx) if custom_ctx else 0,
        "include_custom": include_custom,
        "results": all_results,
    }

    meta_file = RESULTS_DIR / f"run_{run_id}.json"
    with open(meta_file, "w") as f:
        json.dump(run_meta, f, indent=2)

    print(f"\nResults saved to: {meta_file}")
    return run_meta


def main():
    parser = argparse.ArgumentParser(description="Run USWDS HTML generation experiment")
    parser.add_argument(
        "--model",
        default="qwen2.5-coder:7b",
        help="Ollama model name (default: qwen2.5-coder:7b)",
    )
    parser.add_argument(
        "--tasks",
        nargs="*",
        help="Specific task IDs to run (default: all)",
    )
    parser.add_argument(
        "--condensed",
        action="store_true",
        help="Use condensed skills context (SKILL.md + components only)",
    )
    parser.add_argument(
        "--condition",
        choices=["both", "with", "without"],
        default="both",
        help="Which condition(s) to run (default: both)",
    )
    parser.add_argument(
        "--custom-skill",
        action="store_true",
        help="Include a third condition using the custom targeted skill file",
    )
    args = parser.parse_args()

    print(f"USWDS Skills Experiment")
    print(f"Model: {args.model}")
    print(f"Ollama API: {OLLAMA_API}")
    if args.custom_skill:
        print(f"Custom skill: ENABLED")
    print()

    # Check Ollama connectivity
    if not check_ollama(args.model):
        print(f"\nTo get started, install Ollama and pull the model:")
        print(f"  brew install ollama")
        print(f"  ollama pull {args.model}")
        sys.exit(1)

    # Load tasks
    tasks = load_tasks()
    if args.tasks:
        tasks = [t for t in tasks if t["id"] in args.tasks]
    print(f"Tasks to run: {len(tasks)}")

    # Run experiment
    run_meta = run_experiment(args.model, tasks, use_condensed=args.condensed,
                              include_custom=args.custom_skill)

    # Print summary
    print(f"\n{'='*60}")
    print("EXPERIMENT COMPLETE")
    print(f"{'='*60}")
    print(f"Run ID: {run_meta['run_id']}")
    print(f"Total results: {len(run_meta['results'])}")
    print(f"\nNext step: Run evaluation")
    print(f"  python scripts/evaluate.py results/run_{run_meta['run_id']}.json")


if __name__ == "__main__":
    main()
