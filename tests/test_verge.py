import sqlite3
import pytest
import pandas as pd
from unittest.mock import patch, Mock
from verge_scraper import VergeScraper
from csv_file import CSV
from database import Database

@pytest.fixture(scope="function")
def mock_requests_get():
    with patch("requests.get") as mock_get:
        yield mock_get

@pytest.fixture(scope="function")
def database(tmpdir):
    db_filename = str(tmpdir.join("test.db"))
    db = Database(db_filename)
    db.connect()
    db.create_table()
    yield db
    db.close()

@pytest.fixture(scope="function")
def csv_file(tmpdir):
    csv_filename = str(tmpdir.join("test.csv"))
    csv = CSV(csv_filename)
    yield csv

def test_database_connect(database):
    assert isinstance(database.conn, sqlite3.Connection)
    assert isinstance(database.c, sqlite3.Cursor)

def test_database_create_table(database):
    database.create_table()
    database.c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles'")
    assert database.c.fetchone()[0] == "articles"

def test_database_add_article_to_db(database):
    database.add_article_to_db("http://example.com", "Title", "Author", "2022/01/01")
    database.c.execute("SELECT * FROM articles")
    row = database.c.fetchone()
    assert row[1] == "http://example.com"
    assert row[2] == "Title"
    assert row[3] == "Author"
    assert row[4] == "2022/01/01"

def test_database_count_articles_with_title(database):
    database.add_article_to_db("http://example.com", "Title", "Author", "2022/01/01")
    count = database.count_articles_with_title("Title")
    assert count == 1


def test_database_get_articles_from_db(database):
    database.add_article_to_db("http://example.com", "Title", "Author", "2022/01/01")
    data = database.get_articles_from_db()
    assert len(data) == 1
    assert data[0][1] == "http://example.com"
    assert data[0][2] == "Title"
    assert data[0][3] == "Author"
    assert data[0][4] == "2022/01/01"

def test_csv_read_csv(csv_file):
    data_df = csv_file.read_csv()
    assert isinstance(data_df, pd.DataFrame)

def test_csv_add_row_to_csv(csv_file):
    row = {"id": 0, "url": "http://example.com", "headline": "Title", "author": "Author", "date": "2022/01/01"}
    csv_file.add_row_to_csv(row)
    data_df = pd.read_csv(csv_file.csv_filename)
    assert data_df.iloc[0]["url"] == "http://example.com"
    assert data_df.iloc[0]["headline"] == "Title"
    assert data_df.iloc[0]["author"] == "Author"
    assert data_df.iloc[0]["date"] == "2022/01/01"

def test_verge_scraper_get_data(mock_requests_get):
    scraper = VergeScraper("http://example.com")

    # Create a mock response object
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = "<!DOCTYPE html><html><body><script id='__NEXT_DATA__'>{\"test\": \"data\"}</script></body></html>"

    # Set the mock response for the requests.get() function
    mock_requests_get.return_value = mock_response

    scraper.get_data()
    assert scraper.data == {"test": "data"}

    # Ensure that requests.get() was called with the correct URL
    mock_requests_get.assert_called_once_with("http://example.com")
