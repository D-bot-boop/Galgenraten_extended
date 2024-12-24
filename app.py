from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_migrate import Migrate  
from models import *#db, bcrypt, User, Game
import random
import os

# Flask-Initialisierung
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'  # Lokale DB für Tests
app.config['SECRET_KEY'] = 'your_secret_key'

# Erweiterungen initialisieren
db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Globale Variablen für Spielzustand
words = []
current_word = ""
display_word = []
wrong_letters = []
mistake_count = 0

# Datenpfade für lokale Dateien
exe_path = os.path.dirname(os.path.abspath(__file__))
words_file = os.path.join(exe_path, "words_Deutsch.txt")

# Helper-Funktionen
def load_words():
    try:
        with open(words_file, "r", encoding="utf-8") as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        return []

def filter_words(filename):
    """
    Filtert Wörter aus einer Datei, die mindestens 4 Zeichen lang sind.
    """
    filtered_words = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                word_group = line.strip()
                if len(word_group) >= 4:
                    filtered_words.append(word_group)
    except FileNotFoundError:
        pass  # Datei nicht gefunden, leere Liste zurückgeben
    return filtered_words

def choose_random_word():
    global current_word, display_word, mistake_count, wrong_letters
    current_word = random.choice(words)
    display_word = ["_" for _ in current_word]
    mistake_count = 0
    wrong_letters = []

def guess_letter(letter):
    global mistake_count, display_word, wrong_letters
    if letter in current_word:
        for i, char in enumerate(current_word):
            if char == letter:
                display_word[i] = letter
        return True
    else:
        if letter not in wrong_letters:
            wrong_letters.append(letter)
            mistake_count += 1
        return False

# Routen
@app.route('/')
def index():
    leaderboard = User.query.order_by(User.mmr.desc()).limit(10).all()
    player_stats = {
        "name": current_user.username if current_user.is_authenticated else "Gast",
        "mmr": current_user.mmr if current_user.is_authenticated else 0,
        "rank": current_user.rank if current_user.is_authenticated else "Unranked"
    }
    return render_template('index.html', leaderboard=leaderboard, player_stats=player_stats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']  # Benutzername aus dem Formular
        password = request.form['password']  # Passwort aus dem Formular

        # Passwort-Hash generieren
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Neuen Benutzer erstellen und in die Datenbank speichern
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('Account erstellt! Sie können sich jetzt einloggen.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Falls der Benutzer schon eingeloggt ist, weiter zur Startseite

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Benutzer anhand des Usernamens finden
        user = User.query.filter_by(username=username).first()
        
        # Überprüfen, ob der Benutzer existiert und das Passwort korrekt ist
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login erfolgreich!', 'success')
            return redirect(url_for('index'))  # Weiterleitung zur Startseite oder Dashboard
        else:
            flash('Falsches Passwort oder Benutzername', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sie haben sich abgemeldet.', 'info')
    return redirect(url_for('login'))

@app.route('/leaderboard')
def leaderboard():
    top_players = User.query.order_by(User.mmr.desc()).limit(10).all()
    return render_template('leaderboard.html', players=top_players)

@app.route('/game')
@login_required
def game():
    return render_template('game.html')

@app.route('/start_game', methods=['POST'])
@login_required
def start_game():
    global words
    result = choose_random_word(words)
    if not result:
        return jsonify({"error": "Keine Wörter verfügbar"}), 400

    # Initialisiere den globalen Spielstatus
    current_word = result["current_word"]
    display_word = result["display_word"]
    mistake_count = result["mistake_count"]
    wrong_letters = result["wrong_letters"]

    return jsonify({
        "word": " ".join(display_word),
        "wrong_letters": wrong_letters,
        "mistake_count": mistake_count
    })

@app.route('/guess_letter', methods=['POST'])
@login_required
def handle_guess():
    letter = request.json.get("letter")
    if not letter or len(letter) != 1:
        return jsonify({"error": "Ungültiger Buchstabe."}), 400

    result = guess_letter(letter)
    return jsonify({
        "word": " ".join(display_word),
        "wrong_letters": wrong_letters,
        "mistake_count": mistake_count,
        "success": result
    })

@app.route('/game_state', methods=['GET'])
@login_required
def game_state():
    return jsonify({
        "word_display": " ".join(display_word),
        "wrong_letters": wrong_letters,
        "mistake_count": mistake_count,
        "mmr": current_user.mmr,
        "rank": current_user.rank
    })

# Hauptfunktion
if __name__ == '__main__':
    words = load_words()
    app.run(debug=True)
