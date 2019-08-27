from card_lookup import process_card_id_match


def test_card_id_found(db_cursor):
    test_inputs = ["100011010",
                   "709822010",
                   "705614020"
                   ]
    for i in test_inputs:
        assert process_card_id_match(i, db_cursor) is not None


def test_card_id_not_found(db_cursor):
    test_inputs = ["1",
                   "abcd",
                   "9001",
                   "100000000",
                   "999999999",
                   "12345678O",
                   "11111111111111111111111111111111111111111111111111111111",
                   " "
                   "1 2 3 4"
                   "709 822 010",
                   "709,822,010",
                   ]
    for i in test_inputs:
        assert process_card_id_match(i, db_cursor) is None
