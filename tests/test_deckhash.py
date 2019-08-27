from decklist import process_deckhash
import svportal.deckcode as svp


def test_invalid_deckhash(caplog):
    hsh = "1.8.6gexy.6Z0fy.6Z0fy.6cqoo.6cqoo.6Y-DY.6Y-DY.6Y-DY.6cp5Q." + \
          "6cp5Q.6cp5Q.6coMi.6coMi.6coMi.6YxnI.6YxnI.6YxnI.6clwI.6clwI." + \
          "6clwI.6clwS.6clwS.6clwS.6V5CM.6V5CM.6V5CM.6cjUC.6cjUC.6cjUC." + \
          "6cjUM.6cjUM.6cjUM.60dFA.60dFA.60dFA.60a4M.60a4M.60a4M.60a4C. 60a4C"
    process_deckhash(hsh)
    assert "invalid" in caplog.text


def test_valid_deckhash(caplog):
    code = "pd0202"
    hsh = svp.get_hash(code)
    process_deckhash(hsh)
    assert "invalid" not in caplog.text
