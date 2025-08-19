from unittest.mock import patch, ANY, MagicMock
from datetime import date

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


SAMPLE_GAZETTE_PAYLOAD = {
    "url": "http://example.com/gazette.pdf",
    "publication_date": "2025-07-15",
    "file_path": "/tmp/gazette.pdf",
    "details": "Official Gazette from July"
}


def create_mock_gazette():
    """Helper function to create a configured mock gazette object."""

    gazette = MagicMock()
    gazette.id = 1
    gazette.url = SAMPLE_GAZETTE_PAYLOAD["url"]
    gazette.publication_date = date.fromisoformat(SAMPLE_GAZETTE_PAYLOAD["publication_date"])
    gazette.file_path = SAMPLE_GAZETTE_PAYLOAD["file_path"]
    gazette.details = SAMPLE_GAZETTE_PAYLOAD["details"]
    gazette.created_at = date.today()

    return gazette


@patch('src.conthabil.crud.create_gazette')
def test_create_gazette_success(mock_create_gazette):
    """
    Tests successful creation of a gazette.
    """

    # Arrange
    mock_create_gazette.return_value = create_mock_gazette()

    # Act
    response = client.post("/api/gazettes/", json=SAMPLE_GAZETTE_PAYLOAD)

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["url"] == SAMPLE_GAZETTE_PAYLOAD["url"]
    assert response_data["id"] == 1

    assert SAMPLE_GAZETTE_PAYLOAD["publication_date"] in response_data["publication_date"]

    mock_create_gazette.assert_called_once_with(db=ANY, gazette=ANY)


def test_create_gazette_bad_payload():
    """
    Tests API behavior with a bad payload.
    """

    # Act
    response = client.post("/api/gazettes/", json={"url": "bad-url"})

    # Assert
    assert response.status_code == 422


@patch('src.conthabil.crud.get_gazettes')
def test_read_gazettes_no_filter(mock_get_gazettes):
    """
    Tests retrieving gazettes without any filters.
    """

    # Arrange
    mock_get_gazettes.return_value = [create_mock_gazette()]

    # Act
    response = client.get("/api/gazettes/")

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["id"] == 1

    mock_get_gazettes.assert_called_once_with(ANY, skip=0, limit=100)


@patch('src.conthabil.crud.get_gazettes_by_month_year')
def test_read_gazettes_with_filter(mock_get_by_month_year):
    """
    Tests retrieving gazettes with month and year filters.
    """

    # Arrange
    mock_get_by_month_year.return_value = [create_mock_gazette()]
    test_month = 7
    test_year = 2025

    # Act
    response = client.get(f"/api/gazettes/?month={test_month}&year={test_year}")

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 1
    assert SAMPLE_GAZETTE_PAYLOAD["publication_date"] in response_data[0]["publication_date"]

    mock_get_by_month_year.assert_called_once_with(ANY, month=test_month, year=test_year)


def test_read_gazettes_filter_error():
    """
    Tests that providing only month or only year results in an error.
    """

    # Act
    response_month_only = client.get("/api/gazettes/?month=7")
    response_year_only = client.get("/api/gazettes/?year=2025")

    # Assert
    assert response_month_only.status_code == 400
    assert response_month_only.json() == {"detail": "Both month and year must be provided for filtering."}

    assert response_year_only.status_code == 400
    assert response_year_only.json() == {"detail": "Both month and year must be provided for filtering."}

