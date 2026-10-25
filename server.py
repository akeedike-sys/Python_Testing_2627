
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs():
    with open('clubs.json', encoding='utf-8') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json', encoding='utf-8') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email', '').strip()

    club = next(
        (club for club in clubs
         if club['email'].strip().lower() == email.lower()),
        None
    )

    if club is None:
        flash("Adresse e-mail inconnue. Veuillez reessayer.")
        return redirect(url_for('index'))

    competitions_a_venir = []
    for comp in competitions:
        try:
            date_competition = datetime.strptime(
                comp['date'], '%Y-%m-%d %H:%M:%S'
            )
        except (KeyError, TypeError, ValueError):
            continue

        if date_competition > datetime.now():
            competitions_a_venir.append(comp)

    return render_template(
        'welcome.html',
        club=club,
        competitions=competitions_a_venir
    )

@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next(
        (c for c in clubs if c['name'] == club),
        None
    )
    foundCompetition = next(
        (c for c in competitions if c['name'] == competition),
        None
    )

    if foundClub is None or foundCompetition is None:
        flash("Club ou competition introuvable.")
        return redirect(url_for('index'))

    return render_template(
        'booking.html',
        club=foundClub,
        competition=foundCompetition
    )


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competitionName = request.form.get('competition', '')
    clubName = request.form.get('club', '')

    competition = next(
        (c for c in competitions if c['name'] == competitionName),
        None
    )
    club = next(
        (c for c in clubs if c['name'] == clubName),
        None
    )

    if competition is None or club is None:
        flash("Club ou competition introuvable.")
        return redirect(url_for('index'))

    try:
        dateCompetition = datetime.strptime(
            competition['date'], '%Y-%m-%d %H:%M:%S'
        )
    except (KeyError, TypeError, ValueError):
        flash("La date de cette competition est invalide.")
        return redirect(
            url_for('book', competition=competition['name'], club=club['name'])
        )

    if dateCompetition <= datetime.now():
        flash("Impossible de reserver une competition passee.")
        return redirect(
            url_for('book', competition=competition['name'], club=club['name'])
        )

    try:
        placesRequired = int(request.form.get('places', ''))
    except (TypeError, ValueError):
        flash("Veuillez saisir un nombre de places valide.")
        return redirect(
            url_for('book', competition=competition['name'], club=club['name'])
        )

    if placesRequired <= 0:
        flash("Le nombre de places doit etre superieur a zero.")
        return redirect(
            url_for('book', competition=competition['name'], club=club['name'])
        )

    if placesRequired > 12:
        flash("Vous ne pouvez pas reserver plus de 12 places par competition.")
        return redirect(
            url_for('book', competition=competition['name'], club=club['name'])
        )

    if int(club['points']) < placesRequired:
        flash("Votre club ne possede pas assez de points.")
        return redirect(
            url_for('book', competition=competition['name'], club=club['name'])
        )

    if int(competition['numberOfPlaces']) < placesRequired:
        flash("Il ne reste pas assez de places pour cette competition.")
        return redirect(
            url_for('book', competition=competition['name'], club=club['name'])
        )

    # Mettre a jour les places et les points uniquement si la reservation est valide.
    competition['numberOfPlaces'] = (
        int(competition['numberOfPlaces']) - placesRequired
    )
    club['points'] = int(club['points']) - placesRequired

    flash("Reservation effectuee avec succes !")
    return render_template(
        'welcome.html',
        club=club,
        competitions=competitions
    )


# TODO: Ajouter la route d'affichage du classement des points


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
