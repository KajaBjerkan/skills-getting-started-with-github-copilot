"""
Integration tests for complex multi-step workflows.
These tests validate end-to-end scenarios involving multiple API calls.
"""

import pytest


def test_signup_then_unregister_then_signup_again(client):
    """Test signup → unregister → re-signup workflow."""
    activity = "Basketball Team"
    email = "workflow@mergington.edu"
    
    # Step 1: Sign up
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]
    
    # Step 2: Unregister
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]
    
    # Step 3: Sign up again (should succeed)
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]


def test_multiple_signups_different_activities(client):
    """Test signing up for multiple different activities."""
    email = "multi@mergington.edu"
    activities = ["Basketball Team", "Swimming Club", "Art Studio"]
    
    # Sign up for multiple activities
    for activity in activities:
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify signup in all activities
    activities_data = client.get("/activities").json()
    for activity in activities:
        assert email in activities_data[activity]["participants"]


def test_signup_multiple_users_same_activity(client):
    """Test multiple different users signing up for the same activity."""
    activity = "Programming Class"
    emails = [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu"
    ]
    
    # Signup multiple users
    for email in emails:
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all are signed up
    activity_data = client.get("/activities").json()[activity]
    for email in emails:
        assert email in activity_data["participants"]
    
    # Verify participant count increased
    total_participants = len(activity_data["participants"])
    assert total_participants >= len(emails)


def test_unregister_one_from_pre_populated_activity(client):
    """Test removing one person from activity with initial participants."""
    activity = "Chess Club"
    # Chess Club starts with 2 participants
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity]["participants"])
    
    # Unregister one
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 200
    
    # Verify count decreased
    after_response = client.get("/activities")
    after_count = len(after_response.json()[activity]["participants"])
    assert after_count == initial_count - 1


def test_signup_then_check_participant_list_order(client):
    """Test that participants list maintains integrity after operations."""
    activity = "Gym Class"
    new_email = "newstudent@mergington.edu"
    
    # Get initial participants
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()[activity]["participants"]
    
    # Sign up new participant
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": new_email}
    )
    assert response.status_code == 200
    
    # Check participants list
    updated_response = client.get("/activities")
    updated_participants = updated_response.json()[activity]["participants"]
    
    # New participant should be in list
    assert new_email in updated_participants
    
    # All previous participants should still be there
    for email in initial_participants:
        assert email in updated_participants


def test_unregister_then_signup_different_activity(client):
    """Test unregister from one activity and sign up for another."""
    email = "switcher@mergington.edu"
    activity1 = "Drama Club"
    activity2 = "Debate Team"
    
    # Sign up for activity 1
    response = client.post(
        f"/activities/{activity1}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Unregister from activity 1
    response = client.delete(
        f"/activities/{activity1}/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Sign up for activity 2
    response = client.post(
        f"/activities/{activity2}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify state
    activities_data = client.get("/activities").json()
    assert email not in activities_data[activity1]["participants"]
    assert email in activities_data[activity2]["participants"]


def test_activities_list_consistency_after_operations(client):
    """Test that GET /activities returns consistent data after modifications."""
    activity1 = "Science Club"
    activity2 = "Art Studio"
    email = "consistency@mergington.edu"
    
    # Perform various operations
    client.post(f"/activities/{activity1}/signup", params={"email": email})
    client.post(f"/activities/{activity2}/signup", params={"email": email})
    
    # Get activities list multiple times
    response1 = client.get("/activities")
    response2 = client.get("/activities")
    response3 = client.get("/activities")
    
    # All responses should be identical
    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()
    
    assert data1 == data2
    assert data2 == data3


def test_duplicate_signup_attempt_preserves_state(client):
    """Test that failed duplicate signup doesn't change state."""
    activity = "Swimming Club"
    email = "duplicate@mergington.edu"
    
    # First signup
    response1 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Get participant count after first signup
    data_after_first = client.get("/activities").json()[activity]
    count_after_first = len(data_after_first["participants"])
    
    # Try duplicate signup (should fail)
    response2 = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response2.status_code == 400
    
    # Get participant count after duplicate attempt
    data_after_duplicate = client.get("/activities").json()[activity]
    count_after_duplicate = len(data_after_duplicate["participants"])
    
    # Count should be unchanged
    assert count_after_first == count_after_duplicate
    # Email should appear only once
    assert data_after_duplicate["participants"].count(email) == 1
