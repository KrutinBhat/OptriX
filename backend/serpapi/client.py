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
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = 20.0,
    ) -> None:
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        self.timeout = timeout

    def search(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute one SerpApi request and return its JSON response."""

        # Check API key
        if not self.api_key:
            raise SerpApiError(
                "SERPAPI_API_KEY is not configured. "
                "Add it to your environment or .env file."
            )

        # Add common SerpApi parameters
        request_params = {
            **params,
            "api_key": self.api_key,
            "output": "json",
        }

        try:
            # Send request
            response = requests.get(
                SERPAPI_URL,
                params=request_params,
                timeout=self.timeout,
            )

            # Raise an exception for HTTP errors such as 400, 401, 429, etc.
            response.raise_for_status()

        except requests.HTTPError as exc:
            # Try to extract the actual SerpApi error message
            error_message = response.text

            try:
                error_data = response.json()

                if isinstance(error_data, dict):
                    error_message = error_data.get(
                        "error",
                        error_message,
                    )

            except ValueError:
                # Response wasn't valid JSON
                pass

            raise SerpApiError(
                f"SerpApi HTTP {response.status_code}: {error_message}"
            ) from exc

        except requests.Timeout as exc:
            raise SerpApiError(
                "SerpApi request timed out."
            ) from exc

        except requests.RequestException as exc:
            raise SerpApiError(
                f"Unable to reach SerpApi: {exc}"
            ) from exc

        # Parse JSON response
        try:
            payload = response.json()

        except ValueError as exc:
            raise SerpApiError(
                "SerpApi returned an invalid JSON response."
            ) from exc

        # Validate response format
        if not isinstance(payload, dict):
            raise SerpApiError(
                "SerpApi returned an invalid response format."
            )

        # SerpApi can return an error inside a successful HTTP response
        if payload.get("error"):
            raise SerpApiError(
                f"SerpApi error: {payload['error']}"
            )

        return payload