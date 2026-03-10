"""
Evaluate USWDS compliance of generated HTML outputs.

Scoring dimensions:
  1. USWDS Class Usage   - Are the correct usa-* and grid-* classes present?
  2. HTML Structure       - Are semantic HTML elements used correctly?
  3. Accessibility        - Are ARIA attributes and a11y patterns present?
  4. Completeness         - Does the output address all parts of the prompt?
  5. Valid HTML           - Is the output parseable, well-formed HTML?

Usage:
  python scripts/evaluate.py results/run_<id>.json
  python scripts/evaluate.py --html results/with_skills/run_id/01_gov_banner.html --task 01_gov_banner
"""

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_FILE = PROJECT_ROOT / "prompts" / "tasks.json"


class HTMLStructureParser(HTMLParser):
    """Parse HTML to extract structural information for evaluation."""

    def __init__(self):
        super().__init__()
        self.elements = []
        self.classes = []
        self.aria_attrs = []
        self.scope_attrs = []
        self.all_attrs = {}
        self.errors = []
        self.open_tags = []
        self.has_doctype = False

    def handle_decl(self, decl):
        if decl.lower().startswith("doctype"):
            self.has_doctype = True

    def handle_starttag(self, tag, attrs):
        self.elements.append(tag)
        self.open_tags.append(tag)
        attr_dict = dict(attrs)
        for key, value in attrs:
            if key == "class" and value:
                self.classes.extend(value.split())
            if key.startswith("aria-"):
                self.aria_attrs.append(key)
            if key == "scope":
                self.scope_attrs.append(value)
            if key == "role":
                self.aria_attrs.append("role")

    def handle_endtag(self, tag):
        if self.open_tags and self.open_tags[-1] == tag:
            self.open_tags.pop()

    def handle_data(self, data):
        pass

    def error(self, message):
        self.errors.append(message)


def parse_html(html_content: str) -> HTMLStructureParser:
    """Parse HTML and return structural data."""
    parser = HTMLStructureParser()
    try:
        parser.feed(html_content)
    except Exception as e:
        parser.errors.append(str(e))
    return parser


def score_uswds_classes(parser: HTMLStructureParser, expected_classes: list[str]) -> dict:
    """Score how many expected USWDS classes are present in the output."""
    found_classes = set(parser.classes)
    expected = set(expected_classes)

    if not expected:
        return {"score": 1.0, "found": [], "missing": [], "detail": "No classes expected"}

    found = expected & found_classes
    missing = expected - found_classes

    # Also check for partial matches (e.g., grid-col-* matches grid-col)
    for exp_cls in list(missing):
        for actual_cls in found_classes:
            if actual_cls.startswith(exp_cls) or exp_cls.startswith(actual_cls.split("-")[0]):
                if "grid-col" in exp_cls and "grid-col" in actual_cls:
                    found.add(exp_cls)
                    missing.discard(exp_cls)
                    break

    score = len(found) / len(expected) if expected else 1.0

    return {
        "score": round(score, 3),
        "found": sorted(found),
        "missing": sorted(missing),
        "extra_uswds_classes": sorted(
            c for c in found_classes if c.startswith("usa-") or c.startswith("grid-")
        ),
    }


def score_html_structure(parser: HTMLStructureParser, expected_elements: list[str]) -> dict:
    """Score whether expected semantic HTML elements are present."""
    found_elements = set(parser.elements)
    expected = set(expected_elements)

    if not expected:
        return {"score": 1.0, "found": [], "missing": [], "detail": "No elements expected"}

    found = expected & found_elements
    missing = expected - found_elements
    score = len(found) / len(expected) if expected else 1.0

    # Bonus checks for semantic HTML
    semantic_elements = {"header", "nav", "main", "section", "article", "aside", "footer"}
    semantic_used = semantic_elements & found_elements

    return {
        "score": round(score, 3),
        "found": sorted(found),
        "missing": sorted(missing),
        "semantic_html_used": sorted(semantic_used),
    }


