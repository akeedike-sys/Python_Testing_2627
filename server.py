
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs():
    with open('clubs.json', encoding='utf-8') as c:
        return json.load(c)['clubs']


def loadCompetitions():
    with open('competitions.json', encoding='utf-8') as comps:
        return json.load(comps)['competitions']


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
        (
            club for club in clubs
            if club['email'].strip().lower() == email.lower()
        ),
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
    found_club = next(
        (c for c in clubs if c['name'] == club),
        None
    )
    found_competition = next(
        (c for c in competitions if c['name'] == competition),
        None
    )

    if found_club is None or found_competition is None:
        flash("Club ou competition introuvable.")
        return redirect(url_for('index'))

    return render_template(
        'booking.html',
        club=found_club,
        competition=found_competition
    )


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition_name = request.form.get('competition', '')
    club_name = request.form.get('club', '')

    competition = next(
        (c for c in competitions if c['name'] == competition_name),
        None
    )
    club = next(
        (c for c in clubs if c['name'] == club_name),
        None
    )

    if competition is None or club is None:
        flash("Club ou competition introuvable.")
        return redirect(url_for('index'))

    try:
        date_competition = datetime.strptime(
            competition['date'], '%Y-%m-%d %H:%M:%S'
        )
    except (KeyError, TypeError, ValueError):
        flash("La date de cette competition est invalide.")
        return redirect(
            url_for(
                'book',
                competition=competition['name'],
                club=club['name']
            )
        )

    if date_competition <= datetime.now():
        flash("Impossible de reserver une competition passee.")
        return redirect(
            url_for(
                'book',
                competition=competition['name'],
                club=club['name']
            )
        )

    try:
        places_required = int(request.form.get('places', ''))
    except (TypeError, ValueError):
        flash("Veuillez saisir un nombre de places valide.")
        return redirect(
            url_for(
                'book',
                competition=competition['name'],
                club=club['name']
            )
        )

    if places_required <= 0:
        flash("Le nombre de places doit etre superieur a zero.")
        return redirect(
            url_for(
                'book',
                competition=competition['name'],
                club=club['name']
            )
        )

    if places_required > 12:
        flash("Vous ne pouvez pas reserver plus de 12 places par competition.")
        return redirect(
            url_for(
                'book',
                competition=competition['name'],
                club=club['name']
            )
        )

    if int(club['points']) < places_required:
        flash("Votre club ne possede pas assez de points.")
        return redirect(
            url_for(
                'book',
                competition=competition['name'],
                club=club['name']
            )
        )

    if int(competition['numberOfPlaces']) < places_required:
        flash("Il ne reste pas assez de places pour cette competition.")
        return redirect(
            url_for(
                'book',
                competition=competition['name'],
                club=club['name']
            )
        )

    # Modifier les soldes uniquement si la reservation est valide.
    competition['numberOfPlaces'] = (
        int(competition['numberOfPlaces']) - places_required
    )
    club['points'] = int(club['points']) - places_required

    flash("Reservation effectuee avec succes !")

    return render_template(
        'welcome.html',
        club=club,
        competitions=[
            comp for comp in competitions
            if datetime.strptime(
                comp['date'], '%Y-%m-%d %H:%M:%S'
            ) > datetime.now()
        ]
    )


@app.route('/points')
def points():
    # Classement public en lecture seule.
    classement = sorted(
        clubs,
        key=lambda club: int(club['points']),
        reverse=True
    )

    return render_template('points.html', clubs=classement)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
