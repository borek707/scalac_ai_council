# Council

Council is a multi-agent AI marketing strategy system. It turns a company brief, structured market context, and optional research documents into a debated go-to-market plan written by four specialist agents: Marcus, Elena, Kai, and David.

The point is not just that four agents write four files. The point is that they work across rounds. Each round is written to a shared workspace, later rounds read the prior discussion, and final outputs reflect critique from several professional perspectives: offer, funnel, copy, and account strategy.

Current package version: `3.3.0`.

## Why Multi-Agent Debate Matters

A single LLM can produce a polished marketing plan, but it often collapses trade-offs into one confident answer. Council keeps the trade-offs visible:

- Pricing and packaging are challenged by funnel conversion reality.
- Funnel assumptions are checked against message clarity and account selection.
- Copy is grounded in positioning, ICP pain, and outreach constraints.
- ABM recommendations are connected back to offer, buying stage, and pipeline.

The system writes both the intermediate debate and the final artifacts to disk, so you can inspect how a recommendation emerged instead of only seeing a finished document.

## What Council Does

Council runs a complete strategy workflow:

- Loads a company config from JSON, a built-in template, Scalac mode, or a demo scenario.
- Injects optional context from Markdown/text documents, a document directory, or `--brief`.
- Builds four named agents with role-specific prompts and final deliverables.
- Runs debate rounds with `asyncio`, state tracking, timeouts, provider routing, and filesystem-backed discussion files.
- Writes round files, final agent outputs, an aggregated proposal, a structured manifest, and observability traces.
- Provides a live Textual dashboard during a run and a read-only Textual artifact browser after a run.
- Supports zero-key demo mode and real LLM providers.

## The Four Agents

Council is built around four named specialists. They all receive the same company configuration, optional brief, optional research documents, and shared discussion history, but each agent is prompted to see the go-to-market problem through a different professional lens.

| Agent | Role | What They Know | Decision Lens | Final Deliverable |
| --- | --- | --- | --- | --- |
| Marcus | Offer Architect | B2B SaaS pricing, packaging, positioning, competitive reframing, commercial narrative | "Is the offer clear, valuable, differentiated, and tied to measurable business outcomes?" | `output/agents/marcus_offer.md` |
| Elena | Funnel Architect | Sales funnel design, pipeline velocity, qualification, stage ownership, conversion math, handoff discipline | "Can this become a measurable revenue system with clear stages, owners, SLAs, and conversion targets?" | `output/agents/elena_funnel.md` |
| Kai | Copywriter | Technical B2B copy, content strategy, brand voice, web copy, email, LinkedIn, CTAs, content angles | "Will the right buyer understand the message quickly, care about it, and take the next specific action?" | `output/agents/kai_copy.md` |
| David | Lead Strategist | ABM, lead generation, target account selection, trigger events, account scoring, outreach plays | "Which accounts should be pursued now, why them, who should be contacted, and with what message?" | `output/agents/david_abm.md` |

### Marcus, Offer Architect

Marcus is responsible for the commercial shape of the recommendation. He works with frameworks such as Gap Selling, StoryBrand, Good-Better-Best tiering, and Challenger Sale. His job is to diagnose the buyer's problem, turn that problem into a compelling offer, define pricing or package logic, and explain why the market should see the company differently from competitors.

Marcus typically focuses on:

- The core problem statement and buyer pain.
- Offer architecture, packages, pricing tiers, guarantees, and value metric logic.
- Competitive positioning and objection handling.
- ROI framing and a business case that a buyer can understand quickly.
- A 30-60-90 day path for launching or refining the offer.

His final file, `output/agents/marcus_offer.md`, is the offer and positioning artifact. It should read like a practical commercial blueprint, not a generic positioning essay.

### Elena, Funnel Architect

Elena turns strategy into a measurable revenue machine. She uses MEDDIC, JOLT, Three Pipelines, and Predictable Revenue to define how prospects move from attention to qualified opportunity to closed revenue. She is deliberately skeptical of vague "awareness" or "engagement" language unless it is connected to stage definitions, exit criteria, owners, and numbers.

Elena typically focuses on:

- Funnel stages with entry and exit criteria.
- Inbound, outbound, and expansion pipeline motions.
- Conversion assumptions, target rates, response times, and SLAs.
- MEDDIC qualification rules and MQL-to-SQL-to-opportunity handoffs.
- Funnel risks, leading indicators, and a 90-day rollout plan.

