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
    original_points = club["points"]
    reservations_originales = server.reservations.copy()

    competition["date"] = "2099-03-27 10:00:00"

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

        redirected_response = client.get(
            response.location, follow_redirects=True
        )
        assert redirected_response.status_code == 200
        assert (
            "Vous ne pouvez pas reserver plus de 12 places"
            in redirected_response.get_data(as_text=True)
        )
    finally:
        competition["date"] = date_originale
        competition["numberOfPlaces"] = original_places
        club["points"] = original_points
        server.reservations.clear()
        server.reservations.update(reservations_originales)


def test_deux_reservations_ne_peuvent_pas_depasser_12_places():
    client = server.app.test_client()

    competition = next(
        c for c in server.competitions
        if c["name"] == "Spring Festival"
    )
    club = next(
        c for c in server.clubs
        if c["name"] == "Simply Lift"
    )

    places_originales = competition["numberOfPlaces"]
    date_originale = competition["date"]
    points_originaux = club["points"]
    reservations_originales = server.reservations.copy()

    competition["date"] = "2099-03-27 10:00:00"

    try:
        premiere = client.post(
            "/purchasePlaces",
            data={
                "competition": "Spring Festival",
                "club": "Simply Lift",
                "places": "8",
            },
        )
        assert premiere.status_code == 200

        places_apres_premiere = int(competition["numberOfPlaces"])
        points_apres_premiere = int(club["points"])

        seconde = client.post(
            "/purchasePlaces",
            data={
                "competition": "Spring Festival",
                "club": "Simply Lift",
                "places": "5",
            },
        )

        assert seconde.status_code == 302
        assert int(competition["numberOfPlaces"]) == places_apres_premiere
        assert int(club["points"]) == points_apres_premiere
    finally:
        competition["date"] = date_originale
        competition["numberOfPlaces"] = places_originales
        club["points"] = points_originaux
        server.reservations.clear()
        server.reservations.update(reservations_originales)

import pytest


@pytest.mark.parametrize("places", ["0", "-2", "abc", ""])
def test_places_invalides_sont_refusees(places):
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

    try:
        response = client.post(
            "/purchasePlaces",
            data={
                "competition": "Spring Festival",
                "club": "Simply Lift",
                "places": places,
            },
        )

        assert response.status_code == 302
        assert competition["numberOfPlaces"] == places_originales
        assert club["points"] == points_originaux
        assert server.reservations == reservations_originales
    finally:
        competition["date"] = date_originale
        competition["numberOfPlaces"] = places_originales
        club["points"] = points_originaux
        server.reservations.clear()
        server.reservations.update(reservations_originales)
