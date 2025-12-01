"""Tests for the utilities module."""

import pytest

from openf1_client.utils import (
    FilterBuilder,
    build_query_params,
    chunk_list,
    parse_csv_response,
    sanitize_for_logging,
)


class TestBuildQueryParams:
    """Tests for build_query_params function."""

    def test_simple_equality(self) -> None:
        """Test simple equality filters."""
        result = build_query_params({
            "session_key": 9161,
            "driver_number": 63,
        })

        assert result == {
            "session_key": "9161",
            "driver_number": "63",
        }

    def test_string_values(self) -> None:
        """Test string filter values."""
        result = build_query_params({
            "meeting_key": "latest",
            "country_code": "GBR",
        })

        assert result == {
            "meeting_key": "latest",
            "country_code": "GBR",
        }

    def test_greater_than(self) -> None:
        """Test greater-than operator."""
        result = build_query_params({
            "speed": {">=": 315},
        })

        assert result == {"speed>=": "315"}

    def test_less_than(self) -> None:
        """Test less-than operator."""
        result = build_query_params({
            "interval": {"<": 0.5},
        })

        assert result == {"interval<": "0.5"}

    def test_range_filter(self) -> None:
        """Test range filter with multiple operators."""
        result = build_query_params({
            "date": {
                ">": "2023-09-16T13:00:00",
                "<": "2023-09-16T14:00:00",
            },
        })

        assert result == {
            "date>": "2023-09-16T13:00:00",
            "date<": "2023-09-16T14:00:00",
        }

    def test_equality_operator(self) -> None:
        """Test explicit equality operator."""
        result = build_query_params({
            "lap_number": {"=": 10},
        })

        assert result == {"lap_number": "10"}

    def test_mixed_filters(self) -> None:
        """Test mix of simple and operator filters."""
        result = build_query_params({
            "session_key": 9161,
            "driver_number": 55,
            "speed": {">=": 315},
        })

        assert result == {
            "session_key": "9161",
            "driver_number": "55",
            "speed>=": "315",
        }

    def test_none_values_ignored(self) -> None:
        """Test that None values are ignored."""
        result = build_query_params({
            "session_key": 9161,
            "driver_number": None,
        })

        assert result == {"session_key": "9161"}
        assert "driver_number" not in result

    def test_csv_format(self) -> None:
        """Test CSV format parameter."""
        result = build_query_params(
            {"session_key": 9161},
            format="csv",
        )

        assert result == {
            "session_key": "9161",
            "csv": "true",
        }

    def test_json_format_no_param(self) -> None:
        """Test that JSON format doesn't add parameter."""
        result = build_query_params(
            {"session_key": 9161},
            format="json",
        )

        assert "csv" not in result

    def test_empty_filters(self) -> None:
        """Test empty filter dictionary."""
        result = build_query_params({})
        assert result == {}


class TestParseCsvResponse:
    """Tests for parse_csv_response function."""

    def test_simple_csv(self) -> None:
        """Test parsing simple CSV."""
        csv_text = "name,value\nalice,1\nbob,2"
        result = parse_csv_response(csv_text)

        assert len(result) == 2
        assert result[0] == {"name": "alice", "value": "1"}
        assert result[1] == {"name": "bob", "value": "2"}

    def test_empty_csv(self) -> None:
        """Test parsing empty CSV."""
        result = parse_csv_response("")
        assert result == []

    def test_whitespace_only(self) -> None:
        """Test parsing whitespace-only CSV."""
        result = parse_csv_response("   \n  \n")
        assert result == []

    def test_headers_only(self) -> None:
        """Test parsing CSV with only headers."""
        csv_text = "name,value"
        result = parse_csv_response(csv_text)
        assert result == []


class TestChunkList:
    """Tests for chunk_list function."""

    def test_even_chunks(self) -> None:
        """Test chunking with even division."""
        result = list(chunk_list([1, 2, 3, 4], 2))
        assert result == [[1, 2], [3, 4]]

    def test_uneven_chunks(self) -> None:
        """Test chunking with uneven division."""
        result = list(chunk_list([1, 2, 3, 4, 5], 2))
        assert result == [[1, 2], [3, 4], [5]]

    def test_chunk_larger_than_list(self) -> None:
        """Test chunking when chunk size exceeds list length."""
        result = list(chunk_list([1, 2], 10))
        assert result == [[1, 2]]

    def test_empty_list(self) -> None:
        """Test chunking empty list."""
        result = list(chunk_list([], 5))
        assert result == []


