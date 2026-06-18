# Council

Multi-agent AI marketing council for turning a company brief into a structured go-to-market plan.

`council` runs four specialist agents in parallel, lets them critique each other over several rounds, and writes the resulting strategy artifacts to a local workspace. It is a Python `src/` layout package with the console command `council` and the equivalent module entrypoint `python -m council`.

## What It Does

- Runs four marketing strategy agents: Marcus (offer), Elena (funnel), Kai (copy), and David (ABM/leads).
- Orchestrates round-based debate with `asyncio`, shared discussion files, state tracking, retries, and timeouts.
- Supports real LLM providers plus zero-key demo runs.
- Loads company configuration from JSON templates or your own config file.
- Injects extra context from Markdown/text documents, document directories, or an inline brief.
- Writes final deliverables, a combined proposal, a manifest, and observability traces.
- Provides an interactive terminal menu, optional live dashboard, artifact review, and streaming output.

## Requirements

- Python `>=3.12`
- Package name: `council`
- CLI command after installation: `council`
- Source package: `src/council`

Core dependencies are declared in `pyproject.toml`: Pydantic v2, Jinja2, aiohttp, OpenAI, Anthropic, Rich, and Textual. LiteLLM support is optional via the `litellm` extra.

## Quick Start

```bash
git clone https://github.com/borek707/scalac_ai_council.git
cd scalac_ai_council
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Check the CLI:

```bash
council --help
# or
python -m council --help
```

Run a no-key demo:

```bash
council --demo --scenario saas-launch --rounds 2
```

Run with a built-in template:

```bash
export OPENAI_API_KEY="sk-..."
council --template saas --rounds 3
```

Run with your own company config:

```bash
council --config my_company.json --provider openai --rounds 3
```

Running `council` with no flags launches the interactive menu.

## Providers

The CLI currently supports these providers:

| Provider | CLI value | Default model / behavior | Credential |
| --- | --- | --- | --- |
| OpenAI | `openai` | `gpt-4o` | `OPENAI_API_KEY` or `--api-key` |
| Anthropic Claude | `anthropic` | `claude-sonnet-4-6` | `ANTHROPIC_API_KEY` or `--api-key` |
| OpenRouter | `openrouter` | free-tier model chain by default unless `--no-free-tier` is passed | `OPENROUTER_API_KEY` or `--api-key` |
| Ollama | `ollama` | `llama3` | local Ollama server |
| Kimi Code | `kimi-code` | `kimi-for-coding` | local Kimi Code CLI/session |
| Claude Code | `claude-code` | `claude-sonnet-4-6` | Claude CLI/session or local Claude credentials |
| LiteLLM | `litellm` | `openai/gpt-4o` | upstream provider credentials |

Examples:

```bash
# Anthropic
council --template consulting --provider anthropic

# OpenRouter, explicitly disable free-tier fallback
council --template fintech --provider openrouter --no-free-tier --model anthropic/claude-sonnet-4

# Local Ollama
council --template ecommerce --provider ollama --model llama3

# Kimi Code or Claude Code local agent providers
council --template saas --provider kimi-code
council --template saas --provider claude-code

# LiteLLM with fallbacks
pip install -e ".[litellm]"
council --config my_company.json --provider litellm \
  --model openai/gpt-4o \
  --litellm-fallback anthropic/claude-sonnet-4-6 \
  --litellm-fallback openrouter/google/gemini-2.0-flash-exp:free
