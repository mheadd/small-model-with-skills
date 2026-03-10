# Small Models + Skills: USWDS HTML Generation Experiment

Can well-crafted **skills files** improve the output quality of smaller open-source LLMs?
This experiment tests that hypothesis by measuring how accurately small models generate
[USWDS](https://designsystem.digital.gov/) (U.S. Web Design System) compliant HTML —
with and without USWDS skill context injected into the prompt.

## Background

Recent research suggests that domain-specific skill documentation — structured reference
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
       ┌───────▼────────┐    ┌────────▼───────────┐
       │  WITHOUT Skills │    │   WITH Skills       │
       │  (base prompt)  │    │  (prompt + USWDS    │
       │                 │    │   reference docs)    │
       └───────┬─────────┘    └────────┬────────────┘
               │                       │
               ▼                       ▼
       ┌─────────────────────────────────────────┐
       │          Automated Evaluation            │
       │  • USWDS class correctness (30%)        │
       │  • HTML structure (20%)                  │
       │  • Accessibility attributes (20%)        │
       │  • Completeness (15%)                    │
       │  • HTML validity (15%)                   │
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
