from card_lookup import process_nonexact_match


def test_nonexact_match_found_first_word(db_cursor):
    result = process_nonexact_match("kel", db_cursor)
    assert result["card_name"] == "Kel, Holy Marksman"

    result = process_nonexact_match("HADES", db_cursor)
    assert result["card_name"] == "Hades, Father of Purgatory"

    result = process_nonexact_match("Ferry", db_cursor)
    assert result["card_name"] == "Ferry, Spirit Maiden"

    result = process_nonexact_match("XXI.", db_cursor)
    assert result["card_name"] == "XXI. Zelgenea, The World"


def test_nonexact_match_found_multiword(db_cursor):
    result = process_nonexact_match("elana prayer", db_cursor)
    assert result["card_name"] == "Elana, Purest Prayer"

    result = process_nonexact_match("orchis puppet", db_cursor)
    assert result["card_name"] == "Orchis, Puppet Girl"

    result = process_nonexact_match("hades cerberus", db_cursor)
    assert result["card_name"] == "Cerberus, Hound of Hades"

    result = process_nonexact_match("vi. the lovers", db_cursor)
    assert result["card_name"] == "VI. Milteo, The Lovers"


def test_nonexact_match_found_partial_string(db_cursor):
    result = process_nonexact_match("heart", db_cursor)
    assert result is not None

    result = process_nonexact_match("ha ha", db_cursor)
    assert result is not None

    result = process_nonexact_match("prince CoC", db_cursor)
    assert result is not None

    result = process_nonexact_match("luzen", db_cursor)
    assert result is not None


def test_nonexact_match_not_found(db_cursor):
    test_inputs = ["kell",
                   "elena",
                   "abcd",
                   "foo bar",
                   "%xxx%"
                   ]
    for i in test_inputs:
        assert process_nonexact_match(i, db_cursor) is None

    assert process_nonexact_match("   ", db_cursor) == "Error"
    assert process_nonexact_match("[]", db_cursor) == "Error"
    assert process_nonexact_match("[[]]", db_cursor) == "Error"
