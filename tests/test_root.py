"""
Tests for GET / endpoint.
"""


def test_root_redirect(client):
    """Test that root endpoint redirects to static/index.html."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"
