"""Analyze weaknesses in qwen2.5-coder:7b without-skills results."""
import json
import glob

# Find the eval file
eval_files = sorted(glob.glob("results/eval_qwen2.5-coder_7b_*.json"))
if not eval_files:
    print("No eval file found")
    exit(1)

with open(eval_files[0]) as f:
    data = json.load(f)

print("=== WITHOUT SKILLS: Per-Task Weakness Analysis ===\n")

all_missing_classes = []
all_missing_elements = []
all_missing_aria = []

for task in data["without_skills"]["per_task"]:
    scores = task["scores"]
    composite = task["composite_score"]
    uswds = scores["uswds_classes"]
    structure = scores["html_structure"]
    a11y = scores["accessibility"]
    validity = scores["html_validity"]

    print(f"{task['task_id']} ({task['difficulty']}) {task['task_name']}")
    print(f"  Composite: {composite}")
    print(f"  USWDS Classes: {uswds['score']}")
    if uswds["missing"]:
        print(f"    MISSING: {uswds['missing']}")
        all_missing_classes.extend(uswds["missing"])
    if uswds["found"]:
        print(f"    FOUND:   {uswds['found']}")
    print(f"  HTML Structure: {structure['score']}")
    if structure["missing"]:
        print(f"    MISSING: {structure['missing']}")
        all_missing_elements.extend(structure["missing"])
    print(f"  Accessibility: {a11y['score']}")
    if a11y["missing_expected"]:
        print(f"    MISSING: {a11y['missing_expected']}")
        all_missing_aria.extend(a11y["missing_expected"])
    print(f"  Validity: {validity['score']}")
    if validity["issues"]:
        print(f"    ISSUES: {validity['issues']}")
    print()

print("\n=== AGGREGATE WEAKNESS SUMMARY ===\n")

from collections import Counter

print("Most frequently missing USWDS classes:")
for cls, count in Counter(all_missing_classes).most_common():
    print(f"  {cls} (missing in {count} task(s))")

print("\nMost frequently missing HTML elements:")
for el, count in Counter(all_missing_elements).most_common():
    print(f"  {el} (missing in {count} task(s))")

print("\nMost frequently missing accessibility attributes:")
for attr, count in Counter(all_missing_aria).most_common():
    print(f"  {attr} (missing in {count} task(s))")

# Identify lowest-scoring tasks
print("\n=== TASKS RANKED BY COMPOSITE (worst first) ===\n")
ranked = sorted(data["without_skills"]["per_task"], key=lambda t: t["composite_score"])
for task in ranked:
    print(f"  {task['composite_score']:.3f}  {task['task_id']} - {task['task_name']}")
