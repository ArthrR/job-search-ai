import logging
from datetime import UTC, datetime

import pytest

from job_search_ai.collectors.base import Collector, collect_all
from job_search_ai.models import Job


def make_job(job_id: str) -> Job:
    return Job(
        id=job_id,
        source="greenhouse",
        company="Example Corp",
        title="Site Reliability Engineer",
        description="Run our Kubernetes platform.",
        url=f"https://boards.greenhouse.io/examplecorp/jobs/{job_id.split(':')[1]}",
        fetched_at=datetime(2026, 10, 18, 12, 0, tzinfo=UTC),
    )


class FakeCollector(Collector):
    def __init__(self, name: str, jobs: list[Job]):
        self._name = name
        self._jobs = jobs

    @property
    def name(self) -> str:
        return self._name

    def fetch(self) -> list[Job]:
        return self._jobs


class BrokenCollector(Collector):
    @property
    def name(self) -> str:
        return "broken"

    def fetch(self) -> list[Job]:
        raise ConnectionError("board unreachable")


def test_one_failing_collector_does_not_break_the_run(caplog):
    first = FakeCollector("first", [make_job("greenhouse:1")])
    last = FakeCollector("last", [make_job("greenhouse:2"), make_job("greenhouse:3")])

    with caplog.at_level(logging.ERROR):
        result = collect_all([first, BrokenCollector(), last])

    assert [job.id for job in result.jobs] == ["greenhouse:1", "greenhouse:2", "greenhouse:3"]
    assert result.failed == ["broken"]
    assert "broken" in caplog.text
    assert "board unreachable" in caplog.text


def test_all_collectors_succeeding_reports_no_failures():
    result = collect_all([FakeCollector("only", [make_job("greenhouse:1")])])

    assert len(result.jobs) == 1
    assert result.failed == []


def test_no_collectors_returns_an_empty_result():
    result = collect_all([])

    assert result.jobs == []
    assert result.failed == []


def test_collector_without_fetch_cannot_be_created():
    class Incomplete(Collector):
        @property
        def name(self) -> str:
            return "incomplete"

    with pytest.raises(TypeError, match="fetch"):
        Incomplete()
