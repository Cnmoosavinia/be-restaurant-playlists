from os import environ
import pytest

environ[
    "PYTEST_CURRENT_TEST"
] = ""  # This ensures that the connection file selects the correct environment
from db.seed import seed
from db.seed_data.test_data import playlists, users, restaurants, votes
from app import app
import json
from ast import literal_eval


# PYTHONPATH=$(pwd) py.test -rP
# <optional keyword searches with -k -v>


# utility functions


def create_dict(byte):
    return literal_eval(byte.decode("utf-8"))


# tests


@pytest.fixture
def test_app():
    test_app = app
    test_app.config.update(
        {
            "TESTING": True,
        }
    )
    seed(playlists, users, restaurants, votes)
    yield test_app


@pytest.fixture()
def client(test_app):
    return test_app.test_client()


@pytest.fixture()
def runner(test_app):
    return test_app.test_cli_runner()


@pytest.mark.ticket_5
def test_get_playlists_keys(client):
    response = client.get("/api/playlists")
    result = create_dict(response.data)
    array = result["playlists"]
    vote_count_values = []
    count = 0
    assert response.status == "200 OK", "Test Failed"
    for playlist in array:
        assert "cuisine" in playlist, "test failed"
        assert "description" in playlist, "test failed"
        assert "location" in playlist, "test failed"
        assert "name" in playlist, "test failed"
        assert "owner_email" not in playlist, "test failed"
        assert "playlist_id" in playlist, "test failed"
        assert "vote_count" in playlist, "test failed"
        assert "nickname" in playlist, "test failed"
        vote_count_values.append(playlist["vote_count"])
    for i in range(len(vote_count_values)):
        if count != len(vote_count_values) - 1:
            vote_number1 = float(vote_count_values[i])
            vote_number2 = float(vote_count_values[i + 1])
            assert vote_number1 >= vote_number2, "test_failed"
            count = count + 1


@pytest.mark.request_specific_playlist  # this is showing as a warning
def test_request_specific_playlist_success(client):
    response = client.get("/api/playlists/1")
    playlistBytes = response.data
    playlist = json.loads(playlistBytes.decode("utf-8"))

    assert response.status == "200 OK", "incorrect http response"
    assert type(playlist["playlist"]) == list, "Test failed"

    for playlist in playlist["playlist"]:
        assert playlist["playlist_id"] == 1, "Test failed"
        assert "name" in playlist, "Test failed"
        assert "place_id" in playlist, "Test failed"
        assert "location" in playlist, "Test failed"
        assert "cuisine" in playlist, "Test failed"
        assert "owner_nickname" in playlist, "Test failed"
        assert "description" in playlist, "Test failed"


def test_request_specific_playlist_valid_but_nonexistent_playlist_id(client):
    response = client.get("/api/playlists/1000000")
    playlistBytes = response.data
    playlist = json.loads(playlistBytes.decode("utf-8"))

    assert response.status == "404 NOT FOUND", "incorrect http response"
    assert playlist["msg"] == "playlist not found"


def test_request_specific_playlist_invalid_playlist_id(client):
    response = client.get("/api/playlists/sdfghjkl")
    playlistBytes = response.data
    playlist = json.loads(playlistBytes.decode("utf-8"))

    assert response.status == "400 BAD REQUEST", "incorrect http response"
    assert playlist["msg"] == "invalid playlist id"


@pytest.mark.post_new_user  # this is showing as a warning
def test_post_new_user(client):
    response = client.post(
        "/api/users",
        json={
            "user_email": "someone@example.com",
            "nickname": "Myself",
            "avatar_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSwlrNQyIFCa1XnXF1Ex8lSuOHhHaWxd3_zWR2m3j6Tig&s",
        },
    )
    user_bytes = response.data
    user = json.loads(user_bytes.decode("utf-8"))
    print(user)
    assert response.status == "201 CREATED", "incorrect http response"
    assert user["user"]["user_email"] == "someone@example.com"
    assert user["user"]["nickname"] == "Myself"
    assert (
        user["user"]["avatar_url"]
        == "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSwlrNQyIFCa1XnXF1Ex8lSuOHhHaWxd3_zWR2m3j6Tig&s"
    )


def test_post_new_user_with_excess_data(client):
    response = client.post(
        "/api/users",
        json={
            "useless_property": "useless_value",
            "user_email": "someone@example.com",
            "nickname": "Myself",
            "avatar_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSwlrNQyIFCa1XnXF1Ex8lSuOHhHaWxd3_zWR2m3j6Tig&s",
        },
    )
    user_bytes = response.data
    user = json.loads(user_bytes.decode("utf-8"))
    assert response.status == "201 CREATED", "incorrect http response"
    assert user["user"]["user_email"] == "someone@example.com"
    assert user["user"]["nickname"] == "Myself"
    assert (
        user["user"]["avatar_url"]
        == "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSwlrNQyIFCa1XnXF1Ex8lSuOHhHaWxd3_zWR2m3j6Tig&s"
    )
    assert user["user"].get("useless_property") is None


def test_post_new_user_with_incomplete_data(client):
    response = client.post(
        "/api/users",
        json={
            "nickname": "Myself",
        },
    )
    user_bytes = response.data
    user = json.loads(user_bytes.decode("utf-8"))
    assert response.status == "400 BAD REQUEST", "incorrect http response"
    assert user["msg"] == "Invalid Request Body"


@pytest.mark.post_new_playlist  # this is showing as a warning
def test_post_new_playlist(client):
    response = client.post("/api/playlists", json= {
        "name": "Yousif's playlist",
        "description": "My playlist nice description",
        "location": "Nice Location",
        "cuisine": "Seafood",
        "owner_email": "ymca2@restaurant-playlists.com"
    })



                    # name, description, location, cuisine, owner_email
