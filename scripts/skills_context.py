"""
Build the USWDS skills context string from the blencorp/skills repo files.

This module reads the SKILL.md and reference files from the cloned skills repo
and assembles them into a single context string that can be prepended to prompts.
"""

import os
from pathlib import Path


SKILLS_DIR = Path(__file__).parent.parent / "skills" / "blencorp-skills" / "uswds"
CUSTOM_SKILL_FILE = Path(__file__).parent.parent / "skills" / "custom" / "uswds-targeted.md"


def load_skill_file(filepath: Path) -> str:
    """Read a skill file and return its content."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def build_skills_context() -> str:
    """
    Assemble the full USWDS skills context from all reference files.

    Returns a single string containing the SKILL.md overview and all
    reference documents, suitable for injection into an LLM prompt.
    """
    sections = []

    # Main skill file
    skill_md = SKILLS_DIR / "SKILL.md"
    if skill_md.exists():
        sections.append(load_skill_file(skill_md))

    # Reference files in priority order
    ref_dir = SKILLS_DIR / "references"
    ref_files = [
        "components.md",
        "design-tokens.md",
        "grid-layout.md",
        "utilities.md",
        "sass-theming.md",
    ]

    for ref_file in ref_files:
        filepath = ref_dir / ref_file
        if filepath.exists():
            sections.append(load_skill_file(filepath))

    return "\n\n---\n\n".join(sections)


def build_condensed_context() -> str:
    """
    Build a shorter version of the skills context that fits within
    smaller context windows. Uses only SKILL.md and components.md.
    """
    sections = []

    skill_md = SKILLS_DIR / "SKILL.md"
    if skill_md.exists():
        sections.append(load_skill_file(skill_md))

    components = SKILLS_DIR / "references" / "components.md"
    if components.exists():
        sections.append(load_skill_file(components))

    return "\n\n---\n\n".join(sections)


def build_custom_context() -> str:
    """
    Build a targeted skills context from the custom skill file.
    This is a data-driven skill file created from weakness analysis of
    qwen2.5-coder:7b outputs, focusing on the specific USWDS patterns
    the model gets wrong most often.
    """
    if CUSTOM_SKILL_FILE.exists():
        return load_skill_file(CUSTOM_SKILL_FILE)
    return ""


def get_context_stats() -> dict:
    """Return character and approximate token counts for the skills context."""
    full = build_skills_context()
    condensed = build_condensed_context()
    custom = build_custom_context()
    return {
        "full_chars": len(full),
        "full_approx_tokens": len(full) // 4,
        "condensed_chars": len(condensed),
        "condensed_approx_tokens": len(condensed) // 4,
        "custom_chars": len(custom),
        "custom_approx_tokens": len(custom) // 4,
    }


if __name__ == "__main__":
    stats = get_context_stats()
    print("Skills Context Statistics:")
    print(f"  Full context:      {stats['full_chars']:,} chars (~{stats['full_approx_tokens']:,} tokens)")
    print(f"  Condensed context: {stats['condensed_chars']:,} chars (~{stats['condensed_approx_tokens']:,} tokens)")
    print(f"  Custom context:    {stats['custom_chars']:,} chars (~{stats['custom_approx_tokens']:,} tokens)")
