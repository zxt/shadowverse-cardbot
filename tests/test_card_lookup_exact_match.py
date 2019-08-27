from card_lookup import process_exact_match


def test_exact_match_found(db_cursor):
    test_inputs = ["Goblin",
                   "cerberus",
                   "Puppet",
                   "Ceres of the Night",
                   "Ta-G, Katana Unsheathed",
                   "Marionette//Tre"
                   ]
    for i in test_inputs:
        assert process_exact_match(i, db_cursor) is not None


def test_exact_match_not_found(db_cursor):
    test_inputs = ["wisp",
                   "Hades",
                   "elanas prayer",
                   " ",
                   ""
                   ]
    for i in test_inputs:
        assert process_exact_match(i, db_cursor) is None
