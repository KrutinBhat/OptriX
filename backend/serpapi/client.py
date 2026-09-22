"""Small, reusable HTTP client for SerpApi requests."""

import os
from typing import Any, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_URL = "https://serpapi.com/search.json"


class SerpApiError(Exception):
    """A recoverable error returned by a SerpApi collection request."""


class SerpApiClient:
    def __init__(self, api_key: Optional[str] = None, timeout: float = 20.0) -> None:
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        self.timeout = timeout

    def search(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute one SerpApi request and return its JSON response."""
        if not self.api_key:
            raise SerpApiError(
                "SERPAPI_API_KEY is not configured. Add it to your environment or .env file."
            )

        request_params = {**params, "api_key": self.api_key, "output": "json"}
        try:
            response = requests.get(SERPAPI_URL, params=request_params, timeout=self.timeout)
            response.raise_for_status()
        except requests.Timeout as exc:
            raise SerpApiError("SerpApi request timed out") from exc
        except requests.RequestException as exc:
            raise SerpApiError("Unable to reach SerpApi") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise SerpApiError("SerpApi returned an invalid JSON response") from exc

        if not isinstance(payload, dict):
            raise SerpApiError("SerpApi returned an invalid response format")
        if payload.get("error"):
            raise SerpApiError(f"SerpApi error: {payload['error']}")
        return payload