def score_accessibility(parser: HTMLStructureParser, expected_aria: list[str]) -> dict:
    """Score accessibility attributes and patterns."""
    found_aria = set(parser.aria_attrs)
    expected = set(expected_aria)

    # Base score from expected ARIA attributes
    if expected:
        found = expected & found_aria
        missing = expected - found_aria
        aria_score = len(found) / len(expected)
    else:
        found = set()
        missing = set()
        aria_score = 1.0

    # Bonus points for additional a11y patterns
    bonus = 0.0
    bonus_details = []

    # Check for scope attributes on th elements
    if "scope" in parser.scope_attrs or parser.scope_attrs:
        bonus += 0.1
        bonus_details.append("table scope attributes")

    # Check for semantic HTML elements
    semantic = {"header", "nav", "main", "footer", "section"}
    if semantic & set(parser.elements):
        bonus += 0.1
        bonus_details.append("semantic HTML elements")

    # Check for any ARIA attributes beyond expected
    extra_aria = found_aria - expected
    if extra_aria:
        bonus += 0.05 * min(len(extra_aria), 4)
        bonus_details.append(f"additional ARIA: {sorted(extra_aria)}")

    final_score = min(1.0, aria_score + bonus)

    return {
        "score": round(final_score, 3),
        "found_expected": sorted(found),
        "missing_expected": sorted(missing),
        "all_aria_attrs": sorted(found_aria),
        "bonus_details": bonus_details,
    }


def score_completeness(html_content: str, task: dict) -> dict:
    """Score how complete the output is relative to the task requirements."""
    checks = []

    # Check minimum length (very short outputs are likely incomplete)
    if len(html_content) < 50:
        checks.append(("minimum_length", False, "Output too short (<50 chars)"))
    else:
        checks.append(("minimum_length", True, ""))

    # Check for HTML structure
    has_tags = bool(re.search(r"<[a-z]+[\s>]", html_content, re.IGNORECASE))
    checks.append(("has_html_tags", has_tags, "" if has_tags else "No HTML tags found"))

    # Check for closing tags (well-formed HTML)
    has_closing = bool(re.search(r"</[a-z]+>", html_content, re.IGNORECASE))
    checks.append(("has_closing_tags", has_closing, "" if has_closing else "No closing tags"))

    # Check for USWDS class usage
    has_uswds = bool(re.search(r'class="[^"]*usa-', html_content))
    checks.append(("uses_uswds_classes", has_uswds, "" if has_uswds else "No usa-* classes found"))

    passed = sum(1 for _, ok, _ in checks if ok)
    score = passed / len(checks) if checks else 0.0

    return {
        "score": round(score, 3),
        "checks": [{"check": name, "passed": ok, "note": note} for name, ok, note in checks],
    }


def score_html_validity(html_content: str, parser: HTMLStructureParser) -> dict:
    """Score basic HTML validity."""
    issues = list(parser.errors)

    # Check for unclosed tags (simplified check)
    void_elements = {"area", "base", "br", "col", "embed", "hr", "img", "input",
                     "link", "meta", "source", "track", "wbr"}
    unclosed = [t for t in parser.open_tags if t not in void_elements]
    if unclosed:
        issues.append(f"Potentially unclosed tags: {unclosed}")

    # Check for DOCTYPE
    has_doctype = parser.has_doctype or "<!doctype" in html_content.lower()[:100]

    score = 1.0
    if issues:
        score -= 0.1 * min(len(issues), 5)
    score = max(0.0, score)

    return {
        "score": round(score, 3),
        "has_doctype": has_doctype,
        "issues": issues,
    }


