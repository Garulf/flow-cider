import pytest

from parse_args import QueryError, parse_args
from test_plugin import results


def test_options_are_parsed_between_words():
    args, _ = parse_args("midnight :limit 5 city")
    assert args.query == ["midnight", "city"]
    assert args.limit == 5


@pytest.mark.parametrize("query", ["midnight :foo", "midnight :limit many"])
def test_bad_options_raise_instead_of_exiting(query):
    with pytest.raises(QueryError):
        parse_args(query)


def test_bad_option_is_shown_as_a_result(server):
    (result,) = results("query", "midnight :foo")
    assert result["Title"] == "Invalid search"
    assert ":foo" in result["SubTitle"]
    assert server.sent == []
