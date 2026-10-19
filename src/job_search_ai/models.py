"""Data models shared by every pipeline stage.

Collectors map each source's API response to a `Job`; every later stage
(dedup, prefilter, scoring, storage) only ever sees `Job`.
"""

from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, HttpUrl

Source = Literal["greenhouse", "lever"]


class Job(BaseModel):
    """One job posting, normalized to the same shape whatever its source."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(min_length=1, description="Unique across sources, e.g. 'greenhouse:4012345'.")
    source: Source
    company: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(description="Plain text, already stripped of HTML.")
    url: HttpUrl
    fetched_at: AwareDatetime

    location: str | None = None
    remote: bool | None = Field(default=None, description="None means unknown, not 'on-site'.")
    posted_at: AwareDatetime | None = None
