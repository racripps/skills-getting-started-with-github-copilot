import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Chess Club"
EXISTING_EMAIL = "existing@mergington.edu"


@pytest.fixture
def client(monkeypatch):
    activities = {
        ACTIVITY_NAME: {
            "description": "Test activity",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 3,
            "participants": [EXISTING_EMAIL],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_activities = {
        ACTIVITY_NAME: {
            "description": "Test activity",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 3,
            "participants": [EXISTING_EMAIL],
        }
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_new_participant(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {ACTIVITY_NAME}"}
    participants = client.get("/activities").json()[ACTIVITY_NAME]["participants"]
    assert participants == [EXISTING_EMAIL, email]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}
    participants = client.get("/activities").json()[ACTIVITY_NAME]["participants"]
    assert participants == [EXISTING_EMAIL]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {ACTIVITY_NAME}"
    }
    participants = client.get("/activities").json()[ACTIVITY_NAME]["participants"]
    assert participants == []


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.delete(
        "/activities/Unknown%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_unregistered_participant(client):
    # Arrange
    email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    participants = client.get("/activities").json()[ACTIVITY_NAME]["participants"]
    assert participants == [EXISTING_EMAIL]
