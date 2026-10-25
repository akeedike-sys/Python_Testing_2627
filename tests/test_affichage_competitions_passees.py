import server
from datetime import datetime, timedelta


def test_show_summary_does_not_display_past_competitions():
    client = server.app.test_client()

    competition_passee = next(
        c for c in server.competitions
        if c["name"] == "Spring Festival"
    )
    date_initiale = competition_passee["date"]

    try:
        competition_passee["date"] = (
            datetime.now() - timedelta(days=1)
        ).strftime("%Y-%m-%d %H:%M:%S")

        response = client.post(
            "/showSummary",
            data={"email": "john@simplylift.co"},
        )

        assert response.status_code == 200
        assert b"Spring Festival" not in response.data
    finally:
        competition_passee["date"] = date_initiale
