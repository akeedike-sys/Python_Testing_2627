import server


def test_booking_page_requires_club_session():
    client = server.app.test_client()

    response = client.get(
        "/book/Spring Festival/Simply Lift",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.location.endswith("/")


def test_purchase_requires_club_session_without_changing_data():
    client = server.app.test_client()

    competition = next(
        c for c in server.competitions
        if c["name"] == "Spring Festival"
    )
    club = next(
        c for c in server.clubs
        if c["name"] == "Simply Lift"
    )

    original_places = competition["numberOfPlaces"]
    original_points = club["points"]

    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "1",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.location.endswith("/")
    assert competition["numberOfPlaces"] == original_places
    assert club["points"] == original_points

def test_connected_club_cannot_purchase_for_another_club():
    client = server.app.test_client()

    login = client.post(
        "/showSummary",
        data={"email": "john@simplylift.co"},
    )
    assert login.status_code == 200

    competition = next(
        c for c in server.competitions
        if c["name"] == "Spring Festival"
    )
    other_club = next(
        c for c in server.clubs
        if c["name"] != "Simply Lift"
    )

    places_before = competition["numberOfPlaces"]
    points_before = other_club["points"]

    response = client.post(
        "/purchasePlaces",
        data={
            "competition": "Spring Festival",
            "club": other_club["name"],
            "places": "1",
        },
    )

    assert response.status_code == 302
    assert response.location.endswith("/")
    assert competition["numberOfPlaces"] == places_before
    assert other_club["points"] == points_before