Her final file, `output/agents/elena_funnel.md`, is the funnel blueprint. It explains how the strategy becomes an operating system for pipeline generation and revenue conversion.

### Kai, Copywriter

Kai translates the offer and funnel into words buyers can understand and act on. He uses AIDA, PAS, Big 5 content, and StoryBrand to produce actual copy, not only copy direction. His role is to make sure the messaging is sharp enough for technical buyers, credible enough for executives, and specific enough to move someone to the next step.

Kai typically focuses on:

- Headline options, hero sections, landing page copy, and message hierarchy.
- Email sequences, LinkedIn ads, nurture copy, and sales enablement language.
- CTAs that say exactly what action the buyer should take.
- Big 5 content topics: cost, problems, comparisons, reviews, and best-of content.
- Brand voice rules, A/B test ideas, and a 90-day content calendar.

His final file, `output/agents/kai_copy.md`, is the copy system. It should contain usable copy blocks and channel-specific messaging, not just strategy notes.

### David, Lead Strategist

David decides where the go-to-market effort should be aimed. He uses ABM Tiers, Dream 100, and Signal-Based Selling to prioritize accounts, contacts, timing signals, and outreach plays. He is the agent most concerned with whether the plan points at the right buyers at the right moment.

David typically focuses on:

- Target account lists, Dream 100 candidates, and ABM tiering.
- ICP scoring based on fit, intent, timing, and buying triggers.
- "Why now" signals such as hiring, funding, technology changes, expansion, regulation, or public initiatives.
- Stakeholder mapping and recommended first-touch messages.
- Tier-specific account plays, channel strategy, engagement metrics, and revenue modeling.

His final file, `output/agents/david_abm.md`, is the ABM and lead strategy artifact. It should identify who to pursue, why they are a fit, what signal makes them timely, and how to approach them.

## How The Agents Work Together

Council is not four independent one-shot prompts. It is a round-based discussion system backed by files on disk. The orchestrator runs the agents in parallel inside each round, waits for the round to finish, then moves to the next round. Every agent writes its contribution to `shared/discussion/`, and later rounds read the discussion files from previous rounds before generating the next response.

The default discussion pattern looks like this:

| Phase | What Happens | Files |
| --- | --- | --- |
| Run setup | The workspace is prepared, the company config is copied, optional brief and documents are loaded, and a run-start marker is written so stale files are ignored. | `config.json`, `shared/brief.md`, `shared/.run_started_at` |
| Round 1 | Marcus, Elena, Kai, and David each produce an initial view from their own specialty. They run concurrently. | `shared/discussion/marcus_round_1.md`, `elena_round_1.md`, `kai_round_1.md`, `david_round_1.md` |
| Round 2+ | Each agent reads the previous discussion history, then critiques, tightens, or builds on what peers wrote. Rounds are sequential, but work inside a round is parallel. | `shared/discussion/*_round_2.md`, `*_round_3.md`, and so on |
| Final synthesis | After debate rounds finish, each agent reads the full discussion history and writes a polished final deliverable from their own domain. | `output/agents/*.md` |
| Aggregation | The system assembles round outputs into a proposal, writes a manifest, and records trace metadata. | `output/proposal.md`, `output/manifest.json`, `output/trace.json` |

In practical terms, each agent sees the debate so far, but still keeps its own responsibility. Marcus should not become a copywriter; Kai should not invent the funnel math; Elena should challenge unfunded assumptions; David should keep pulling the plan back to real accounts and buying signals.

### Example Debate Narrative

The exact output depends on the company config, documents, provider, model, and number of rounds, but a typical debate might unfold like this:

1. Marcus proposes a Good-Better-Best offer: a narrow entry package for fast adoption, a core package tied to the main business outcome, and a premium tier with strategic support. He frames the buyer's old way of working as the hidden cost the product helps eliminate.
2. Elena reads that offer and challenges the economics. If the entry package is too cheap, she may argue that sales-assisted acquisition will not pay back. She may ask for clearer qualification gates, higher-intent CTAs, or a different handoff between marketing and sales.
3. Kai uses Marcus's positioning and Elena's funnel constraints to adjust the message. He might turn a broad claim like "transform your operations" into a more concrete headline, write stage-specific CTAs, and create email copy that handles the objections Marcus listed.
4. David adds account reality. He may point out that the premium package should be aimed only at Tier 1 accounts showing strong timing signals, while lower-touch plays should go to Tier 2 or Tier 3 accounts. He can also suggest that a specific buyer persona needs a different first-touch message.
5. In the next round, Marcus can refine packaging based on funnel payback and ABM tiering, Elena can update conversion assumptions based on the revised offer, Kai can align copy to the sharper account segments, and David can adjust outreach plays to match the final positioning.

