"""
Tests for DELETE /activities/{activity_name}/unregister endpoint.
"""

import pytest


def test_unregister_success(client, sample_email):
    """Test successful unregister from an activity."""
    activity = "Basketball Team"
    
    # First, sign up
    client.post(
        f"/activities/{activity}/signup",
        params={"email": sample_email}
    )
    
    # Then unregister
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": sample_email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert sample_email in data["message"]
    assert activity in data["message"]


def test_unregister_not_signed_up_fails(client, sample_email):
    """Test that unregistering a non-signed-up participant fails."""
    activity = "Swimming Club"
    
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": sample_email}
    )
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"].lower()


def test_unregister_invalid_activity_fails(client, sample_email):
    """Test that unregistering from non-existent activity fails."""
    response = client.delete(
        "/activities/Nonexistent Activity/unregister",
        params={"email": sample_email}
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_unregister_removes_participant(client, sample_email):
    """Test that unregister actually removes participant from activity."""
    activity = "Art Studio"
    
    # Sign up
    client.post(
        f"/activities/{activity}/signup",
        params={"email": sample_email}
    )
    
    # Get count before unregister
    response = client.get("/activities")
    before_count = len(response.json()[activity]["participants"])
    
    # Unregister
    client.delete(
        f"/activities/{activity}/unregister",
        params={"email": sample_email}
    )
    
    # Check that participant was removed
    response = client.get("/activities")
    after_count = len(response.json()[activity]["participants"])
    assert after_count == before_count - 1
    assert sample_email not in response.json()[activity]["participants"]


def test_unregister_empty_email_fails(client, sample_activity):
    """Test that unregister with empty email fails."""
    response = client.delete(
        f"/activities/{sample_activity}/unregister",
        params={"email": ""}
    )
    assert response.status_code == 400


def test_unregister_missing_email_parameter_fails(client, sample_activity):
    """Test that unregister without email parameter fails."""
    response = client.delete(f"/activities/{sample_activity}/unregister")
    assert response.status_code in [400, 422]


def test_unregister_case_sensitivity(client, sample_activity):
    """Test unregister with different case variations of email."""
    activity = sample_activity
    email = "Test@mergington.edu"
    
    # Sign up with original case
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Try unregister with different case
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email.lower()}
    )
    # Should fail if emails are case-sensitive, succeed if case-insensitive
    # Test documents current behavior
    assert response.status_code in [200, 400]


def test_unregister_success_from_pre_populated_activity(client):
    """Test unregister from activity that has initial participants."""
    activity = "Chess Club"
    # Chess Club starts with ["michael@mergington.edu", "daniel@mergington.edu"]
    email_to_remove = "michael@mergington.edu"
    
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email_to_remove}
    )
    assert response.status_code == 200
    
    # Verify removal
    response = client.get("/activities")
    assert email_to_remove not in response.json()[activity]["participants"]


def test_unregister_response_includes_activity_name(client, sample_email, sample_activity):
    """Test that success response includes activity name."""
    activity = sample_activity
    
    # Sign up first
    client.post(
        f"/activities/{activity}/signup",
        params={"email": sample_email}
    )
    
    # Unregister and check response
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": sample_email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert activity in data["message"]
