import server


def test_purchase_non_numeric_places_is_rejected():
    client = server.app.test_client()

    connexion = client.post(
        "/showSummary",
        data={"email": "john@simplylift.co"},
    )
    assert connexion.status_code == 200

    competition = next(
        c for c in server.competitions
        if c["name"] == "Spring Festival"
    )
    club = next(
        c for c in server.clubs
        if c["name"] == "Simply Lift"
    )

    original_places = competition["numberOfPlaces"]
    original_date = competition["date"]
    original_points = club["points"]

    competition["date"] = "2099-03-27 10:00:00"

    try:
        response = client.post(
            "/purchasePlaces",
            data={
                "competition": "Spring Festival",
                "club": "Simply Lift",
                "places": "abc",
            },
        )

        assert response.status_code == 302
        assert int(competition["numberOfPlaces"]) == int(original_places)
        assert int(club["points"]) == int(original_points)

        page = client.get(response.location, follow_redirects=True)
        assert page.status_code == 200
        assert "places" in page.get_data(as_text=True).lower()

    finally:
        competition["date"] = original_date
        competition["numberOfPlaces"] = original_places
        club["points"] = original_points
