
import server


def test_show_summary_with_known_email():
    client = server.app.test_client()

    response = client.post(
        "/showSummary",
        data={"email": "john@simplylift.co"},
    )

    assert response.status_code == 200


def test_show_summary_with_unknown_email_does_not_crash():
    client = server.app.test_client()

    response = client.post(
        "/showSummary",
        data={"email": "unknown@example.com"},
    )

    assert response.status_code != 500

def test_unknown_email_error_message_is_visible_after_redirect():
    client = server.app.test_client()

    response = client.post(
        "/showSummary",
        data={"email": "unknown@example.com"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Adresse e-mail inconnue".encode("utf-8") in response.data
    assert "Adresse e-mail inconnue".encode("utf-8") in response.data
