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

club_reservations = {club['name']: {} for club in clubs}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form['email']
    
    # Vérifier si l'email correspond à un club existant
    club = next((club for club in clubs if club['email'] == email), None)
    
    if club:
        # Si l'e-mail est correct, afficher la page de bienvenue
        return render_template('welcome.html', club=club)
    else:
        # Si l'e-mail n'est pas trouvé, afficher un message d'erreur et rester sur la même page
        flash("Erreur : Email non trouvé. Veuillez réessayer.")
        return redirect(url_for('index'))

@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if foundClub and foundCompetition:
        return render_template('booking.html', club=foundClub, competition=foundCompetition)
    else:
        flash("Something went wrong-please try again.")
        return redirect(url_for('showSummary'))


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)

    try:
        placesRequired = int(request.form['places'])
    except ValueError:
        flash("Invalid number of places requested.")
        return redirect(url_for('book', competition=competition['name'], club=club['name']))

    if not competition or not club:
        flash("Erreur lors de la réservation, veuillez réessayer.")
        return redirect(url_for('index'))

    if placesRequired <= 0:
        flash("Erreur : Le nombre de places doit être supérieur à 0.")
        return render_template('booking.html', club=club, competition=competition)

    # Get the total number of places the club has reserved for all competitions
    total_reserved = sum(club_reservations[club['name']].values())

    # Check if the total number of reserved places will exceed 25
    if total_reserved + placesRequired > 25:
        flash(f"Erreur : Vous ne pouvez pas réserver plus de 25 places au total. "
              f"Vous avez déjà réservé {total_reserved} places.")
        return render_template('booking.html', club=club, competition=competition)

    if placesRequired > 12:
        flash("Erreur : Vous ne pouvez pas réserver plus de 12 places à la fois.")
        return render_template('booking.html', club=club, competition=competition)

    if placesRequired > int(competition['numberOfPlaces']):
        flash(f"Erreur : Il n'y a pas assez de places disponibles pour la compétition {competition['name']}.")
        return render_template('booking.html', club=club, competition=competition)

    if placesRequired > int(club['points']):
        flash(f"Erreur : Vous n'avez pas assez de points. Points disponibles : {club['points']}.")
        return render_template('booking.html', club=club, competition=competition)

    # Deduct the number of places and points, ensuring no negative values
    if int(competition['numberOfPlaces']) - placesRequired < 0 or int(club['points']) - placesRequired < 0:
        flash("Erreur : Cette opération entraînerait des valeurs négatives.")
        return render_template('booking.html', club=club, competition=competition)

    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
    club['points'] = int(club['points']) - placesRequired

    # Update the number of places the club has reserved for this competition
    if competition['name'] in club_reservations[club['name']]:
        club_reservations[club['name']][competition['name']] += placesRequired
    else:
        club_reservations[club['name']][competition['name']] = placesRequired

    flash('Réservation réussie ! Vous avez utilisé {} points pour {} places.'.format(placesRequired, placesRequired))
    return render_template('welcome.html', club=club, competitions=competitions)



# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__== "__main__":
    app.run()        