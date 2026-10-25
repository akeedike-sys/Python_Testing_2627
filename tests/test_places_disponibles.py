import server


def test_reservation_superieure_aux_places_disponibles_refusee():
    client = server.app.test_client()

    competition = next(
        c for c in server.competitions
        if c["name"] == "Spring Festival"
    )
    club = next(
        c for c in server.clubs
        if c["name"] == "Simply Lift"
    )

    date_originale = competition["date"]
    places_originales = competition["numberOfPlaces"]
    points_originaux = club["points"]
    reservations_originales = server.reservations.copy()

    competition["date"] = "2099-03-27 10:00:00"
    competition["numberOfPlaces"] = 2
    club["points"] = max(int(club["points"]), 10)

    try:
        response = client.post(
            "/purchasePlaces",
            data={
                "competition": "Spring Festival",
                "club": "Simply Lift",
                "places": "3",
            },
        )

        assert response.status_code == 302
        assert int(competition["numberOfPlaces"]) == 2
        assert int(club["points"]) == max(int(points_originaux), 10)
        assert server.reservations == reservations_originales

        page = client.get(response.location, follow_redirects=True)
        assert "pas assez de places" in page.get_data(as_text=True).lower()

    finally:
        competition["date"] = date_originale
        competition["numberOfPlaces"] = places_originales
        club["points"] = points_originaux
        server.reservations.clear()
        server.reservations.update(reservations_originales)