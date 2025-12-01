"""
OpenF1 Client Utilities.

This module provides utility functions for building query parameters,
filtering data, and other common operations used throughout the client.
"""

from __future__ import annotations

import csv
import io
import logging
from typing import Any, Iterator, Literal


logger = logging.getLogger("openf1_client")


# Type alias for filter operators
FilterOperator = Literal[">=", "<=", ">", "<", "="]

# Type alias for filter values
FilterValue = str | int | float | dict[FilterOperator, str | int | float]


def build_query_params(
    filters: dict[str, FilterValue],
    format: Literal["json", "csv"] | None = None,
) -> dict[str, str]:
    """
    Build URL query parameters from filter specifications.

    This function converts Python filter dictionaries into URL query parameters
    that the OpenF1 API understands, including comparison operators.

    Args:
        filters: A dictionary of filter names to values. Values can be:
            - Simple values (str, int, float): Used for equality matching
            - Dicts with operator keys: {">=": 315, "<": 320}
        format: Optional response format ("json" or "csv").

    Returns:
        A dictionary of query parameter keys to string values.

    Examples:
        >>> build_query_params({"session_key": 9161, "driver_number": 63})
        {"session_key": "9161", "driver_number": "63"}

        >>> build_query_params({"speed": {">=": 315}})
        {"speed>=": "315"}

        >>> build_query_params({"date": {">": "2023-09-16T13:00:00", "<": "2023-09-16T14:00:00"}})
        {"date>": "2023-09-16T13:00:00", "date<": "2023-09-16T14:00:00"}
    """
    params: dict[str, str] = {}

    for key, value in filters.items():
        if value is None:
            continue

        if isinstance(value, dict):
            # Handle comparison operators
            for operator, op_value in value.items():
                if operator == "=":
                    params[key] = str(op_value)
                else:
                    params[f"{key}{operator}"] = str(op_value)
        else:
            # Simple equality
            params[key] = str(value)

    # Add format parameter if specified
    if format == "csv":
        params["csv"] = "true"

    return params


def parse_csv_response(csv_text: str) -> list[dict[str, Any]]:
    """
    Parse a CSV response into a list of dictionaries.

    Args:
        csv_text: The raw CSV text from the API response.

    Returns:
        A list of dictionaries, one per row, with column headers as keys.

    Example:
        >>> csv_text = "name,value\\nalice,1\\nbob,2"
        >>> parse_csv_response(csv_text)
        [{"name": "alice", "value": "1"}, {"name": "bob", "value": "2"}]
    """
    if not csv_text.strip():
        return []

    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)


def iter_csv_response(csv_text: str) -> Iterator[dict[str, Any]]:
    """
    Iterate over a CSV response lazily.

    Args:
        csv_text: The raw CSV text from the API response.

    Yields:
        Dictionaries, one per row, with column headers as keys.
    """
    if not csv_text.strip():
        return

    reader = csv.DictReader(io.StringIO(csv_text))
    yield from reader


def chunk_list(items: list[Any], chunk_size: int) -> Iterator[list[Any]]:
    """
    Split a list into chunks of the specified size.

    Args:
        items: The list to split.
        chunk_size: Maximum size of each chunk.

    Yields:
        Lists of at most chunk_size items.

    Example:
        >>> list(chunk_list([1, 2, 3, 4, 5], 2))
        [[1, 2], [3, 4], [5]]
    """
    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


def sanitize_for_logging(value: Any) -> Any:
    """
    Sanitize a value for safe logging.

    This function redacts sensitive information like passwords and tokens
    to prevent them from appearing in logs.

    Args:
        value: The value to sanitize.

    Returns:
        The sanitized value with sensitive data redacted.
    """
    if isinstance(value, dict):
        sanitized = {}
        sensitive_keys = {
            "password",
            "token",
            "access_token",
            "refresh_token",
            "authorization",
            "secret",
            "api_key",
        }
        for k, v in value.items():
            if k.lower() in sensitive_keys:
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = sanitize_for_logging(v)
        return sanitized
    return value


