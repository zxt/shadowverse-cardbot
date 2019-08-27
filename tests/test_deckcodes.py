from decklist import process_deckcodes


def test_invalid_deckcodes(caplog):
    process_deckcodes(["abcd"])
    assert "invalid" in caplog.text


def test_valid_deckcodes(caplog):
    process_deckcodes(["pd0102"])
    process_deckcodes(["pd0204"])
    process_deckcodes(["pd0303"])
    process_deckcodes(["pd0405"])
    process_deckcodes(["pd0504"])
    process_deckcodes(["pd0601"])
    process_deckcodes(["pd0702"])
    process_deckcodes(["pd0805"])
    assert "invalid" not in caplog.text
