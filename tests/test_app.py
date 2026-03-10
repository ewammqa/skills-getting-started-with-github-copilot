import pytest
from fastapi.testclient import TestClient
from src.app import app
import copy

# Mock activities data for isolation
def get_mock_activities():
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": []
        }
    }

@pytest.fixture(autouse=True)
def mock_activities(monkeypatch):
    # Arrange: Patch activities with mock data
    from src import app as app_module
    app_module.activities = get_mock_activities()

client = TestClient(app)

# Test GET /activities
def test_get_activities():
    # Arrange: Already mocked
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()

# Test POST /activities/{activity_name}/signup
def test_signup_for_activity():
    # Arrange: Already mocked
    email = "test@mergington.edu"
    # Act
    response = client.post("/activities/Chess Club/signup?email=" + email)
    # Assert
    assert response.status_code == 200
    assert email in client.get("/activities").json()["Chess Club"]["participants"]

# Test duplicate signup
def test_signup_duplicate():
    email = "test@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

# Test signup for invalid activity
def test_signup_invalid_activity():
    response = client.post("/activities/Invalid/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

# Test DELETE /activities/{activity_name}/unregister
def test_unregister_for_activity():
    email = "test@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 200
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]

# Test unregister for invalid activity
def test_unregister_invalid_activity():
    response = client.delete("/activities/Invalid/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

# Test unregister for non-existent participant
def test_unregister_nonexistent():
    response = client.delete("/activities/Chess Club/unregister?email=ghost@mergington.edu")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]
