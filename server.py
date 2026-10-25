import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

# R?servations cumul?es par club et comp?tition.
reservations = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email', '').strip()

    club = next(
        (club for club in clubs if club['email'] == email),
        None
    )

    if club is None:
        flash("Adresse e-mail inconnue. Veuillez r\u00e9essayer.")
        return redirect(url_for('index'))

    return render_template(
        'welcome.html',
        club=club,
        competitions=competitions
    )

@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next(
        (c for c in competitions if c['name'] == request.form.get('competition')),
        None
    )
    club = next(
        (c for c in clubs if c['name'] == request.form.get('club')),
        None
    )

    if competition is None or club is None:
        flash("Club ou comp?tition introuvable.")
        return redirect(url_for('index'))

    booking_url = url_for(
        'book', competition=competition['name'], club=club['name']
    )

    try:
        placesRequired = int(request.form.get('places', ''))
        placesAvailable = int(competition['numberOfPlaces'])
        pointsAvailable = int(club['points'])
    except (TypeError, ValueError, KeyError):
        flash("Donn?es de r?servation invalides.")
        return redirect(booking_url)

    if placesRequired <= 0:
        flash("Le nombre de places doit ?tre sup?rieur ? z?ro.")
        return redirect(booking_url)

    reservationKey = (club['name'], competition['name'])
    placesAlreadyReserved = reservations.get(reservationKey, 0)

    if placesAlreadyReserved + placesRequired > 12:
        flash("Vous ne pouvez pas r?server plus de 12 places par comp?tition.")
        return redirect(booking_url)

    if placesRequired > placesAvailable:
        flash("Il n'y a pas assez de places disponibles.")
        return redirect(booking_url)

    if placesRequired > pointsAvailable:
        flash("Votre club n'a pas assez de points.")
        return redirect(booking_url)

    competition['numberOfPlaces'] = placesAvailable - placesRequired
    club['points'] = pointsAvailable - placesRequired
    reservations[reservationKey] = placesAlreadyReserved + placesRequired

    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
