import server


def test_purchase_more_than_12_places_is_rejected():
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

    try:
        response = client.post(
            "/purchasePlaces",
            data={
                "competition": "Spring Festival",
                "club": "Simply Lift",
                "places": "13",
            },
        )

        assert response.status_code == 302
        assert int(competition["numberOfPlaces"]) == int(original_places)
        assert int(club["points"]) == int(original_points)

        redirected_response = client.get(response.location, follow_redirects=True)
        assert redirected_response.status_code == 200
        assert b"12" in redirected_response.data
    finally:
        competition["numberOfPlaces"] = original_places
        club["points"] = original_points
