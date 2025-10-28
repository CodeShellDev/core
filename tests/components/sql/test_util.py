"""Test the sql utils."""

import pytest
import voluptuous as vol

from homeassistant.components.recorder import Recorder, get_instance
from homeassistant.components.sql.util import resolve_db_url, validate_sql_select
from homeassistant.core import HomeAssistant
from homeassistant.helpers.template import Template


async def test_resolve_db_url_when_none_configured(
    recorder_mock: Recorder,
    hass: HomeAssistant,
) -> None:
    """Test return recorder db_url if provided db_url is None."""
    db_url = None
    resolved_url = resolve_db_url(hass, db_url)

    assert resolved_url == get_instance(hass).db_url


async def test_resolve_db_url_when_configured(hass: HomeAssistant) -> None:
    """Test return provided db_url if it's set."""
    db_url = "mssql://"
    resolved_url = resolve_db_url(hass, db_url)

    assert resolved_url == db_url


@pytest.mark.parametrize(
    ("sql_query", "expected_error_message"),
    [
        (
            "DROP TABLE *",
            "SQL query must be of type SELECT",
        ),
        (
            "SELECT5 as value",
            "SQL query is empty or unknown type",
        ),
        (
            ";;",
            "SQL query is empty or unknown type",
        ),
        (
            "UPDATE states SET state = 999999 WHERE state_id = 11125",
            "SQL query must be of type SELECT",
        ),
        (
            "WITH test AS (SELECT state FROM states) UPDATE states SET states.state = test.state;",
            "SQL query must be of type SELECT",
        ),
        (
            "SELECT 5 as value; UPDATE states SET state = 10;",
            "Multiple SQL statements are not allowed",
        ),
    ],
)
async def test_invalid_sql_queries(
    hass: HomeAssistant,
    sql_query: str,
    expected_error_message: str,
) -> None:
    """Test that various invalid or disallowed SQL queries raise the correct exception."""
    with pytest.raises(vol.Invalid, match=expected_error_message):
        validate_sql_select(Template(sql_query, hass))