This is the core behavior Council is designed to expose: a recommendation is not treated as final until it has been seen through offer, funnel, copy, and account-strategy lenses.

## Quick Start

### Install

Requirements:

- Python `>=3.12`
- `pip` or `uv`
- API keys only for providers that require them

```bash
git clone https://github.com/borek707/scalac_ai_council.git
cd scalac_ai_council
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Equivalent with `uv`:

```bash
uv pip install -e ".[dev]"
```

Check the CLI:

```bash
council --help
python -m council --help
```

Running `council` or `python -m council` with no flags opens the interactive terminal menu.

### Run A Demo With No API Keys

Demo mode uses built-in scenarios and scripted provider responses. It is useful for onboarding, screenshots, smoke tests, and presentations.

```bash
council --demo --scenario saas-launch --rounds 2
council --demo --scenario fintech-scale --rounds 2 --dashboard
```

Available scenarios are `saas-launch`, `ecommerce-rebrand`, `fintech-scale`, and `healthcare-app`.

### Run With A Built-In Template

```bash
export OPENAI_API_KEY="sk-..."
council --template saas --rounds 3
council --template consulting --dashboard
council --template scalac --rounds 3
```

List templates:

```bash
council --template
```

Current templates include `consulting`, `ecommerce`, `fintech`, `saas`, and `scalac`.

### Run With Your Own Company Config

```bash
council --config my_company.json --provider openai --rounds 3
council --config my_company.json --provider anthropic --dashboard
council --config my_company.json --provider ollama --model llama3
```

A minimal config includes company, product, competitors, target segment, and execution constraints:

```json
{
  "name": "Acme Corp",
  "product": "API-first payment platform for SaaS",
  "pricing_tier": "$5K-$50K ACV",
  "value_proposition": "Reduce payment integration time from 3 months to 2 weeks",
  "competitors": [{"name": "Stripe", "threat": "HIGH", "pricing": "2.9% + $0.30"}],
  "target": {
    "segment": "SaaS companies processing >$1M/year",
    "decision_maker": "CTO / VP Engineering",
    "pain_points": ["Slow integration", "High fees", "Compliance complexity"],
    "budget_range": "$50K-$200K/year"
  },
  "constraints": {"timeline_days": 90, "team_size": 3}
}
```

The schema is validated with Pydantic. See `src/council/config/schema.py` and `templates/companies/` for the current shape.

### Add Extra Context

```bash
council --config my_company.json --documents brief.md research.md
council --config my_company.json --documents-dir ./research
council --config my_company.json --brief "ABM campaign for CFOs in EU fintech"
```

## Interfaces And Review

### Interactive Menu And Dashboard

```bash
council
python -m council --interactive
python -m council --onboarding
council --template saas --dashboard
council --demo --scenario healthcare-app --dashboard
```

The interactive Textual menu is intended for first runs and exploratory use. The live dashboard shows agent cards, state, progress, logs, timeline information, and artifact previews while the council is running.

The terminal UI uses ASCII-style status labels such as `[PENDING]`, `[WRITING]`, `[DONE]`, `[AGENT]`, `[ROUND]`, and `[PROPOSAL]`. Avoiding emoji keeps output stable across terminals, CI logs, and environments with inconsistent glyph support.

### Browse Artifacts After A Run

```bash
council browse ./output
council browse ./results
python -m council browse ./output
```

`council browse <workspace>` opens a read-only Textual artifact browser for a previous run. It discovers artifacts manifest-first from `output/manifest.json`, then falls back to scanning known paths when the manifest is missing or incomplete.

The browser groups artifacts into Proposal, Agent Outputs, Discussion, Manifest, Trace, Review, and Inputs. It previews Markdown in the terminal and shows metadata such as artifact type, agent, round number, file size, modified timestamp, and summary hints.

Use the legacy Rich review output instead of the Textual browser:

```bash
council browse ./output --rich
```

### Review Artifacts

```bash
council --review ./output
council --template saas --review
council --template saas --review --review-ai
```

`--review DIR` reviews an existing workspace. `--review` without a value runs a review after a successful council run. `--review-ai` runs LLM-assisted quality review and writes:

- `output/artifacts/reviews/review.md`
- `output/artifacts/reviews/review.json`

When `output/manifest.json` exists, review metadata is added to the manifest.

### Monitor And Stream

```bash
council --monitor --output ./output
council --template saas --stream
```

`--monitor` prints status for an existing workspace without starting agents. `--stream` prints agent output chunks to the console as supported providers generate content.

## Providers

Council supports several LLM providers through the CLI. The authoritative list is in `src/council/llm/factory.py` and `src/council/cli.py`.

| Provider | CLI value | Default model / behavior | Credentials |
| --- | --- | --- | --- |
| OpenAI | `openai` | `gpt-4o` | `OPENAI_API_KEY` or `--api-key` |
| Anthropic Claude | `anthropic` | `claude-sonnet-4-6` | `ANTHROPIC_API_KEY` or `--api-key` |
| OpenRouter | `openrouter` | free-tier routing by default unless disabled | `OPENROUTER_API_KEY` or `--api-key` |
| Ollama | `ollama` | `llama3` | local Ollama server |
| Kimi Code | `kimi-code` | `kimi-for-coding` | Kimi Code CLI/session or local credentials |
| Claude Code | `claude-code` | `claude-sonnet-4-6` | Claude CLI/session or local credentials |
| LiteLLM | `litellm` | `openai/gpt-4o` | upstream provider credentials |

Examples:

```bash
export OPENAI_API_KEY="sk-..."
council --template saas --provider openai --model gpt-4o

