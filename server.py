
import json
from datetime import datetime

from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs():
    with open("clubs.json", encoding="utf-8") as c:
        return json.load(c)["clubs"]


def loadCompetitions():
    with open("competitions.json", encoding="utf-8") as comps:
        return json.load(comps)["competitions"]


app = Flask(__name__)
app.secret_key = "something_special"

competitions = loadCompetitions()
clubs = loadClubs()

# Suivi des réservations par club et par compétition.
# Attention : ces données sont conservées uniquement en mémoire.
reservations = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def showSummary():
    email = request.form.get("email", "").strip().lower()

    club = next(
        (
            c for c in clubs
            if c.get("email", "").strip().lower() == email
        ),
        None,
    )

    if club is None:
        flash("Adresse e-mail inconnue. Veuillez réessayer.")
        return redirect(url_for("index"))

    competitions_a_venir = []

    for comp in competitions:
        try:
            date_competition = datetime.strptime(
                comp["date"], "%Y-%m-%d %H:%M:%S"
            )
        except (KeyError, TypeError, ValueError):
            continue

        if date_competition > datetime.now():
            competitions_a_venir.append(comp)

    return render_template(
        "welcome.html",
        club=club,
        competitions=competitions_a_venir,
    )


@app.route("/book/<competition>/<club>")
def book(competition, club):
    found_club = next(
        (c for c in clubs if c["name"] == club),
        None,
    )
    found_competition = next(
        (c for c in competitions if c["name"] == competition),
        None,
    )

    if found_club is None or found_competition is None:
        flash("Club ou compétition introuvable.")
        return redirect(url_for("index"))

    return render_template(
        "booking.html",
        club=found_club,
        competition=found_competition,
    )


@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    competition_name = request.form.get("competition", "").strip()
    club_name = request.form.get("club", "").strip()

    competition = next(
        (c for c in competitions if c["name"] == competition_name),
        None,
    )
    club = next(
        (c for c in clubs if c["name"] == club_name),
        None,
    )

    if competition is None or club is None:
        flash("Club ou compétition introuvable.")
        return redirect(url_for("index"))

    booking_url = url_for(
        "book",
        competition=competition["name"],
        club=club["name"],
    )

    # Vérifier la date de la compétition.
    try:
        date_competition = datetime.strptime(
            competition["date"], "%Y-%m-%d %H:%M:%S"
        )
    except (KeyError, TypeError, ValueError):
        flash("La date de cette compétition est invalide.")
        return redirect(booking_url)

    if date_competition <= datetime.now():
        flash("Impossible de réserver une compétition passée.")
        return redirect(booking_url)

    # Vérifier le nombre de places demandé.
    try:
        places_demandees = int(request.form.get("places", ""))
    except (TypeError, ValueError):
        flash("Veuillez saisir un nombre de places valide.")
        return redirect(booking_url)

    if places_demandees <= 0:
        flash("Le nombre de places doit être supérieur à zéro.")
        return redirect(booking_url)

    # Maximum autorisé par club pour cette compétition :
    # 12 places au total, et non 12 à chaque réservation.
    cle_reservation = (club_name, competition_name)
    places_deja_reservees = reservations.get(cle_reservation, 0)

    if places_deja_reservees + places_demandees > 12:
        flash("Vous ne pouvez pas reserver plus de 12 places")
        return redirect(booking_url)

    # Vérifier les points et les places disponibles.
    try:
        points_club = int(club["points"])
        places_disponibles = int(competition["numberOfPlaces"])
    except (KeyError, TypeError, ValueError):
        flash("Les points du club ou les places disponibles sont invalides.")
        return redirect(booking_url)

    if points_club < places_demandees:
        flash("Votre club ne possède pas assez de points.")
        return redirect(booking_url)

    if places_disponibles < places_demandees:
        flash("Il ne reste pas assez de places pour cette compétition.")
        return redirect(booking_url)

    # Modifier les données seulement après toutes les validations.
    competition["numberOfPlaces"] = places_disponibles - places_demandees
    club["points"] = points_club - places_demandees
    reservations[cle_reservation] = (
        places_deja_reservees + places_demandees
    )

    flash("Réservation effectuée avec succès !")

    competitions_a_venir = []
    for comp in competitions:
        try:
            date_comp = datetime.strptime(
                comp["date"], "%Y-%m-%d %H:%M:%S"
            )
        except (KeyError, TypeError, ValueError):
            continue

        if date_comp > datetime.now():
            competitions_a_venir.append(comp)

    return render_template(
        "welcome.html",
        club=club,
        competitions=competitions_a_venir,
    )


@app.route("/points")
def points():
    """Afficher publiquement les clubs classés par points décroissants."""
    try:
        classement = sorted(
            clubs,
            key=lambda club: int(club["points"]),
            reverse=True,
        )
    except (KeyError, TypeError, ValueError):
        flash("Impossible de charger le classement des clubs.")
        return redirect(url_for("index"))

    return render_template("points.html", clubs=classement)


@app.route("/logout")
def logout():
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
