"""
Base Endpoint Class.

This module provides the base class for all API endpoint implementations,
with common functionality for fetching and parsing data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar

from pydantic import ValidationError

from openf1_client.errors import OpenF1ValidationError
from openf1_client.models import OpenF1BaseModel
from openf1_client.utils import FilterValue, parse_csv_response


if TYPE_CHECKING:
    from openf1_client.http_client import OpenF1Transport


T = TypeVar("T", bound=OpenF1BaseModel)


class BaseEndpoint(Generic[T]):
    """
    Base class for all OpenF1 API endpoints.

    Provides common functionality for fetching data, parsing responses,
    and converting to Pydantic models.

    Type Parameters:
        T: The Pydantic model type for this endpoint's data.

    Attributes:
        _transport: The transport layer for making HTTP requests.
        _endpoint: The API endpoint path (e.g., "laps", "car_data").
        _model_class: The Pydantic model class for response data.
    """

    _endpoint: str = ""
    _model_class: type[T]

    def __init__(self, transport: "OpenF1Transport") -> None:
        """
        Initialize the endpoint.

        Args:
            transport: The transport layer for making HTTP requests.
        """
        self._transport = transport

    def _build_filters(self, **kwargs: FilterValue | None) -> dict[str, FilterValue]:
        """
        Build filter dictionary from keyword arguments.

        Removes None values from the filter dictionary.

        Args:
            **kwargs: Filter parameters.

        Returns:
            A dictionary of non-None filter values.
        """
        return {k: v for k, v in kwargs.items() if v is not None}

    def _fetch_list(self, **filters: FilterValue | None) -> list[T]:
        """
        Internal method to fetch a list of records from the endpoint.

        Args:
            **filters: Filter parameters to apply.

        Returns:
            A list of model instances.

        Raises:
            OpenF1ValidationError: If response data fails validation.
            OpenF1APIError: If the API returns an error.
        """
        clean_filters = self._build_filters(**filters)
        data = self._transport.fetch_json(self._endpoint, clean_filters)
        return self._parse_response(data)

    def list(self, **filters: FilterValue | None) -> list[T]:
        """
        Fetch a list of records from the endpoint.

        Args:
            **filters: Filter parameters to apply.

        Returns:
            A list of model instances.

        Raises:
            OpenF1ValidationError: If response data fails validation.
            OpenF1APIError: If the API returns an error.
        """
        return self._fetch_list(**filters)

    def list_raw(
        self,
        format: Literal["json", "csv"] | None = None,
        **filters: FilterValue | None,
    ) -> list[dict[str, Any]] | str:
        """
        Fetch raw data from the endpoint without model parsing.

        Args:
            format: Response format ("json" or "csv").
            **filters: Filter parameters to apply.

        Returns:
            For JSON: A list of dictionaries.
            For CSV: The raw CSV string.
        """
        clean_filters = self._build_filters(**filters)
        return self._transport.fetch(self._endpoint, clean_filters, format=format)

    def list_csv(self, **filters: FilterValue | None) -> str:
        """
        Fetch data in CSV format.

        Args:
            **filters: Filter parameters to apply.

        Returns:
            The raw CSV string.
        """
        clean_filters = self._build_filters(**filters)
        return self._transport.fetch_csv(self._endpoint, clean_filters)

    def list_csv_parsed(
        self,
        **filters: FilterValue | None,
    ) -> list[dict[str, Any]]:
        """
        Fetch CSV data and parse it into dictionaries.

        Args:
            **filters: Filter parameters to apply.

        Returns:
            A list of dictionaries parsed from CSV.
        """
        csv_text = self.list_csv(**filters)
        return parse_csv_response(csv_text)

    def first(self, **filters: FilterValue | None) -> T | None:
        """
        Fetch the first matching record.

        Args:
            **filters: Filter parameters to apply.

        Returns:
            The first matching model instance, or None if no matches.
        """
        results = self.list(**filters)
        return results[0] if results else None

    def count(self, **filters: FilterValue | None) -> int:
        """
        Count matching records.

        Note: This fetches all records and counts them locally.
        The OpenF1 API doesn't provide a dedicated count endpoint.

        Args:
            **filters: Filter parameters to apply.

        Returns:
            The number of matching records.
        """
        clean_filters = self._build_filters(**filters)
        data = self._transport.fetch_json(self._endpoint, clean_filters)
        return len(data)

    def _parse_response(self, data: list[dict[str, Any]]) -> list[T]:
        """
        Parse raw response data into model instances.

        Args:
            data: List of dictionaries from the API response.

        Returns:
            List of validated model instances.

        Raises:
            OpenF1ValidationError: If validation fails.
        """
        results: list[T] = []
        for item in data:
            try:
                results.append(self._model_class.model_validate(item))
            except ValidationError as e:
                raise OpenF1ValidationError(
                    message=f"Failed to validate {self._model_class.__name__}",
                    field=str(e.errors()[0]["loc"]) if e.errors() else None,
                    value=item,
                ) from e
        return results

    def _parse_single(self, data: dict[str, Any]) -> T:
        """
        Parse a single response item into a model instance.

        Args:
            data: Dictionary from the API response.

        Returns:
            A validated model instance.

        Raises:
            OpenF1ValidationError: If validation fails.
        """
        try:
            return self._model_class.model_validate(data)
        except ValidationError as e:
            raise OpenF1ValidationError(
                message=f"Failed to validate {self._model_class.__name__}",
                field=str(e.errors()[0]["loc"]) if e.errors() else None,
                value=data,
            ) from e
