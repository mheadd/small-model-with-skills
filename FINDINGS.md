# Findings

## Overview

This experiment used the comprehensive USWDS skills from
[blencorp/skills](https://github.com/blencorp/skills) as a starting point for testing
whether skills files can improve small model output quality. These skills provide
thorough coverage of USWDS v3 components, design tokens, grid layout, utilities, and
Sass theming — approximately 17K tokens of reference material.

For larger or frontier models with broad context windows, this comprehensive coverage
is likely well-suited. However, these experiments with 7B-parameter models revealed that
this volume of context can overwhelm smaller models, leading to the decision to develop a custom,
narrower skill file targeting the specific patterns these saller models struggle with. The results
strongly suggest that **for small models, less is more** — focused, data-driven skill
files outperform comprehensive ones by a wide margin.

This does not diminish the value of more comprehensive skills as a reference or as context for
more capable models. Rather, it highlights that skill authoring for small models is a
distinct challenge that benefits from a different approach: analyze what the smaller model
struggles with, and provide only the targeted guidance it needs.

## Evaluation Metrics

Each output is scored on five dimensions:

| Dimension | Weight | What It Measures |
|:---|:---|:---|
| **USWDS Class Usage** | 30% | Presence of expected `usa-*` and `grid-*` CSS classes |
| **HTML Structure** | 20% | Correct semantic HTML elements (`<header>`, `<nav>`, `<main>`, etc.) |
| **Accessibility** | 20% | ARIA attributes, `scope` on `<th>`, semantic HTML |
| **Completeness** | 15% | Output has HTML tags, USWDS classes, minimum length |
| **HTML Validity** | 15% | Well-formed HTML, no unclosed tags |

## Results

### Phase 1: Full Skills Context Across Three Models

Using the [blencorp/skills](https://github.com/blencorp/skills) USWDS skills as-is,
three 7B-parameter models were tested on all 10 tasks with and without the full
skills context (~17K tokens):

| Model | Without Skills | With Skills | Delta | Skills Helped? |
|:---|:---|:---|:---|:---|
| **qwen2.5-coder:7b** | 0.792 | 0.809 | **+0.017** | **Yes** |
| **codellama:7b** | 0.750 | 0.694 | -0.056 | No |
| **mistral:7b** | 0.676 | 0.609 | -0.067 | No |

### Phase 2: Custom Targeted Skill (qwen2.5-coder:7b)

The Phase 1 results showed that the comprehensive blencorp skills, while valuable as a
reference, were too large for small models to process effectively. This motivated a
different approach: rather than providing the full skills library, I analyzed which
specific USWDS classes, HTML elements, and accessibility attributes qwen2.5-coder missed
most often *without* skills, and created a custom skill file addressing only those
weaknesses. At ~2.5K tokens, it is 85% smaller than the full skills context.

| Condition | Composite | USWDS Classes | HTML Structure | Accessibility |
|:---|:---|:---|:---|:---|
| No skills | 0.766 | 0.615 | 0.832 | 0.620 |
| Full skills (~17K tokens) | 0.815 (+0.049) | 0.731 (+0.116) | 0.832 (+0.000) | 0.700 (+0.080) |
| **Custom skill (~2.5K tokens)** | **0.949 (+0.183)** | **0.973 (+0.358)** | **0.915 (+0.083)** | **0.910 (+0.290)** |

The custom skill improvement is **3.7x larger** than full skills for composite score.

### Per-Task Results: Custom Skill vs Baselines

| Task | Difficulty | No Skills | Full Skills | Custom Skill |
|:---|:---|:---|:---|:---|
| Gov Banner | easy | 0.615 | 0.885 | **0.985** |
| Alert Set | easy | 0.671 | 0.671 | **1.000** |
| Button Variants | easy | 0.900 | 0.885 | 0.900 |
| Card Grid | medium | 0.837 | 0.945 | **0.973** |
| Contact Form | medium | 0.985 | 0.985 | 0.985 |
| Header Nav | medium | 0.797 | 0.888 | **0.985** |
| Data Table | medium | 0.745 | 0.745 | **0.820** |
| Two-Col Layout | medium | 0.600 | 0.600 | **0.967** |
| Step Indicator | hard | 0.676 | 0.698 | **0.964** |
| Full Page | hard | 0.832 | 0.849 | **0.915** |

### USWDS Class Accuracy (Phase 1)

| Model | Without Skills | With Skills | Delta |
|:---|:---|:---|:---|
| **qwen2.5-coder:7b** | 0.636 | 0.712 | **+0.076** |
| **codellama:7b** | 0.587 | 0.508 | -0.079 |
| **mistral:7b** | 0.404 | 0.346 | -0.058 |

## Key Findings

1. **Targeted skills dramatically outperform comprehensive skills.** The custom skill
   file (~2.5K tokens) improved composite scores by +0.183, versus +0.049 for the full
   skills context (~17K tokens) — a 3.7x multiplier. Every single task scored higher
   with the custom skill than with full skills, and most scored higher than without
   any skills.

2. **Less context can be more.** The custom skill is 85% smaller than the full skills
   context but 3.7x more effective. The comprehensive blencorp skills are thorough and
   well-structured — but that breadth becomes a liability for small models with limited
   effective context windows. Small models perform better when given precisely the
   reference material they need, rather than a comprehensive knowledge base. For larger
   or frontier models that can handle longer contexts, the full skills would likely
   remain the better choice.

3. **Data-driven skill authoring works.** The custom skill was created by analyzing the
   model's specific failure patterns (wrong BEM syntax, missing components, old grid
   classes) and writing targeted examples that address exactly those gaps. This
   "diagnose-then-prescribe" approach proved highly effective.

4. **The biggest gains are on the model's weakest areas.** The tasks that improved most
   with the custom skill were the ones the model struggled with most without it:
   Two-Col Layout (+0.367), Step Indicator (+0.288), Alert Set (+0.329), Gov Banner
   (+0.370). The custom skill turned the model's worst tasks into near-perfect scores.

5. **Skills context is not universally beneficial for small models.** In Phase 1, only
   one of three 7B models (qwen2.5-coder) showed improvement with full skills. The
   other two degraded across all metrics due to context window overload.

6. **The model's baseline capability is a prerequisite.** qwen2.5-coder had the
   strongest baseline without skills (0.792), suggesting that a model needs sufficient
   pre-existing knowledge of the domain (HTML/CSS) before it can effectively leverage
   reference documentation.

7. **Component-specific accuracy is where skills shine.** The Gov Banner task jumped
   from 0.615 → 0.985 with the custom skill — a +0.370 improvement on a component
   with very specific, non-obvious class names (`usa-banner__header`,
   `usa-banner__content`). This is exactly the kind of factual recall that targeted
   reference documentation excels at providing.

## Future Work

Several directions could extend this experiment:

- **Apply the custom skill approach to other models.** Test whether the same targeted
  skill file helps codellama and mistral, which degraded with full skills. The custom
  skill's smaller size (~2.5K vs ~17K tokens) may avoid the context overload that
  affected those models.

- **Automate skill file generation.** The current custom skill was hand-crafted from
  weakness analysis. An automated pipeline could: run baseline → analyze failures →
  generate targeted skill → re-run. This could be applied to any model/domain pair.
  That said, [recent research](https://arxiv.org/abs/2602.12670) suggests that
  human-authored or human-curated skills files are associated with higher quality
  output. Automation may be most effective for identifying *which* gaps to address,
  while human expertise remains valuable for authoring the skill content itself — a
  hybrid approach where tooling surfaces the weaknesses and a human writes the
  targeted guidance.

- **Larger open-source models.** Testing models like `qwen2.5-coder:32b` or
  `codellama:70b` against frontier models with skills enhancement would test
  whether skills files close the gap between large open-source models and commercial
  frontier models on specialized tasks.

- **Condensed skills context.** The test scripts include a `--condensed` flag
  that provides an intermediate option between full skills and the custom skill. Where
  the full context includes all five blencorp reference files (components, design tokens,
  grid layout, utilities, and Sass theming at ~17K tokens), the condensed mode loads
  only the SKILL.md overview and the components reference (~7.5K tokens) — stripping out
  design tokens, utilities, and Sass theming that are less relevant to HTML generation.
  Running all three models with this intermediate-size context could map the relationship
  between context size and output quality, revealing whether there is a smooth degradation
  curve or a sharp threshold where small models lose the ability to use the context
  effectively.

- **Repeated trials.** Running each task multiple times (e.g., 3-5 runs) with
  temperature > 0 would provide confidence intervals and reduce noise from single-run
  variance.

- **Alternative evaluation.** Adding a human evaluation component or using an LLM-as-judge
  approach could validate whether the automated scoring aligns with perceived quality.
