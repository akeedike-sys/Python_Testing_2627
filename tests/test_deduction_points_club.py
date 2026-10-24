import server


def test_une_reservation_deduit_les_points_du_club():
    client = server.app.test_client()

    competition = next(
        c for c in server.competitions
        if c["name"] == "Spring Festival"
    )
    club = next(
        c for c in server.clubs
        if c["name"] == "Simply Lift"
    )

    places_initiales = competition["numberOfPlaces"]
    date_originale = competition["date"]
    competition["date"] = "2099-03-27 10:00:00"
    points_initiaux = club["points"]

    try:
        reponse = client.post(
            "/purchasePlaces",
            data={
                "competition": "Spring Festival",
                "club": "Simply Lift",
                "places": "2",
            },
        )

        assert reponse.status_code == 200
        assert int(competition["numberOfPlaces"]) == int(places_initiales) - 2
        assert int(club["points"]) == int(points_initiaux) - 2
    finally:
        competition["date"] = date_originale
        competition["numberOfPlaces"] = places_initiales
        club["points"] = points_initiaux
