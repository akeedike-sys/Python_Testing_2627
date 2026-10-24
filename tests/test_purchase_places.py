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
    date_originale = competition["date"]
    competition["date"] = "2099-03-27 10:00:00"
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
        assert "Vous ne pouvez pas reserver plus de 12 places" in redirected_response.get_data(as_text=True)
    finally:
        competition["date"] = date_originale
        competition["numberOfPlaces"] = original_places
        club["points"] = original_points
