import pytest

import svportal.enums as sv
from card_lookup import lookup_name_from_id


@pytest.mark.parametrize("test_input,expected", sv.CRAFTS)
def test_craft_id2name_lookup(db_cursor, test_input, expected):
    assert lookup_name_from_id(test_input, "crafts", db_cursor) == expected


@pytest.mark.parametrize("test_input,expected", sv.CARD_TYPES)
def test_cardtype_id2name_lookup(db_cursor, test_input, expected):
    assert lookup_name_from_id(test_input, "card_types", db_cursor) == expected


@pytest.mark.parametrize("test_input,expected", sv.CARD_RARITYS)
def test_rarity_id2name_lookup(db_cursor, test_input, expected):
    assert lookup_name_from_id(test_input, "card_rarity", db_cursor) == expected


@pytest.mark.parametrize("test_input,expected", sv.CARD_SETS)
def test_set_id2name_lookup(db_cursor, test_input, expected):
    assert lookup_name_from_id(test_input, "card_sets", db_cursor) == expected
