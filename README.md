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
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
       ┌───────▼───────-─┐    ┌───────▼--───────────┐
       │  WITHOUT Skills │    │   WITH Skills       │
       │  (base prompt)  │    │  (prompt + USWDS    │
       │                 │    │   reference docs)   │
       └───────┬─────────┘    └────────┬────────────┘
               │                       │
               ▼                       ▼
       ┌─────────────────────────────────────────┐
       │          Automated Evaluation           │
       │  • USWDS class correctness (30%)        │
       │  • HTML structure (20%)                 │
       │  • Accessibility attributes (20%)       │
       │  • Completeness (15%)                   │
       │  • HTML validity (15%)                  │
       └─────────────────────────────────────────┘
```

Each task is run twice against the same model — once with only a base system prompt, and
once with the full USWDS skills documentation injected as context. The outputs are then
scored automatically across five dimensions and compared.

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
|---|---|---|
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
│   └── run_all.py              # Full pipeline (generate → evaluate → report)
├── skills/
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

Three 7B-parameter models were tested, each running all 10 tasks with and without the
full USWDS skills context (~17K tokens):

| Model | Without Skills | With Skills | Delta | Skills Helped? |
|---|---|---|---|---|
| **qwen2.5-coder:7b** | 0.792 | 0.809 | **+0.017** | **Yes** |
| **codellama:7b** | 0.750 | 0.694 | -0.056 | No |
| **mistral:7b** | 0.676 | 0.609 | -0.067 | No |

### USWDS Class Accuracy (the metric most directly targeted by skills)

| Model | Without Skills | With Skills | Delta |
|---|---|---|---|
| **qwen2.5-coder:7b** | 0.636 | 0.712 | **+0.076** |
| **codellama:7b** | 0.587 | 0.508 | -0.079 |
| **mistral:7b** | 0.404 | 0.346 | -0.058 |

### By Task Difficulty (qwen2.5-coder:7b, the only model that improved)

| Difficulty | Without Skills | With Skills | Delta |
|---|---|---|---|
| Easy (n=3) | 0.719 | 0.819 | **+0.100** |
| Medium (n=5) | 0.846 | 0.865 | **+0.019** |
| Hard (n=2) | 0.769 | 0.653 | -0.116 |

### Key Findings

1. **Skills context is not universally beneficial for small models.** Only one of three
   7B models (qwen2.5-coder) showed improvement. The other two degraded across all
   metrics.

2. **Context window overload matters.** The full skills context is ~17K tokens — a
   substantial fraction of a 7B model's effective context window. For codellama and
   mistral, this appears to have overwhelmed the model, consistent with recent research
   suggesting that overloading context windows with too much detail can degrade output
   quality rather than enhance it. Generation times for these models increased 3-5x
   with skills, and some codellama tasks exceeded 300 seconds.

3. **The model's baseline capability is a prerequisite.** qwen2.5-coder already had the
   strongest baseline without skills (0.792), suggesting that a model needs sufficient
   pre-existing knowledge of the domain (HTML/CSS) before it can effectively leverage
   reference documentation. Models that lack that foundation may be distracted rather
   than aided by detailed context.

4. **Skills help most on simpler, focused tasks.** Even for qwen2.5-coder, the benefit
   was concentrated on easy (+0.100) and medium (+0.019) tasks. On hard tasks requiring
   multi-component page assembly, performance dropped (-0.116) — suggesting that complex
   prompts combined with large reference contexts can exceed what a small model can
   effectively synthesize.

5. **Component-specific accuracy is where skills shine.** The Gov Banner task jumped
   from 0.585 → 0.885 with skills for qwen2.5-coder — a +0.300 improvement on a
   component with very specific, non-obvious class names (`usa-banner__header`,
   `usa-banner__content`). This is exactly the kind of factual recall that reference
   documentation excels at providing.

## Future Work

Several directions could extend this experiment:

- **Larger open-source models.** Testing models like `qwen2.5-coder:32b` or
  `codellama:70b` against frontier models with skills enhancement would test a
  different hypothesis: can skills files close the gap between large open-source models
  and commercial frontier models on specialized tasks? This would likely require
  specialized hardware (GPU servers with 24GB+ VRAM) to run effectively.

- **Condensed skills context.** The experiment framework includes a `--condensed` flag
  that uses only SKILL.md and components.md (~7.5K tokens vs ~17K). Running all models
  with the condensed context could reveal whether the performance degradation seen in
  codellama and mistral is primarily a context length issue. If a shorter context
  restores or improves their performance, that would strongly support the context
  overload hypothesis.

- **Skills file optimization.** Rather than injecting the entire reference library,
  a smarter approach might select only the relevant subset of skills content based on
  the task prompt (e.g., only card + grid references for a card grid task). This would
  test whether targeted, minimal context outperforms comprehensive context.

- **Repeated trials.** Running each task multiple times (e.g., 3-5 runs) with
  temperature > 0 would provide confidence intervals and reduce noise from single-run
  variance.

- **Alternative evaluation.** Adding a human evaluation component or using an LLM-as-judge
  approach could validate whether the automated scoring aligns with perceived quality.

## CLI Reference

### Run generation only

```bash
python scripts/run_experiment.py --model qwen2.5-coder:7b
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
