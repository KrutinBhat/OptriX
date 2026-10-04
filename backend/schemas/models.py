"""Pydantic schemas shared by API routes."""

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=1, examples=["Drone Components"])
    location: str = Field(min_length=1, examples=["India"])


class ResearchStats(BaseModel):
    total_queries: int
    total_results: int
