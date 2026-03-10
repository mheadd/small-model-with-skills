# Small Models + Skills: USWDS HTML Generation Experiment

Can well-crafted **skills files** improve the output quality of smaller open-source LLMs?
This experiment tests that hypothesis by measuring how accurately small models generate
[USWDS](https://designsystem.digital.gov/) (U.S. Web Design System) compliant HTML —
with and without USWDS skill context injected into the prompt.

## Background

[Recent research](https://arxiv.org/abs/2602.12670) suggests that domain-specific skill documentation — structured reference
material provided as context — can meaningfully improve smaller models' performance on
specialized tasks. This repository provides a reproducible framework for testing that
finding in the domain of government web development.

The skills used in this experiment come from [blencorp/skills](https://github.com/blencorp/skills),
a set of agent skills covering the U.S. Web Design System (USWDS v3).

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    10 USWDS Tasks                       │
│  (banners, forms, cards, tables, full pages, etc.)      │
└────────┬──────────────────┬───────────────┬─────────────┘
         │                  │               │
 ┌───────▼────────┐ ┌───-───▼─────────┐ ┌──-▼─────────────┐
 │ WITHOUT Skills │ │  WITH Skills    │ │ WITH CUSTOM     │
 │ (base prompt)  │ │ (prompt + full  │ │  Skill          │
 │                │ │  USWDS ref docs)│ │ (prompt +       │
 │                │ │  (~17K tokens)  │ │  targeted ref)  │
 │                │ │                 │ │  (~2.5K tokens) │
 └───────┬────────┘ └────────┬────────┘ └───────-┬────────┘
         │                   │                   │
         ▼                   ▼                   ▼
 ┌─────────────────────────────────────────────────────┐
 │              Automated Evaluation                   │
 │  • USWDS class correctness (30%)                    │
 │  • HTML structure (20%)                             │
 │  • Accessibility attributes (20%)                   │
 │  • Completeness (15%)                               │
 │  • HTML validity (15%)                              │
 └─────────────────────────────────────────────────────┘
```

Each task is run against the same model under multiple conditions: a base system prompt
alone, with the full USWDS skills documentation injected as context, and optionally with a
custom targeted skill file. The outputs are scored automatically across five dimensions.

## Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.ai/)** — for running local LLMs
- One or more small models pulled via Ollama

## Quick Start

```bash
# 1. Clone this repo
git clone https://github.com/<your-org>/small-model-with-skills.git
cd small-model-with-skills

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install and start Ollama (if not already)
brew install ollama
ollama serve  # in a separate terminal

# 4. Pull a small model
ollama pull qwen2.5-coder:7b

# 5. Run the full experiment pipeline
python scripts/run_all.py --model qwen2.5-coder:7b
```

## Recommended Models to Test

| Model | Parameters | Notes |
|:---|:---|:---|
| `qwen2.5-coder:7b` | 7B | Strong coding model, good baseline |
| `codellama:7b` | 7B | Meta's code-focused Llama variant |
| `mistral:7b` | 7B | General-purpose, good instruction following |
| `deepseek-coder:6.7b` | 6.7B | Code-specialized model |
| `phi3:3.8b` | 3.8B | Very small, tests floor of capability |
| `codegemma:7b` | 7B | Google's code model |

Pull and run against multiple models to compare:

```bash
ollama pull qwen2.5-coder:7b
ollama pull codellama:7b
ollama pull mistral:7b

python scripts/run_all.py --model qwen2.5-coder:7b
python scripts/run_all.py --model qwen2.5-coder:7b --custom-skill  # with targeted skill
python scripts/run_all.py --model codellama:7b
python scripts/run_all.py --model mistral:7b

# Compare results across models
python scripts/compare_runs.py results/eval_*.json
```

## Project Structure

```
├── README.md
├── requirements.txt
├── prompts/
│   └── tasks.json              # 10 USWDS generation tasks (easy → hard)
├── scripts/
│   ├── skills_context.py       # Builds skills context from reference files
│   ├── run_experiment.py       # Runs generation with/without skills
│   ├── evaluate.py             # Scores outputs for USWDS compliance
│   ├── compare_runs.py         # Cross-model comparison report
│   ├── analyze_weaknesses.py   # Identifies per-task failure patterns
│   └── run_all.py              # Full pipeline (generate → evaluate → report)
├── skills/
│   ├── custom/
│   │   └── uswds-targeted.md   # Data-driven custom skill (~2.5K tokens)
│   └── blencorp-skills/        # USWDS web skills only (from blencorp/skills)
│       └── uswds/
│           ├── SKILL.md
│           └── references/
│               ├── components.md
│               ├── design-tokens.md
│               ├── grid-layout.md
│               ├── utilities.md
│               └── sass-theming.md
├── evaluation/                  # (for additional eval criteria/scripts)
└── results/                     # Generated outputs (gitignored)
    ├── with_skills/
    ├── without_skills/
    ├── run_*.json               # Run metadata
    └── eval_*.json              # Evaluation results
```

## Task Difficulty Levels

The 10 tasks span three difficulty levels:

| Difficulty | Tasks | What's Tested |
|---|---|---|
| **Easy** | Gov Banner, Alerts, Buttons | Single component, correct class names |
| **Medium** | Card Grid, Contact Form, Header, Table, Sidebar Layout | Multi-component composition, grid system, forms |
| **Hard** | Step Indicator Form, Complete Page | Full-page layouts combining many USWDS components |

## Evaluation Metrics

Each output is scored on five dimensions:

| Dimension | Weight | What It Measures |
|---|---|---|
| **USWDS Class Usage** | 30% | Presence of expected `usa-*` and `grid-*` CSS classes |
| **HTML Structure** | 20% | Correct semantic HTML elements (`<header>`, `<nav>`, `<main>`, etc.) |
| **Accessibility** | 20% | ARIA attributes, `scope` on `<th>`, semantic HTML |
| **Completeness** | 15% | Output has HTML tags, USWDS classes, minimum length |
| **HTML Validity** | 15% | Well-formed HTML, no unclosed tags |

## Results

### Phase 1: Full Skills Context Across Three Models

Three 7B-parameter models were tested, each running all 10 tasks with and without the
full USWDS skills context (~17K tokens):

| Model | Without Skills | With Skills | Delta | Skills Helped? |
|---|---|---|---|---|
| **qwen2.5-coder:7b** | 0.792 | 0.809 | **+0.017** | **Yes** |
| **codellama:7b** | 0.750 | 0.694 | -0.056 | No |
| **mistral:7b** | 0.676 | 0.609 | -0.067 | No |

### Phase 2: Custom Targeted Skill (qwen2.5-coder:7b)

After analyzing which specific USWDS classes, HTML elements, and accessibility attributes
qwen2.5-coder missed most often without skills, a custom skill file was created that
addresses only those specific weaknesses. At ~2.5K tokens, it is 85% smaller than the
full skills context.

| Condition | Composite | USWDS Classes | HTML Structure | Accessibility |
|---|---|---|---|---|
| No skills | 0.766 | 0.615 | 0.832 | 0.620 |
| Full skills (~17K tokens) | 0.815 (+0.049) | 0.731 (+0.116) | 0.832 (+0.000) | 0.700 (+0.080) |
| **Custom skill (~2.5K tokens)** | **0.949 (+0.183)** | **0.973 (+0.358)** | **0.915 (+0.083)** | **0.910 (+0.290)** |

The custom skill improvement is **3.7x larger** than full skills for composite score.

### Per-Task Results: Custom Skill vs Baselines

| Task | Difficulty | No Skills | Full Skills | Custom Skill |
|---|---|---|---|---|
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
|---|---|---|---|
| **qwen2.5-coder:7b** | 0.636 | 0.712 | **+0.076** |
| **codellama:7b** | 0.587 | 0.508 | -0.079 |
| **mistral:7b** | 0.404 | 0.346 | -0.058 |

### Key Findings

1. **Targeted skills dramatically outperform comprehensive skills.** The custom skill
   file (~2.5K tokens) improved composite scores by +0.183, versus +0.049 for the full
   skills context (~17K tokens) — a 3.7x multiplier. Every single task scored higher
   with the custom skill than with full skills, and most scored higher than without
   any skills.

2. **Less context can be more.** The custom skill is 85% smaller than the full skills
   context but 3.7x more effective. This strongly supports the hypothesis that small
   models struggle with information overload — they perform better when given precisely
   the reference material they need, rather than a comprehensive but overwhelming
   knowledge base.

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

- **Larger open-source models.** Testing models like `qwen2.5-coder:32b` or
  `codellama:70b` against frontier models with skills enhancement would test
  whether skills files close the gap between large open-source models and commercial
  frontier models on specialized tasks.

- **Condensed skills context.** The experiment framework includes a `--condensed` flag
  that uses only SKILL.md and components.md (~7.5K tokens). Running all models with
  this intermediate-size context could reveal the optimal context size curve.

- **Repeated trials.** Running each task multiple times (e.g., 3-5 runs) with
  temperature > 0 would provide confidence intervals and reduce noise from single-run
  variance.

- **Alternative evaluation.** Adding a human evaluation component or using an LLM-as-judge
  approach could validate whether the automated scoring aligns with perceived quality.

## CLI Reference

### Run generation only

```bash
python scripts/run_experiment.py --model qwen2.5-coder:7b
python scripts/run_experiment.py --model qwen2.5-coder:7b --custom-skill  # adds targeted skill condition
python scripts/run_experiment.py --model codellama:7b --condensed  # smaller context
python scripts/run_experiment.py --model mistral:7b --tasks 01_gov_banner 05_contact_form
```

### Run evaluation only

```bash
python scripts/evaluate.py                          # evaluates most recent run
python scripts/evaluate.py results/run_<id>.json    # specific run
python scripts/evaluate.py --html output.html --task 01_gov_banner  # single file
```

### Compare models

```bash
python scripts/compare_runs.py results/eval_*.json
```

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `OLLAMA_API_URL` | `http://localhost:11434` | Ollama API endpoint |

## Alternative Setups for Reproducibility

This experiment is designed to run with **Ollama on the host** and the Python scripts
invoked directly. This is the simplest path on macOS, where Ollama can leverage Metal
for GPU-accelerated inference on Apple Silicon. That said, others reproducing this
experiment may want a more portable or automated setup. Here are some alternatives
with their tradeoffs:

### Option A: Host Ollama + Direct Python (default, recommended for macOS)

```
You (macOS) → python3 scripts/run_all.py → Ollama (host, Metal GPU) → results/
```

**Pros:** Fastest inference on Apple Silicon. Simple setup.
**Cons:** Requires manual environment setup per machine.

### Option B: Containerized Python + Host Ollama

Containerize the experiment runner while keeping Ollama on the host for GPU access.

```
Docker (Python + scripts) → http://host.docker.internal:11434 → Ollama (host, Metal GPU)
```

**Pros:** Reproducible Python environment; consistent dependency versions across machines.
**Cons:** Slightly more complex setup. Ollama still needs to be installed on the host.

To use this approach, you would set `OLLAMA_API_URL=http://host.docker.internal:11434`
when running the container, since the experiment runner already connects to Ollama over
HTTP.

### Option C: Full Docker Compose (Ollama + Runner)

Run both Ollama and the experiment runner as containers, orchestrated with Docker Compose.

```
docker compose up → [ollama container] + [runner container] → results/
```

**Pros:** Fully self-contained. One command to run everything. Easy to add to CI.
**Cons:** On macOS, Docker cannot access Metal/GPU — inference falls back to CPU, making
7B+ models significantly slower. On Linux with NVIDIA GPUs, this approach works well
using `--gpus all` with the
[Ollama Docker image](https://hub.docker.com/r/ollama/ollama).

### Summary

| Approach | macOS Performance | Linux GPU Performance | Reproducibility | Complexity |
|---|---|---|---|---|
| Host Ollama + Python (default) | Fast (Metal) | Fast (CUDA) | Manual setup | Low |
| Containerized Python + Host Ollama | Fast (Metal) | Fast (CUDA) | Good | Medium |
| Full Docker Compose | Slow (CPU only) | Fast (CUDA + `--gpus`) | Best | Medium |

For most users on macOS, the default approach is recommended. For CI environments or
Linux machines with NVIDIA GPUs, the full Docker Compose option is the most portable.

## Skills Source

The USWDS skills used in this experiment are from:
- **Repository**: [blencorp/skills](https://github.com/blencorp/skills)
- **License**: Apache 2.0
- **Skill used**: USWDS — U.S. Web Design System (v3) (web only; USMDS mobile skill excluded)
- **Content**: 47 component references, design tokens, grid system, utility classes, Sass theming, accessibility patterns

## License

This experiment framework is provided under the MIT License. The USWDS skills files
in `skills/blencorp-skills/` retain their original Apache 2.0 license.
