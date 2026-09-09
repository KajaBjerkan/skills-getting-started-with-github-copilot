"""
Tests for POST /activities/{activity_name}/signup endpoint.
"""

import pytest


def test_signup_success(client, sample_email, sample_activity):
    """Test successful signup for an activity."""
    response = client.post(
        f"/activities/{sample_activity}/signup",
        params={"email": sample_email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert sample_email in data["message"]
    assert sample_activity in data["message"]


def test_signup_duplicate_email_fails(client, sample_email, sample_activity):
    """Test that signing up with same email twice fails."""
    # First signup
    client.post(
        f"/activities/{sample_activity}/signup",
        params={"email": sample_email}
    )
    
    # Second signup with same email should fail
    response = client.post(
        f"/activities/{sample_activity}/signup",
        params={"email": sample_email}
    )
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"].lower()


def test_signup_invalid_activity_fails(client, sample_email):
    """Test that signing up for non-existent activity fails."""
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": sample_email}
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_signup_adds_participant(client, sample_email):
    """Test that signup actually adds participant to activity."""
    activity = "Basketball Team"
    
    # Get initial count
    response = client.get("/activities")
    initial_count = len(response.json()[activity]["participants"])
    
    # Sign up
    client.post(
        f"/activities/{activity}/signup",
        params={"email": sample_email}
    )
    
    # Check that participant was added
    response = client.get("/activities")
    new_count = len(response.json()[activity]["participants"])
    assert new_count == initial_count + 1
    assert sample_email in response.json()[activity]["participants"]


def test_signup_empty_email_accepted_by_app(client, sample_activity):
    """
    Test that app currently accepts empty email (documents current behavior).
    Note: This may be undesired behavior - app should likely validate email format.
    """
    response = client.post(
        f"/activities/{sample_activity}/signup",
        params={"email": ""}
    )
    # Currently app accepts empty email - this documents that behavior
    assert response.status_code == 200


def test_signup_missing_email_parameter_fails(client, sample_activity):
    """Test that signup without email parameter fails."""
    response = client.post(f"/activities/{sample_activity}/signup")
    assert response.status_code in [400, 422]  # Bad request or validation error


def test_signup_whitespace_email_accepted_by_app(client, sample_activity):
    """
    Test that app currently accepts whitespace-only email (documents current behavior).
    Note: This may be undesired behavior - app should likely validate email format.
    """
    response = client.post(
        f"/activities/{sample_activity}/signup",
        params={"email": "   "}
    )
    # Currently app accepts whitespace email - this documents that behavior
    assert response.status_code == 200


def test_signup_special_characters_in_email(client, sample_activity):
    """Test signup with special characters in email."""
    # These should technically be allowed in email format, but test handling
    special_emails = [
        "user+tag@mergington.edu",
        "first.last@mergington.edu",
        "user_name@mergington.edu"
    ]
    for email in special_emails:
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": email}
        )
        # Should succeed - these are valid email formats
        assert response.status_code == 200


def test_signup_response_includes_activity_name(client, sample_email, sample_activity):
    """Test that success response includes activity name."""
    response = client.post(
        f"/activities/{sample_activity}/signup",
        params={"email": sample_email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert sample_activity in data["message"]


def test_signup_response_includes_email(client, sample_email, sample_activity):
    """Test that success response includes email address."""
    response = client.post(
        f"/activities/{sample_activity}/signup",
        params={"email": sample_email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert sample_email in data["message"]