def setup_logging(
    level: int = logging.DEBUG,
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> None:
    """
    Configure logging for the OpenF1 client.

    This is a convenience function for enabling debug logging during
    development or troubleshooting.

    Args:
        level: The logging level (default: DEBUG).
        format: The log message format string.

    Example:
        >>> from openf1_client.utils import setup_logging
        >>> import logging
        >>> setup_logging(logging.DEBUG)
    """
    logging.basicConfig(level=level, format=format)
    logger = logging.getLogger("openf1_client")
    logger.setLevel(level)


class FilterBuilder:
    """
    A fluent builder for constructing query filters.

    This class provides a Pythonic way to build complex filters
    with comparison operators.

    Example:
        >>> from openf1_client.utils import FilterBuilder
        >>> f = FilterBuilder()
        >>> filters = (
        ...     f.eq("session_key", 9161)
        ...     .eq("driver_number", 63)
        ...     .gte("speed", 315)
        ...     .lt("lap_number", 10)
        ...     .build()
        ... )
        >>> print(filters)
        {"session_key": 9161, "driver_number": 63, "speed": {">=": 315}, "lap_number": {"<": 10}}
    """

    def __init__(self) -> None:
        """Initialize an empty filter builder."""
        self._filters: dict[str, FilterValue] = {}

    def eq(self, field: str, value: str | int | float) -> "FilterBuilder":
        """
        Add an equality filter.

        Args:
            field: The field name to filter on.
            value: The value to match.

        Returns:
            Self for method chaining.
        """
        self._filters[field] = value
        return self

    def gt(self, field: str, value: str | int | float) -> "FilterBuilder":
        """
        Add a greater-than filter.

        Args:
            field: The field name to filter on.
            value: The threshold value.

        Returns:
            Self for method chaining.
        """
        if field not in self._filters or not isinstance(self._filters[field], dict):
            self._filters[field] = {}
        if isinstance(self._filters[field], dict):
            self._filters[field][">"] = value  # type: ignore
        return self

    def gte(self, field: str, value: str | int | float) -> "FilterBuilder":
        """
        Add a greater-than-or-equal filter.

        Args:
            field: The field name to filter on.
            value: The threshold value.

        Returns:
            Self for method chaining.
        """
        if field not in self._filters or not isinstance(self._filters[field], dict):
            self._filters[field] = {}
        if isinstance(self._filters[field], dict):
            self._filters[field][">="] = value  # type: ignore
        return self

    def lt(self, field: str, value: str | int | float) -> "FilterBuilder":
        """
        Add a less-than filter.

        Args:
            field: The field name to filter on.
            value: The threshold value.

        Returns:
            Self for method chaining.
        """
        if field not in self._filters or not isinstance(self._filters[field], dict):
            self._filters[field] = {}
        if isinstance(self._filters[field], dict):
            self._filters[field]["<"] = value  # type: ignore
        return self

    def lte(self, field: str, value: str | int | float) -> "FilterBuilder":
        """
        Add a less-than-or-equal filter.

        Args:
            field: The field name to filter on.
            value: The threshold value.

        Returns:
            Self for method chaining.
        """
        if field not in self._filters or not isinstance(self._filters[field], dict):
            self._filters[field] = {}
        if isinstance(self._filters[field], dict):
            self._filters[field]["<="] = value  # type: ignore
        return self

    def between(
        self,
        field: str,
        lower: str | int | float,
        upper: str | int | float,
        inclusive: bool = False,
    ) -> "FilterBuilder":
        """
        Add a range filter.

        Args:
            field: The field name to filter on.
            lower: The lower bound.
            upper: The upper bound.
            inclusive: If True, uses >= and <=; otherwise uses > and <.

        Returns:
            Self for method chaining.
        """
        if inclusive:
            self._filters[field] = {">=": lower, "<=": upper}
        else:
            self._filters[field] = {">": lower, "<": upper}
        return self

    def build(self) -> dict[str, FilterValue]:
        """
        Build and return the filter dictionary.

        Returns:
            The constructed filter dictionary.
        """
        return self._filters.copy()

    def clear(self) -> "FilterBuilder":
        """
        Clear all filters.

        Returns:
            Self for method chaining.
        """
        self._filters.clear()
        return self
