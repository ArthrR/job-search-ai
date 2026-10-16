# job-search-ai

AI agent that triages job postings: collect from public job-board APIs → normalize/dedup →
rule-based prefilter → LLM scoring against the user's profile → daily Telegram review queue.
It **never submits applications**: that is a product decision, not a missing feature.

README.md has the architecture diagram, stack, planned layout and roadmap.

## Commands

```bash
uv sync                      # install deps (creates .venv)
uv run pytest                # tests
uv run ruff check .          # lint
uv run ruff format .         # format
uv run job-search-ai --help  # CLI
```

CI (`.github/workflows/ci.yml`) runs `uv sync --locked`, `ruff check`, `ruff format --check`
and `pytest`. Run all four locally before pushing; never push red.

Add dependencies with `uv add <pkg>` (dev: `uv add --dev <pkg>`) and commit `uv.lock`.

## Environment

- Developer works on **Windows (PowerShell) in VS Code**; CI runs on Ubuntu. Code must be
  cross-platform: use `pathlib`, no shell-specific commands inside Python.
- Python 3.12 (`.python-version`), managed by uv.
- GitHub repo: `ArthrR/job-search-ai`.

## Workflow

- Work is tracked as GitHub issues, grouped in milestones `v0.1 - MVP` … `v0.4 - Operations`
  and labeled `stage:0-setup` … `stage:4-review`. Each issue has a "Done when" checklist:
  that checklist is the acceptance criteria.
- One issue per branch, named `<issue-number>-short-slug` (e.g. `2-job-model`).
- PR description includes `Closes #<n>`. Keep PRs small; each one leaves CI green.
- Commit messages follow Conventional Commits: `feat:`, `fix:`, `test:`, `docs:`, `chore:`.

## Conventions

- Source lives in `src/job_search_ai/`; tests in `tests/`.
- Pydantic v2 models for every piece of data crossing a boundary: API responses, LLM output,
  config files.
- **Tests never hit the network.** Use recorded responses in `tests/fixtures/` with
  `httpx.MockTransport`. LLM calls in tests go through a fake client.
- All LLM calls go through `scoring/llm_client.py`, never a provider SDK directly.
- A CLI stage that isn't built yet exits with code 1. Never fake success.
- Secrets come only from `.env`. Never commit `.env`, `config/profile.yaml`,
  `config/sources.yaml` or database files (all gitignored).

## Design principles — do not violate

- No automatic application submission, ever.
- Recall over precision: when the model is unsure, the verdict is `maybe`, and `maybe`
  still reaches the review queue.
- Only use sources whose terms allow it (public Greenhouse/Lever APIs, email alerts).
  No scraping LinkedIn or other sites that forbid it.
- CV tailoring (v0.3) may reorder and re-emphasize, but never invent experience: every
  generated bullet must trace back to the master CV.
- Every LLM call is observable: model, prompt version, tokens, latency, estimated cost.
