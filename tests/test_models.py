from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from job_search_ai.models import Job

FETCHED_AT = datetime(2026, 10, 18, 12, 0, tzinfo=UTC)

# Shaped like what the collectors (#4, #5) will build from each API.
GREENHOUSE_JOB = {
    "id": "greenhouse:4012345",
    "source": "greenhouse",
    "company": "Example Corp",
    "title": "Site Reliability Engineer",
    "description": "You will run our Kubernetes platform.",
    "url": "https://boards.greenhouse.io/examplecorp/jobs/4012345",
    "fetched_at": FETCHED_AT,
    "location": "Remote - Brazil",
    "posted_at": "2026-10-01T09:30:00-04:00",
}

LEVER_JOB = {
    "id": "lever:5ac21346-8e0c-4494-8e7a-3eb92ff77902",
    "source": "lever",
    "company": "Example Co",
    "title": "Platform Engineer",
    "description": "Own our CI/CD and Terraform modules.",
    "url": "https://jobs.lever.co/exampleco/5ac21346-8e0c-4494-8e7a-3eb92ff77902",
    "fetched_at": FETCHED_AT,
    "location": "São Paulo",
    "remote": False,
    "posted_at": datetime(2026, 9, 28, 14, 0, tzinfo=UTC),
}

REQUIRED_FIELDS = ("id", "source", "company", "title", "description", "url", "fetched_at")
OPTIONAL_FIELDS = ("location", "remote", "posted_at")


@pytest.mark.parametrize("sample", [GREENHOUSE_JOB, LEVER_JOB], ids=["greenhouse", "lever"])
def test_validates_a_sample_posting_from_each_source(sample):
    job = Job.model_validate(sample)

    assert job.source == sample["source"]
    assert job.title == sample["title"]
    assert str(job.url) == sample["url"]
    assert job.posted_at is not None


def test_parses_iso_timestamps_keeping_the_timezone():
    job = Job.model_validate(GREENHOUSE_JOB)

    assert job.posted_at == datetime(2026, 10, 1, 13, 30, tzinfo=UTC)


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_required_field_missing_is_rejected(field):
    data = {k: v for k, v in GREENHOUSE_JOB.items() if k != field}

    with pytest.raises(ValidationError) as exc_info:
        Job.model_validate(data)

    assert exc_info.value.errors()[0]["loc"] == (field,)


def test_optional_fields_default_to_none():
    data = {k: v for k, v in GREENHOUSE_JOB.items() if k not in OPTIONAL_FIELDS}

    job = Job.model_validate(data)

    for field in OPTIONAL_FIELDS:
        assert getattr(job, field) is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source", "linkedin"),
        ("title", "   "),
        ("url", "not a url"),
        ("fetched_at", datetime(2026, 10, 18, 12, 0)),  # no timezone
        ("salary", "100k"),  # unknown field
    ],
)
def test_invalid_value_is_rejected(field, value):
    data = {**GREENHOUSE_JOB, field: value}

    with pytest.raises(ValidationError) as exc_info:
        Job.model_validate(data)

    assert exc_info.value.errors()[0]["loc"] == (field,)


def test_strips_surrounding_whitespace():
    job = Job.model_validate({**GREENHOUSE_JOB, "title": "  SRE \n"})

    assert job.title == "SRE"