```

The project also loads a local `.env` from the current working directory before running the CLI.

## Main Usage Patterns

### Demo Mode

Demo mode uses prebuilt scenarios and scripted agent responses, so it does not require API keys.

```bash
council --demo
council --demo --scenario fintech-scale --rounds 2 --dashboard
```

Available scenarios:

- `saas-launch`
- `ecommerce-rebrand`
- `fintech-scale`
- `healthcare-app`

### Templates

Built-in company templates live in `templates/companies/`:

- `consulting`
- `ecommerce`
- `fintech`
- `saas`
- `scalac`

```bash
council --template saas --dashboard
council --template scalac --rounds 3
```

You can list templates with:

```bash
council --template
```

### Custom Config

Use `--config` for your own company JSON file. A minimal shape looks like this:

```json
{
  "name": "Acme Corp",
  "product": "API-first payment platform for SaaS",
  "pricing_tier": "$5K-$50K ACV",
  "value_proposition": "Reduce payment integration time from 3 months to 2 weeks",
  "competitors": [
    {
      "name": "Stripe",
      "threat": "HIGH",
      "pricing": "2.9% + $0.30"
    }
  ],
  "target": {
    "segment": "SaaS companies processing >$1M/year",
    "decision_maker": "CTO / VP Engineering",
    "pain_points": ["Slow integration", "High fees", "Compliance complexity"],
    "budget_range": "$50K-$200K/year"
  },
  "constraints": {
    "timeline_days": 90,
    "team_size": 3
  }
}
```

The schema is validated with Pydantic. See `src/council/config/schema.py` and the files in `templates/companies/` for the current full shape.

### Extra Context

Add campaign research, notes, or customer material to every agent prompt:

```bash
council --config my_company.json --documents brief.md research.md
council --config my_company.json --documents-dir ./research
council --config my_company.json --brief "ABM campaign for CFOs in EU fintech"
```

### Dashboard, Review, And Streaming

```bash
# Live terminal dashboard
council --template saas --dashboard

# Review artifacts from an existing workspace
council --review ./output

# Auto-review after a successful run
council --template saas --review

# LLM-assisted quality review, used together with --review
council --template saas --review --review-ai

# Stream agent output in the console
council --template saas --stream

# Check current discussion files without starting a run
council --monitor --output ./output
```

## Output Layout

`--output` points to a workspace directory. The default is `./output`.

```text
<workspace>/
  config.json
  shared/
    brief.md
    discussion/
      *_round_*.md
  output/
    agents/
      marcus_offer.md
      elena_funnel.md
      kai_copy.md
      david_abm.md
    artifacts/
      reviews/
    manifest.json
    proposal.md
    trace.json
```

With the default `--output ./output`, final files therefore land under `./output/output/`.

## CLI Reference

Common commands:

```bash
council
council --help
council --demo --scenario healthcare-app --rounds 2
council --template saas --rounds 3 --dashboard
council --config my_company.json --provider openai --model gpt-4o-mini
council --config my_company.json --provider openrouter --free-tier
council --config my_company.json --provider litellm --model openai/gpt-4o
council --config my_company.json --rounds 5 --timeout 600
council --config my_company.json --output ./results --force
council --review ./results
council --monitor --output ./results
```

Current option groups include:

- Inputs: `--config`, `--template`, `--scalac-mode`, `--brief`, `--documents`, `--documents-dir`
- Providers: `--provider`, `--model`, `--api-key`, `--free-tier`, `--no-free-tier`, `--litellm-fallback`, `--litellm-api-base`
- Run control: `--rounds`, `--timeout`, `--output`, `--force`, `--stream`
- Interfaces: `--interactive`, `--onboarding`, `--dashboard`, `--platform`
- Inspection: `--monitor`, `--review`, `--review-ai`
- Compatibility: `--aggregate` is still accepted but artifacts are written automatically

Run `council --help` for the authoritative list.

## Project Structure

```text
scalac_ai_council/
  pyproject.toml
  README.md
  src/
    council/
      __main__.py
      cli.py
      service.py
      agents/
      config/
      llm/
      orchestration/
      platform/
      prompts/
      vis/
  templates/
    companies/
  tests/
    live/
```

Important entrypoints:

- `src/council/cli.py` defines the CLI and command-line options.
- `src/council/llm/factory.py` constructs supported LLM providers.
- `src/council/service.py` coordinates a council run.
- `src/council/orchestration/` contains the async orchestration layer.
- `src/council/agents/` contains agent implementations and prompt templates.
- `src/council/config/schema.py` defines the company config schema.

## Development

Install development dependencies:

```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

Useful checks:

```bash
pytest
pytest -m "not live"
pytest --cov=council --cov-report=html --cov-fail-under=80 tests/
mypy src/
ruff check .
black --check .
```

The project configuration also supports `uv`:

```bash
uv run pytest -m "not live"
uv run mypy src/
uv run ruff check .
uv run black --check .
```

Live provider tests are opt-in because they call external services and may spend credits:

```bash
OPENROUTER_API_KEY="sk-or-..." uv run pytest tests/live -m live
```

## License

MIT. See `LICENSE` if present.
