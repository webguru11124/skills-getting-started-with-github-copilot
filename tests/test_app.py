import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

# Store initial activities for resetting
initial_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))

@pytest.fixture
def client():
    return TestClient(app)

def test_get_activities(client):
    # Arrange: No specific setup needed as activities are reset by fixture
    
    # Act: Make a GET request to /activities
    response = client.get("/activities")
    
    # Assert: Check status code and response structure
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]

def test_signup_for_activity_success(client):
    # Arrange: Choose an activity and a new email
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act: Make a POST request to signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Check success and that email was added
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    # Verify in activities
    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity_name]["participants"]

def test_signup_for_activity_already_signed_up(client):
    # Arrange: Sign up first
    activity_name = "Programming Class"
    email = "test@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Act: Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Should fail with 400
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_for_nonexistent_activity(client):
    # Arrange: Use a fake activity name
    activity_name = "Fake Club"
    email = "student@mergington.edu"
    
    # Act: Attempt signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Assert: Should return 404
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_remove_participant_success(client):
    # Arrange: Add a participant first
    activity_name = "Gym Class"
    email = "removeme@mergington.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Act: Remove the participant
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    
    # Assert: Check success and removal
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    # Verify removed
    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity_name]["participants"]

def test_remove_participant_not_found(client):
    # Arrange: Use an email not in the activity
    activity_name = "Basketball Team"
    email = "notsignedup@mergington.edu"
    
    # Act: Attempt removal
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    
    # Assert: Should return 404
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]