def evaluate_single(html_content: str, task: dict) -> dict:
    """Evaluate a single HTML output against its task requirements."""
    parser = parse_html(html_content)

    uswds_score = score_uswds_classes(parser, task.get("expected_classes", []))
    structure_score = score_html_structure(parser, task.get("expected_elements", []))
    a11y_score = score_accessibility(parser, task.get("expected_aria", []))
    completeness_score = score_completeness(html_content, task)
    validity_score = score_html_validity(html_content, parser)

    # Weighted composite score
    weights = {
        "uswds_classes": 0.30,
        "html_structure": 0.20,
        "accessibility": 0.20,
        "completeness": 0.15,
        "html_validity": 0.15,
    }

    composite = (
        uswds_score["score"] * weights["uswds_classes"]
        + structure_score["score"] * weights["html_structure"]
        + a11y_score["score"] * weights["accessibility"]
        + completeness_score["score"] * weights["completeness"]
        + validity_score["score"] * weights["html_validity"]
    )

    return {
        "task_id": task["id"],
        "task_name": task["name"],
        "difficulty": task.get("difficulty", "unknown"),
        "composite_score": round(composite, 3),
        "scores": {
            "uswds_classes": uswds_score,
            "html_structure": structure_score,
            "accessibility": a11y_score,
            "completeness": completeness_score,
            "html_validity": validity_score,
        },
        "weights": weights,
    }


def load_tasks() -> dict:
    """Load tasks indexed by ID."""
    with open(PROMPTS_FILE) as f:
        tasks = json.load(f)
    return {t["id"]: t for t in tasks}


def evaluate_run(run_file: Path) -> dict:
    """Evaluate all outputs from an experiment run."""
    with open(run_file) as f:
        run_meta = json.load(f)

    tasks = load_tasks()
    evaluations = {"with_skills": [], "without_skills": [], "with_custom_skill": []}

    for result in run_meta["results"]:
        task_id = result["task_id"]
        condition = result["condition"]
        html_file = PROJECT_ROOT / result["html_file"]

        if condition not in evaluations:
            evaluations[condition] = []

        if not html_file.exists():
            print(f"  WARNING: {html_file} not found, skipping")
            continue

        with open(html_file) as f:
            html_content = f.read()

        task = tasks.get(task_id)
        if not task:
            print(f"  WARNING: Task {task_id} not found, skipping")
            continue

        evaluation = evaluate_single(html_content, task)
        evaluation["html_file"] = str(html_file.relative_to(PROJECT_ROOT))
        evaluations[condition].append(evaluation)

    return compute_summary(evaluations, run_meta)


def compute_summary(evaluations: dict, run_meta: dict) -> dict:
    """Compute summary statistics comparing conditions."""

    def avg(scores):
        return round(sum(scores) / len(scores), 3) if scores else 0

    summary = {"run_id": run_meta["run_id"], "model": run_meta["model"]}

    for condition in ["without_skills", "with_skills", "with_custom_skill"]:
        evals = evaluations.get(condition, [])
        if not evals:
            continue

        composites = [e["composite_score"] for e in evals]
        uswds_scores = [e["scores"]["uswds_classes"]["score"] for e in evals]
        structure_scores = [e["scores"]["html_structure"]["score"] for e in evals]
        a11y_scores = [e["scores"]["accessibility"]["score"] for e in evals]

        summary[condition] = {
            "num_tasks": len(evals),
            "avg_composite": avg(composites),
            "avg_uswds_classes": avg(uswds_scores),
            "avg_html_structure": avg(structure_scores),
            "avg_accessibility": avg(a11y_scores),
            "per_task": evals,
        }

    # Compute deltas
    if "with_skills" in summary and "without_skills" in summary:
        ws = summary["with_skills"]
        ns = summary["without_skills"]
        summary["deltas"] = {
            "composite": round(ws["avg_composite"] - ns["avg_composite"], 3),
            "uswds_classes": round(ws["avg_uswds_classes"] - ns["avg_uswds_classes"], 3),
            "html_structure": round(ws["avg_html_structure"] - ns["avg_html_structure"], 3),
            "accessibility": round(ws["avg_accessibility"] - ns["avg_accessibility"], 3),
        }

    if "with_custom_skill" in summary and "without_skills" in summary:
        cs = summary["with_custom_skill"]
        ns = summary["without_skills"]
        summary["deltas_custom"] = {
            "composite": round(cs["avg_composite"] - ns["avg_composite"], 3),
            "uswds_classes": round(cs["avg_uswds_classes"] - ns["avg_uswds_classes"], 3),
            "html_structure": round(cs["avg_html_structure"] - ns["avg_html_structure"], 3),
            "accessibility": round(cs["avg_accessibility"] - ns["avg_accessibility"], 3),
        }

    summary["evaluations"] = evaluations
    return summary


