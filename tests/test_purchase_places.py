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
from datetime import date, timedelta


def test_two_reservations_cannot_exceed_12_places():
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
    original_date = competition.get("date")

    # Utiliser une date future pour rendre le test indépendant
    # de la date réelle d'exécution.
    competition["date"] = (date.today() + timedelta(days=30)).isoformat()

    try:
        first_response = client.post(
            "/purchasePlaces",
            data={
                "competition": "Spring Festival",
                "club": "Simply Lift",
                "places": "8",
            },
        )
        assert first_response.status_code == 200

        places_after_first = int(competition["numberOfPlaces"])
        points_after_first = int(club["points"])

        second_response = client.post(
            "/purchasePlaces",
            data={
                "competition": "Spring Festival",
                "club": "Simply Lift",
                "places": "5",
            },
        )

        assert second_response.status_code == 302
        assert int(competition["numberOfPlaces"]) == places_after_first
        assert int(club["points"]) == points_after_first

    finally:
        competition["numberOfPlaces"] = original_places
        club["points"] = original_points
        if original_date is None:
            competition.pop("date", None)
        else:
            competition["date"] = original_date
