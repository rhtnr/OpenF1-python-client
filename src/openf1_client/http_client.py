"""
OpenF1 HTTP Transport Layer.

This module provides the low-level HTTP client for making requests to the
OpenF1 API. It handles retries, error mapping, and response processing.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Literal

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from openf1_client.config import ClientConfig
from openf1_client.errors import (
    OpenF1TimeoutError,
    OpenF1TransportError,
    raise_for_status,
)
from openf1_client.utils import build_query_params, sanitize_for_logging


logger = logging.getLogger("openf1_client")


class HTTPClientProtocol(ABC):
    """
    Abstract base class defining the HTTP client interface.

    This protocol defines the interface that all HTTP client implementations
    must follow, enabling dependency injection and easy testing.
    """

    @abstractmethod
    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | tuple[float, float] | None = None,
    ) -> requests.Response:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: URL path relative to base URL.
            params: Query parameters.
            data: Request body data.
            headers: Additional headers.
            timeout: Optional timeout override.

        Returns:
            The HTTP response.
        """
        ...

    @abstractmethod
    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Make a GET request."""
        ...

    @abstractmethod
    def post(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """Make a POST request."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Close the HTTP client and release resources."""
        ...


class SyncHTTPClient(HTTPClientProtocol):
    """
    Synchronous HTTP client using the requests library.

    This class handles all HTTP communication with the OpenF1 API, including
    automatic retries, error handling, and request logging.

    Attributes:
        config: The client configuration.
        session: The requests session.
    """

    def __init__(self, config: ClientConfig) -> None:
        """
        Initialize the HTTP client.

        Args:
            config: The client configuration.
        """
        self.config = config
        self.session = self._create_session()
        self._base_url = config.base_url.rstrip("/")

    def _create_session(self) -> requests.Session:
        """
        Create and configure a requests session with retry logic.

        Returns:
            A configured requests session.
        """
        session = requests.Session()

        # Configure retries
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=0.5,
            status_forcelist=self.config.retry_on_status,
            allowed_methods=["GET", "POST"],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update(self.config.get_headers())

        return session

    def _build_url(self, path: str) -> str:
        """
        Build a full URL from a path.

        Args:
            path: The URL path.

        Returns:
            The full URL.
        """
        path = path.lstrip("/")
        return f"{self._base_url}/{path}"

    def _get_auth_header(self) -> dict[str, str]:
        """
        Get the authorization header if a token is available.

        Returns:
            A dictionary containing the Authorization header, or empty dict.
        """
        if self.config.access_token:
            return {"Authorization": f"Bearer {self.config.access_token}"}
        return {}

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | tuple[float, float] | None = None,
    ) -> requests.Response:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: URL path relative to base URL.
            params: Query parameters.
            data: Request body data (for POST).
            headers: Additional headers.
            timeout: Optional timeout override.

        Returns:
            The HTTP response.

        Raises:
            OpenF1TimeoutError: If the request times out.
            OpenF1TransportError: If a network error occurs.
            OpenF1APIError: If the API returns an error response.
        """
        url = self._build_url(path)
        request_timeout = timeout or self.config.get_timeout()

        # Merge headers
        request_headers = self._get_auth_header()
        if headers:
            request_headers.update(headers)

        # Log the request (without sensitive data)
        logger.debug(
            "HTTP %s %s params=%s",
            method,
            url,
            sanitize_for_logging(params),
        )

        try:
            start_time = time.monotonic()
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=request_headers,
                timeout=request_timeout,
                verify=self.config.verify_ssl,
            )
            elapsed = time.monotonic() - start_time

            # Log the response
            logger.debug(
                "HTTP %s %s -> %d (%.2fs)",
                method,
                url,
                response.status_code,
                elapsed,
            )

            # Check for errors and raise appropriate exceptions
            retry_after = response.headers.get("Retry-After")
            retry_after_int = int(retry_after) if retry_after else None

            raise_for_status(
                status_code=response.status_code,
                response_body=self._parse_response_body(response),
                request_url=url,
                retry_after=retry_after_int,
            )

            return response

        except requests.exceptions.Timeout as e:
            logger.error("Request timeout: %s", url)
            raise OpenF1TimeoutError(
                message=f"Request to {url} timed out",
                timeout=request_timeout
                if isinstance(request_timeout, float)
                else request_timeout[1],
                original_error=e,
            ) from e

        except requests.exceptions.ConnectionError as e:
            logger.error("Connection error: %s - %s", url, e)
            raise OpenF1TransportError(
                message=f"Failed to connect to {url}",
                original_error=e,
            ) from e

        except requests.exceptions.RequestException as e:
            logger.error("Request error: %s - %s", url, e)
            raise OpenF1TransportError(
                message=f"Request to {url} failed",
                original_error=e,
            ) from e

    def _parse_response_body(self, response: requests.Response) -> str | dict[str, Any]:
        """
        Parse the response body.

        Args:
            response: The HTTP response.

        Returns:
            The parsed response body (JSON dict or raw text).
        """
        try:
            return response.json()
        except ValueError:
            return response.text

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Make a GET request.

        Args:
            path: URL path relative to base URL.
            params: Query parameters.
            **kwargs: Additional arguments passed to request().

        Returns:
            The HTTP response.
        """
        return self.request("GET", path, params=params, **kwargs)

    def post(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        """
        Make a POST request.

        Args:
            path: URL path relative to base URL.
            data: Request body data.
            **kwargs: Additional arguments passed to request().

        Returns:
            The HTTP response.
        """
        return self.request("POST", path, data=data, **kwargs)

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self.session.close()

    def __enter__(self) -> "SyncHTTPClient":
        """Enter the context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit the context manager and close the session."""
        self.close()


class OpenF1Transport:
    """
    High-level transport layer for the OpenF1 API.

    This class provides convenient methods for fetching data from the API
    with automatic query parameter building and response parsing.
    """

    def __init__(self, http_client: HTTPClientProtocol, config: ClientConfig) -> None:
        """
        Initialize the transport.

        Args:
            http_client: The HTTP client to use.
            config: The client configuration.
        """
        self._http = http_client
        self._config = config

    def fetch(
        self,
        endpoint: str,
        filters: dict[str, Any] | None = None,
        format: Literal["json", "csv"] | None = None,
    ) -> list[dict[str, Any]] | str:
        """
        Fetch data from an API endpoint.

        Args:
            endpoint: The endpoint path (e.g., "laps", "car_data").
            filters: Filter parameters to apply.
            format: Response format ("json" or "csv"). Defaults to config value.

        Returns:
            For JSON format: A list of dictionaries.
            For CSV format: The raw CSV string.
        """
        effective_format = format or self._config.default_format
        params = build_query_params(filters or {}, format=effective_format)

        response = self._http.get(endpoint, params=params)

        if effective_format == "csv":
            return response.text
        return response.json()

    def fetch_json(
        self,
        endpoint: str,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch JSON data from an API endpoint.

        Args:
            endpoint: The endpoint path.
            filters: Filter parameters to apply.

        Returns:
            A list of dictionaries containing the response data.
        """
        result = self.fetch(endpoint, filters, format="json")
        if isinstance(result, str):
            return []
        return result

    def fetch_csv(
        self,
        endpoint: str,
        filters: dict[str, Any] | None = None,
    ) -> str:
        """
        Fetch CSV data from an API endpoint.

        Args:
            endpoint: The endpoint path.
            filters: Filter parameters to apply.

        Returns:
            The raw CSV string.
        """
        result = self.fetch(endpoint, filters, format="csv")
        if isinstance(result, list):
            return ""
        return result

    def post_form(
        self,
        url: str,
        data: dict[str, str],
    ) -> dict[str, Any]:
        """
        Make a POST request with form data.

        This is primarily used for OAuth2 token requests.

        Args:
            url: The full URL to post to.
            data: Form data to send.

        Returns:
            The JSON response.
        """
        # For token requests, we need to post to an absolute URL
        response = self._http.session.post(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=self._config.get_timeout(),
            verify=self._config.verify_ssl,
        )

        raise_for_status(
            status_code=response.status_code,
            response_body=response.text,
            request_url=url,
        )

        return response.json()

    def close(self) -> None:
        """Close the transport and release resources."""
        self._http.close()
