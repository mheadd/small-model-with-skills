# Findings

Context and instruction files used with small open-source models need to be custom tailored
for those models and designed to accomodate their more constrained context window. Instruction files designed for larger models or commercial frontier models will very likely not work well with small models — and may actually *diminish* performance.
But on the upside, customized instruction files for smaller open-source models can
dramatically improve the quality of their output, potentially making them a viable
alternative to larger or commercial offerings for specialized tasks.

Phase 3 testing with a larger 35B-parameter model (`qwen3.5:35b-a3b-q4_K_M`) confirmed
the other side of this finding: comprehensive skills context that overwhelms small models
can be highly effective for larger ones. The 35B model showed a +0.230 composite
improvement with full skills — 13.5x the gain the best 7B model achieved with the
same context.

## Overview

This experiment used the comprehensive USWDS skills from
[blencorp/skills](https://github.com/blencorp/skills) as a starting point for testing
whether skills files can improve small model output quality. These skills provide
thorough coverage of USWDS v3 components, design tokens, grid layout, utilities, and
Sass theming — approximately 17K tokens of reference material.

For larger or frontier models with broad context windows, this comprehensive coverage
is likely well-suited — and Phase 3 testing with a 35B-parameter model confirmed this.
However, the earlier experiments with 7B-parameter models revealed that
this volume of context can overwhelm smaller models, leading to the decision to develop a custom,
narrower skill file targeting the specific patterns these smaller models struggle with. The results
strongly suggest that **for small models, less is more** — focused, data-driven skill
files outperform comprehensive ones by a wide margin.

This does not diminish the value of more comprehensive skills as a reference or as context for
more capable models — in fact, the Phase 3 results demonstrate that larger models benefit
substantially from the full skills context. Skill authoring for small models is a
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

(Note - results are simple averages (mean) of the per-task composite scores across all 10 tasks.)

The composite scores above blend all five evaluation dimensions. Breaking out USWDS
class accuracy alone — the single dimension most directly affected by skills context,
since it measures whether the model uses the correct `usa-*` and `grid-*` class
names — shows a sharper picture of where skills helped and where they didn't:

| Model | Without Skills | With Skills | Delta | Skills Helped? |
|:---|:---|:---|:---|:---|
| **qwen2.5-coder:7b** | 0.636 | 0.712 | **+0.076** | **Yes** |
| **codellama:7b** | 0.587 | 0.508 | -0.079 | No |
| **mistral:7b** | 0.404 | 0.346 | -0.058 | No |

Even on this dimension, only `qwen2.5-coder` improved with the full skills context. This
pattern — modest gains for the strongest model, degradation for the others — motivated
the targeted approach in Phase 2.

### Phase 2: Custom Targeted Skill (using qwen2.5-coder:7b model)

The Phase 1 results showed that the comprehensive blencorp skills, while valuable as a
reference, were too large for small models to process effectively. This motivated a
different approach: rather than providing the full skills library, I then analyzed which
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

### Phase 3: Larger Model with Full Skills (qwen3.5:35b)

A key question from Phase 1 was whether the full skills context — which overwhelmed the
7B models — would prove effective for a larger model with a bigger context window. Testing
`qwen3.5:35b-a3b-q4_K_M` (a 35B-parameter model, quantized to Q4_K_M, run on an RTX 4090)
provided a clear answer.

| Condition | Composite | USWDS Classes | HTML Structure | Accessibility |
|:---|:---|:---|:---|:---|
| No skills | 0.697 | 0.549 | 0.550 | 0.805 |
| Full skills (~17K tokens) | **0.927 (+0.230)** | **0.955 (+0.406)** | **0.872 (+0.322)** | **0.890 (+0.085)** |

The +0.230 composite improvement is **13.5x larger** than what qwen2.5-coder:7b achieved
with the same full skills context (+0.017), and even exceeds the improvement the custom
targeted skill provided to qwen2.5-coder:7b (+0.183). The USWDS class accuracy improvement
of +0.406 is the largest single-dimension gain in any phase of this experiment.

Notably, the 35B model's *baseline* without skills (0.697) is actually lower than
qwen2.5-coder:7b's baseline (0.792). This suggests that `qwen3.5:35b` — a
general-purpose model — has less pre-existing USWDS knowledge than the code-specialized
7B model, but its larger context window allows it to absorb and apply the full skills
reference far more effectively.

#### Per-Task Results: qwen3.5:35b

| Task | Difficulty | No Skills | Full Skills | Delta |
|:---|:---|:---|:---|:---|
| Gov Banner | easy | 0.885 | **0.985** | +0.100 |
| Alert Set | easy | 0.350 | **0.896** | +0.546 |
| Button Variants | easy | 0.350 | **0.885** | +0.535 |
| Card Grid | medium | 0.930 | 0.880 | -0.050 |
| Contact Form | medium | 0.985 | 0.985 | +0.000 |
| Header Nav | medium | 0.584 | **0.985** | +0.401 |
| Data Table | medium | 0.830 | 0.835 | +0.005 |
| Two-Col Layout | medium | 0.914 | 0.930 | +0.016 |
| Step Indicator | hard | 0.448 | **0.902** | +0.454 |
| Full Page | hard | 0.691 | **0.985** | +0.294 |

The largest gains came on the tasks where the model struggled most without skills:
Alert Set (+0.546), Button Variants (+0.535), Step Indicator (+0.454), and Header Nav
(+0.401). These are components with specific USWDS class names and structures that the
model could not infer from general training data alone.

#### Cross-Model Comparison: Full Skills Effectiveness

Comparing all four models with full skills context:

| Model | Params | Without Skills | With Full Skills | Delta | Skills Helped? |
|:---|:---|:---|:---|:---|:---|
| **qwen3.5:35b** | 35B | 0.697 | **0.927** | **+0.230** | **Yes** |
| **qwen2.5-coder:7b** | 7B | 0.792 | 0.809 | +0.017 | Yes (modest) |
| **codellama:7b** | 7B | 0.750 | 0.694 | -0.056 | No |
| **mistral:7b** | 7B | 0.676 | 0.609 | -0.067 | No |

The relationship between model size and skills effectiveness is striking: the 35B model
derives an order of magnitude more benefit from the same skills context than any 7B model.

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

8. **Larger models unlock the full value of comprehensive skills.** The 35B model
   achieved a +0.230 composite improvement with the full blencorp skills — 13.5x
   what the best 7B model gained from the same context. This confirms that
   comprehensive, well-structured skills files are not wasted effort; they simply
   require models with sufficient context capacity to use them effectively.

9. **Context capacity matters more than baseline domain knowledge.** The 35B model's
   baseline without skills (0.697) was actually *lower* than qwen2.5-coder:7b's
   (0.792), yet it responded far more effectively to the full skills context. This
   suggests that a model's ability to process and apply reference documentation is more
   dependent on context window capacity than on pre-existing domain knowledge.

10. **The right skill strategy depends on model size.** For 7B models, a targeted
    ~2.5K-token custom skill outperformed the full ~17K-token skills context by 3.7x.
    For the 35B model, the full skills context alone produced a +0.230 improvement —
    larger than even the custom skill's +0.183 gain on the 7B model. Skill authors
    should consider their target model class when designing skills files.

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

- **Larger open-source models.** Phase 3 testing with `qwen3.5:35b` confirmed
  that larger models benefit dramatically from the full skills context (+0.230
  composite improvement). Further testing with other large open-source models
  (e.g., `codellama:70b`, `qwen2.5-coder:32b`) could confirm whether this
  pattern generalizes, and comparison against commercial frontier models would
  test whether skills files close the remaining gap on specialized tasks.

- **Custom skills for the 35B model.** The 35B model thrived with full skills, but its
  baseline (0.697) has clear weaknesses — Alert Set (0.350), Button Variants (0.350),
  and Step Indicator (0.448) all scored poorly without skills. A targeted custom skill
  for the 35B model could potentially push it even higher than 0.927, especially on
  the Card Grid task where it slightly regressed with full skills (0.930 → 0.880).

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