export ANTHROPIC_API_KEY="sk-ant-..."
council --template consulting --provider anthropic

export OPENROUTER_API_KEY="sk-or-..."
council --template fintech --provider openrouter
council --template fintech --provider openrouter --no-free-tier --model anthropic/claude-sonnet-4

council --template ecommerce --provider ollama --model llama3
council --template saas --provider kimi-code
council --template saas --provider claude-code
council --config my_company.json --provider litellm --model openai/gpt-4o \
  --litellm-fallback anthropic/claude-sonnet-4-6
```

The CLI loads a local `.env` file from the current working directory before running, so provider keys can live there during local development.

## Platform Support

Council has a platform adapter layer for different AI IDE and hosted coding environments. The CLI auto-detects common environment variables and also accepts an explicit `--platform` value.

| Platform | CLI value | Notes |
| --- | --- | --- |
| Local CLI | `cli` | Default local terminal execution |
| Kimi Code | `kimi` | Kimi Code sessions |
| Google IDX | `idx` | Google IDX / Project IDX |
| Cursor | `cursor` | Cursor environments |
| GitHub Copilot / Codespaces | `copilot` | Copilot and Codespaces-style environments |
| Web platforms | `web` | Bolt, Lovable, Replit-style environments |

```bash
council --config firm.json --platform cli
council --config firm.json --platform cursor
council --config firm.json --platform kimi --provider kimi-code
```

Provider and platform are separate choices. For example, `--provider anthropic --platform cursor` means "call Anthropic as the LLM provider while running from a Cursor-oriented environment."

## Output Layout

`--output` points to the workspace root for a run. The default is `./output`.

With the default workspace, final files are written under `./output/output/` because the first `output` is the workspace and the second `output` is the artifact subdirectory inside that workspace.

```text
<workspace>/
  config.json
  shared/
    .run_started_at
    brief.md
    discussion/
      marcus_round_1.md
      elena_round_1.md
      kai_round_1.md
      david_round_1.md
      ...
  output/
    agents/
      marcus_offer.md
      elena_funnel.md
      kai_copy.md
      david_abm.md
    artifacts/
      reviews/
        review.md
        review.json
    manifest.json
    proposal.md
    trace.json
