import pytest
import settings
from db_connect import DBConnect


@pytest.fixture(scope="session")
def db_cursor():
    with DBConnect(settings.CARD_DB) as conn:
        cur = conn.cursor()
        yield cur
