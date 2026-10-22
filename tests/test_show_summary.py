
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
