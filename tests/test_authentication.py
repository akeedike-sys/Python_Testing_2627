
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
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.location.endswith("/")
    assert competition["numberOfPlaces"] == places_before
    assert other_club["points"] == points_before


def test_logout_clears_session_and_blocks_protected_pages():
    client = server.app.test_client()

    # Se connecter avec un club connu.
    login = client.post(
        "/showSummary",
        data={"email": "john@simplylift.co"},
    )
    assert login.status_code == 200

    with client.session_transaction() as sess:
        assert sess.get("club_email") == "john@simplylift.co"

    # Se déconnecter.
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302

    # Vérifier que la session ne contient plus le club connecté.
    with client.session_transaction() as sess:
        assert "club_email" not in sess

    # Vérifier que la page protégée refuse de nouveau l'accès.
    protected = client.get(
        "/book/Spring Festival/Simply Lift",
        follow_redirects=False,
    )

    assert protected.status_code == 302
    assert protected.location.endswith("/")