```

Important files:

| Path | Meaning |
| --- | --- |
| `config.json` | Runtime copy of the company configuration used for the run |
| `shared/brief.md` | Inline brief saved from `--brief`, when provided |
| `shared/.run_started_at` | Timestamp marker used to ignore stale discussion files |
| `shared/discussion/*_round_*.md` | Round-by-round agent discussion files |
| `output/agents/*.md` | Final agent deliverables |
| `output/proposal.md` | Aggregated proposal assembled from round outputs |
| `output/manifest.json` | Structured manifest of generated artifacts and metadata |
| `output/trace.json` | Timed spans for agent rounds and final-generation phases |
| `output/artifacts/reviews/*` | AI-assisted review outputs |

## Artifact Discovery

Artifact discovery is manifest-first. If `output/manifest.json` exists and parses correctly, Council uses it as the source of truth for proposal, final deliverables, round outputs, and review files.

If the manifest is missing or invalid, Council falls back to scanning known locations such as `output/proposal.md`, `output/agents/*.md`, legacy `FINAL_PROPOSAL.md`, `shared/discussion/*_round_*.md`, trace files, review files, `config.json`, and `shared/brief.md`. This makes post-run review useful even for interrupted or older workspaces.

## CLI Reference

Common commands:

```bash
council
council --help
python -m council --help
council --demo --scenario healthcare-app --rounds 2
council --template saas --rounds 3 --dashboard
council --config my_company.json --provider openai --model gpt-4o-mini
council --config my_company.json --provider openrouter --free-tier
council --config my_company.json --provider litellm --model openai/gpt-4o
council --config my_company.json --rounds 5 --timeout 600
council --config my_company.json --output ./results --force
council browse ./results
council --review ./results
council --monitor --output ./results
```

Run `council --help` and `council browse --help` for the authoritative option list. `--aggregate` is still accepted for compatibility, but artifacts are written automatically.

## Changelog / What Changed

### Current v3.3 Capabilities

- Universal company configuration through JSON templates and Pydantic validation.
- Four real LLM-backed agents with separate roles, prompts, and final deliverables.
- Parallel round execution with `asyncio.gather`, state transitions, timeouts, and failure reporting.
- Round-by-round filesystem discussion logs under `shared/discussion/`.
- Automatic final artifacts: agent deliverables, aggregated proposal, manifest, and trace.
- Zero-key demo mode with four built-in scenarios.
- Interactive Textual menu for guided usage.
- Live Textual dashboard with agent panels, progress, logs, preview, timeline, and artifact handoff.
- Post-run Textual artifact browser via `council browse <workspace>`.
- Manifest-first artifact discovery with filesystem fallback for interrupted or legacy workspaces.
- AI-assisted artifact review that writes Markdown and JSON review files.
- Observability traces in `output/trace.json`, with optional OpenTelemetry export support in code.
- Provider routing across OpenAI, Anthropic, Ollama, OpenRouter, Kimi Code, Claude Code, and LiteLLM.
- LiteLLM fallback chains via repeatable `--litellm-fallback`.
- Platform adapter layer for local CLI, Kimi, Google IDX, Cursor, Copilot/Codespaces, and web IDE-style environments.

### Version History

| Version | Theme | Summary |
| --- | --- | --- |
| v3.3 | Product UX and artifact review | Demo mode, interactive TUI, live dashboard, artifact discovery, browser/review flows, document context, OpenRouter, Claude Code, LiteLLM, structured manifests, and traces |
| v3.1 | Kimi Code provider | Kimi Code CLI provider, subprocess execution, credential detection, retry behavior, and tests |
| v3.0 | Universal Council | Removed hardcoded Scalac behavior; added JSON configs, real LLM providers, async orchestration, state machine, retry/timeouts, and reusable abstractions |
| v2 | Multi-agent prototype | Four named agents and filesystem communication, still largely manual and template-driven |
| v1 | Prototype | Single-agent prompt experiment |

## Project Structure

```text
scalac_ai_council/
  pyproject.toml
  README.md
  src/council/
    __main__.py              # python -m council
    cli.py                   # argparse CLI and browse subcommand
    service.py               # run orchestration service layer
    demo.py                  # zero-key demo scenarios/provider
    interactive.py           # Textual interactive menu
    review.py                # AI-assisted artifact review
    artifacts.py             # manifest-first artifact discovery
    agents/                  # Marcus, Elena, Kai, David and templates
    config/                  # schema, loader, document context, env loading
    llm/                     # provider factory and provider implementations
    orchestration/           # async orchestrator, state machine, barrier
    observability/           # trace spans and trace.json support
    platform/                # CLI/Kimi/IDX/Cursor/Copilot/Web adapters
    vis/                     # dashboard and artifact browser
  templates/companies/       # built-in company configs
  tests/                     # tests plus opt-in live provider tests
```

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

The project also supports `uv`:

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
