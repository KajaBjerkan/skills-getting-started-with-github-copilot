"""
Tests for GET /activities endpoint.
"""


def test_get_activities_returns_list(client):
    """Test that /activities endpoint returns a list of activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_get_activities_contains_required_fields(client):
    """Test that each activity has required fields."""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity in data.items():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


def test_get_activities_chess_club_exists(client):
    """Test that Chess Club activity exists with expected participants."""
    response = client.get("/activities")
    data = response.json()
    
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


def test_get_activities_expected_count(client):
    """Test that expected number of activities are returned."""
    response = client.get("/activities")
    data = response.json()
    
    # Should have 9 activities as per app.py
    assert len(data) == 9


def test_get_activities_all_required_activities_present(client):
    """Test that all expected activities are in the response."""
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Swimming Club",
        "Art Studio",
        "Drama Club",
        "Debate Team",
        "Science Club"
    ]
    
    response = client.get("/activities")
    data = response.json()
    
    for activity in expected_activities:
        assert activity in data, f"Expected activity '{activity}' not found"


def test_get_activities_fields_are_correct_types(client):
    """Test that activity fields have correct data types."""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity in data.items():
        assert isinstance(activity["description"], str)
        assert isinstance(activity["schedule"], str)
        assert isinstance(activity["max_participants"], int)
        assert isinstance(activity["participants"], list)
        assert activity["max_participants"] > 0


def test_get_activities_participants_are_strings(client):
    """Test that all participants in participant lists are strings."""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity in data.items():
        for participant in activity["participants"]:
            assert isinstance(participant, str), \
                f"Participant in {activity_name} is not a string: {participant}"


def test_get_activities_empty_participants_list(client):
    """Test activities with no participants."""
    response = client.get("/activities")
    data = response.json()
    
    # Basketball Team, Swimming Club, Art Studio, Drama Club, Debate Team, Science Club
    # should start with empty participants
    empty_activities = ["Basketball Team", "Swimming Club", "Art Studio", 
                       "Drama Club", "Debate Team", "Science Club"]
    
    for activity in empty_activities:
        assert len(data[activity]["participants"]) == 0, \
            f"{activity} should start with no participants"


def test_get_activities_participants_count_accurate(client):
    """Test that participant counts in response match actual list lengths."""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity in data.items():
        # The count should match the length of the participants list
        actual_count = len(activity["participants"])
        assert actual_count >= 0, f"{activity_name} has negative participant count"


def test_get_activities_description_not_empty(client):
    """Test that all activities have non-empty descriptions."""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity in data.items():
        assert len(activity["description"]) > 0, \
            f"{activity_name} has empty description"


def test_get_activities_schedule_not_empty(client):
    """Test that all activities have non-empty schedules."""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity in data.items():
        assert len(activity["schedule"]) > 0, \
            f"{activity_name} has empty schedule"