class TestSanitizeForLogging:
    """Tests for sanitize_for_logging function."""

    def test_redacts_password(self) -> None:
        """Test that password is redacted."""
        data = {"username": "user", "password": "secret123"}
        result = sanitize_for_logging(data)

        assert result["username"] == "user"
        assert result["password"] == "[REDACTED]"

    def test_redacts_token(self) -> None:
        """Test that token is redacted."""
        data = {"access_token": "abc123", "data": "value"}
        result = sanitize_for_logging(data)

        assert result["access_token"] == "[REDACTED]"
        assert result["data"] == "value"

    def test_redacts_authorization(self) -> None:
        """Test that authorization is redacted."""
        data = {"Authorization": "Bearer abc123"}
        result = sanitize_for_logging(data)

        assert result["Authorization"] == "[REDACTED]"

    def test_nested_dict(self) -> None:
        """Test sanitizing nested dictionaries."""
        data = {
            "auth": {"password": "secret"},
            "info": {"name": "test"},
        }
        result = sanitize_for_logging(data)

        assert result["auth"]["password"] == "[REDACTED]"
        assert result["info"]["name"] == "test"

    def test_non_dict_passthrough(self) -> None:
        """Test that non-dict values pass through."""
        assert sanitize_for_logging("test") == "test"
        assert sanitize_for_logging(123) == 123
        assert sanitize_for_logging(None) is None


class TestFilterBuilder:
    """Tests for FilterBuilder class."""

    def test_equality(self) -> None:
        """Test equality filter."""
        f = FilterBuilder()
        filters = f.eq("session_key", 9161).build()

        assert filters == {"session_key": 9161}

    def test_greater_than(self) -> None:
        """Test greater-than filter."""
        f = FilterBuilder()
        filters = f.gt("speed", 300).build()

        assert filters == {"speed": {">": 300}}

    def test_greater_than_equal(self) -> None:
        """Test greater-than-or-equal filter."""
        f = FilterBuilder()
        filters = f.gte("speed", 300).build()

        assert filters == {"speed": {">=": 300}}

    def test_less_than(self) -> None:
        """Test less-than filter."""
        f = FilterBuilder()
        filters = f.lt("interval", 1.0).build()

        assert filters == {"interval": {"<": 1.0}}

    def test_less_than_equal(self) -> None:
        """Test less-than-or-equal filter."""
        f = FilterBuilder()
        filters = f.lte("position", 10).build()

        assert filters == {"position": {"<=": 10}}

    def test_between_exclusive(self) -> None:
        """Test exclusive range filter."""
        f = FilterBuilder()
        filters = f.between("lap_number", 5, 10, inclusive=False).build()

        assert filters == {"lap_number": {">": 5, "<": 10}}

    def test_between_inclusive(self) -> None:
        """Test inclusive range filter."""
        f = FilterBuilder()
        filters = f.between("lap_number", 5, 10, inclusive=True).build()

        assert filters == {"lap_number": {">=": 5, "<=": 10}}

    def test_chaining(self) -> None:
        """Test method chaining."""
        f = FilterBuilder()
        filters = (
            f.eq("session_key", 9161)
            .eq("driver_number", 63)
            .gte("speed", 300)
            .build()
        )

        assert filters == {
            "session_key": 9161,
            "driver_number": 63,
            "speed": {">=": 300},
        }

    def test_clear(self) -> None:
        """Test clearing filters."""
        f = FilterBuilder()
        f.eq("session_key", 9161)
        f.clear()
        filters = f.build()

        assert filters == {}

    def test_build_returns_copy(self) -> None:
        """Test that build returns a copy."""
        f = FilterBuilder()
        f.eq("session_key", 9161)
        filters1 = f.build()
        filters2 = f.build()

        assert filters1 == filters2
        assert filters1 is not filters2