def print_report(summary: dict):
    """Print a human-readable evaluation report."""
    print(f"\n{'='*70}")
    print(f"EVALUATION REPORT")
    print(f"{'='*70}")
    print(f"Run ID: {summary['run_id']}")
    print(f"Model:  {summary['model']}")

    for condition in ["without_skills", "with_skills", "with_custom_skill"]:
        if condition not in summary:
            continue
        data = summary[condition]
        labels = {
            "without_skills": "WITHOUT Skills",
            "with_skills": "WITH Skills (full)",
            "with_custom_skill": "WITH CUSTOM Skill (targeted)",
        }
        label = labels.get(condition, condition)
        print(f"\n{'─'*70}")
        print(f"  {label}")
        print(f"{'─'*70}")
        print(f"  Avg Composite Score:    {data['avg_composite']:.3f}")
        print(f"  Avg USWDS Classes:      {data['avg_uswds_classes']:.3f}")
        print(f"  Avg HTML Structure:     {data['avg_html_structure']:.3f}")
        print(f"  Avg Accessibility:      {data['avg_accessibility']:.3f}")
        print()

        for task_eval in data["per_task"]:
            difficulty = task_eval["difficulty"]
            print(f"    {task_eval['task_id']} ({difficulty:6s}) {task_eval['task_name']:.<40s} {task_eval['composite_score']:.3f}")

    if "deltas" in summary:
        print(f"\n{'─'*70}")
        print(f"  IMPROVEMENT: full skills vs no skills")
        print(f"{'─'*70}")
        for metric, delta in summary["deltas"].items():
            direction = "↑" if delta > 0 else "↓" if delta < 0 else "─"
            print(f"  {direction} {metric:.<40s} {delta:+.3f}")

    if "deltas_custom" in summary:
        print(f"\n{'─'*70}")
        print(f"  IMPROVEMENT: custom skill vs no skills")
        print(f"{'─'*70}")
        for metric, delta in summary["deltas_custom"].items():
            direction = "↑" if delta > 0 else "↓" if delta < 0 else "─"
            print(f"  {direction} {metric:.<40s} {delta:+.3f}")

    print(f"\n{'='*70}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate USWDS HTML generation outputs")
    parser.add_argument(
        "run_file",
        nargs="?",
        help="Path to run JSON file (e.g., results/run_<id>.json)",
    )
    parser.add_argument(
        "--html",
        help="Evaluate a single HTML file",
    )
    parser.add_argument(
        "--task",
        help="Task ID for single file evaluation",
    )
    parser.add_argument(
        "--output",
        help="Save evaluation results to JSON file",
    )
    args = parser.parse_args()

    if args.html and args.task:
        # Single file evaluation
        tasks = load_tasks()
        task = tasks.get(args.task)
        if not task:
            print(f"Task '{args.task}' not found")
            sys.exit(1)

        with open(args.html) as f:
            html_content = f.read()

        result = evaluate_single(html_content, task)
        print(json.dumps(result, indent=2))
        return

    if not args.run_file:
        # Find the most recent run file
        run_files = sorted(RESULTS_DIR.glob("run_*.json"))
        if not run_files:
            print("No run files found. Run the experiment first:")
            print("  python scripts/run_experiment.py --model qwen2.5-coder:7b")
            sys.exit(1)
        args.run_file = str(run_files[-1])
        print(f"Using most recent run: {args.run_file}")

    run_path = Path(args.run_file)
    if not run_path.exists():
        print(f"File not found: {run_path}")
        sys.exit(1)

    summary = evaluate_run(run_path)
    print_report(summary)

    # Save full evaluation
    output_file = args.output or str(run_path).replace("run_", "eval_")
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nFull evaluation saved to: {output_file}")


if __name__ == "__main__":
    main()
