"""The contract every collector follows, and the loop that runs them all.

A failing source must not stop the others: `collect_all` logs the error,
records which collector failed and moves on.
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field

from job_search_ai.models import Job

logger = logging.getLogger(__name__)


class Collector(ABC):
    """Fetches the current postings from one source, e.g. one Greenhouse board."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Identifies this collector in logs, e.g. 'greenhouse:examplecorp'."""

    @abstractmethod
    def fetch(self) -> list[Job]:
        """Return every open posting. Raise on failure; never return partial data silently."""


@dataclass
class CollectResult:
    jobs: list[Job] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)


def collect_all(collectors: Iterable[Collector]) -> CollectResult:
    """Run every collector; one that raises is logged and skipped."""
    result = CollectResult()
    for collector in collectors:
        try:
            jobs = collector.fetch()
        except Exception:
            logger.exception("Collector %s failed; skipping it", collector.name)
            result.failed.append(collector.name)
            continue
        logger.info("Collector %s fetched %d postings", collector.name, len(jobs))
        result.jobs.extend(jobs)
    return result
