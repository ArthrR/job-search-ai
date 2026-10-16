"""Command-line interface.

Each pipeline stage is a subcommand. Stages not built yet exit with code 1,
so a scheduled run never reports success for work it didn't do.
"""

import typer

from job_search_ai import __version__

app = typer.Typer(
    help="Find the jobs worth applying to — and leave the decision to you.",
    no_args_is_help=True,
)


def _not_implemented(stage: str) -> None:
    typer.echo(f"'{stage}' is not implemented yet. See the roadmap in README.md.", err=True)
    raise typer.Exit(code=1)


@app.command()
def collect() -> None:
    """Fetch, normalize, dedup and prefilter new postings."""
    _not_implemented("collect")


@app.command()
def score() -> None:
    """Score candidates not yet scored with the current prompt version."""
    _not_implemented("score")


@app.command()
def review() -> None:
    """Send today's queue to Telegram."""
    _not_implemented("review")


@app.command()
def run() -> None:
    """Run the full pipeline: collect -> score -> review."""
    _not_implemented("run")


@app.command("eval")
def eval_cmd() -> None:
    """Run the scorer against the eval set and write a report."""
    _not_implemented("eval")


@app.command()
def version() -> None:
    """Show the installed version."""
    typer.echo(f"job-search-ai {__version__}")


if __name__ == "__main__":
    app()
