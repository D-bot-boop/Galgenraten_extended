from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_migrate import Migrate  
from models import *#db, bcrypt, User, Game
from helpers import load_words, choose_random_word, calculate_word_difficulty, show_image, reveal_random_letter, update_highscore, define_rank, filter_words, calculate_letter_difficulty, convert_to_stars
from flask import session
import math

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
    # Prüfe, ob ein aktives Spiel existiert
    game_state = GameState.query.filter_by(user_id=current_user.id, completed=False).first()
    
    if not game_state:
        # Starte ein neues Spiel, falls keines existiert
        words = load_words("words_Deutsch.txt")
        choose_random_word(current_user.id, words)
    
    return render_template('game.html')


def load_words_for_language(language):
    """
    Lädt Wörter basierend auf der gewählten Sprache aus einer Datei.
    """
    filename = os.path.join("static/words", f"words_{language}.txt")
    return filter_words(filename)

@app.route('/change_language', methods=['POST'])
@login_required
def change_language():
    """
    Ändert die Sprache und lädt neue Wörter in die Session.
    """
    data = request.json
    language = data.get("language", "Deutsch")
    words = load_words_for_language(language)
    session['words'] = words
    session['language'] = language
    return jsonify({"message": f"Sprache geändert zu {language}"})


@app.route('/start_game', methods=['POST'])
@login_required
def start_game():
    existing_game = GameState.query.filter_by(user_id=current_user.id, completed=False).first()
    if existing_game:
        existing_game.completed = True
        db.session.commit()

    words = load_words("words_Deutsch.txt")
    if not words:
        return jsonify({"error": "Keine Wörter verfügbar"}), 400

    game_state = choose_random_word(current_user.id, words)
    difficulty_stars = convert_to_stars(game_state.difficulty)

    return jsonify({
        "word": " ".join(game_state.display_word),
        "difficulty": difficulty_stars,
        "mmr": current_user.mmr,
        "rank": current_user.rank,
        "coins": current_user.coins,  # Coins zurückgeben
        "winstreak": current_user.winstreak
    })


@app.route('/guess_letter', methods=['POST'])
@login_required
def guess_letter():
    data = request.json
    user_input = data.get('letter', '').lower()

    print(f"[DEBUG] Eingegebener Buchstabe: {user_input}")

    if len(user_input) != 1 or not user_input.isalpha():
        return jsonify({"error": "Ungültiger Buchstabe"}), 400

    game_state = GameState.query.filter_by(user_id=current_user.id, completed=False).first()
    if not game_state:
        print("[DEBUG] Kein aktives Spiel gefunden.")
        return jsonify({"error": "Kein aktives Spiel gefunden"}), 404

    current_word = game_state.current_word
    display_word = list(game_state.display_word)
    mistake_count = game_state.mistake_count
    wrong_letters = game_state.wrong_letters.split(",") if game_state.wrong_letters else []
    mmr_change = 0
    difficulty_stars = convert_to_stars(game_state.difficulty)

    print(f"[DEBUG] Aktuelles Wort: {current_word}")
    print(f"[DEBUG] Fehleranzahl: {mistake_count}")
    print(f"[DEBUG] Vorherige MMR: {current_user.mmr}")

    if user_input in display_word or user_input in wrong_letters:
        print(f"[DEBUG] Buchstabe {user_input} wurde bereits geraten.")
        return jsonify({
            "error": "Buchstabe wurde bereits geraten.",
            "wrong_letters": wrong_letters,
            "word_display": " ".join(display_word),
            "mmr": current_user.mmr,
            "difficulty": difficulty_stars
        }), 400

    if user_input in current_word.lower():
        print(f"[DEBUG] Buchstabe {user_input} ist korrekt.")
        
        # Groß- und Kleinschreibung ignorieren
        positions = [i for i, char in enumerate(current_word) if char.lower() == user_input]
        for pos in positions:
            display_word[pos] = current_word[pos]  # Originalbuchstabe übernehmen (Groß-/Kleinschreibung)

        # MMR-Änderung bei Erfolg
        letter_difficulty = calculate_letter_difficulty(user_input, session.get("language", "Deutsch"))
        if len(current_word) >= 19:
            change = round(max(1, 2 * letter_difficulty) * ((-2 * math.sqrt(abs(current_user.mmr))) * 0.01 + 1.5))
        else:
            change = round(max(1, 3 * letter_difficulty) * ((-2 * math.sqrt(abs(current_user.mmr))) * 0.01 + 1.5))
        
        current_user.mmr += change
        mmr_change += change

    else:
        print(f"[DEBUG] Buchstabe {user_input} ist falsch.")
        mistake_count += 1
        wrong_letters.append(user_input)

        letter_difficulty = calculate_letter_difficulty(user_input, session.get("language", "Deutsch"))
        change = max(1, 4 - letter_difficulty)
        current_user.mmr -= change
        mmr_change -= change

    if mistake_count > 7:  # Spiel verloren
        word_difficulty = calculate_word_difficulty(current_word)
        mmr_loss = round(max(20, 60 - 20 * word_difficulty))
        current_user.mmr -= mmr_loss
        current_user.winstreak = 0
        current_user.rank = define_rank(current_user)[0] 
        game_state.completed = True
        game_state.mistake_count = mistake_count
        db.session.commit()

        image_path = show_image(mistake_count)  # Bild für maximale Fehleranzahl

        return jsonify({
            "message": f"Du hast verloren. Das Wort war '{current_word}'.",
            "mmr_change": mmr_change - mmr_loss,
            "mmr": current_user.mmr,
            "rank": current_user.rank,
            "image_path": image_path,  # Bildpfad hinzufügen
            "winstreak": current_user.winstreak,
            "coins": current_user.coins,  # Aktualisierte Münzen zurückgeben
            "difficulty": convert_to_stars(word_difficulty),  # Schwierigkeit hinzufügen
            "game_over": True
        })

    if "_" not in display_word:
        print("[DEBUG] Spiel gewonnen.")
        word_difficulty = calculate_word_difficulty(current_word)
        winstreak_bonus = 1 + 0.05 * current_user.winstreak if current_user.winstreak >= 3 else 1
        error_penalty = max(1, (7 - mistake_count))
        coins_earned = round(2 * word_difficulty * winstreak_bonus * error_penalty)
        mmr_gain = round((max(20, word_difficulty * 20) * winstreak_bonus))
        current_user.mmr += mmr_gain
        current_user.winstreak += 1
        current_user.coins += coins_earned
        current_user.rank = define_rank(current_user)[0] 
        game_state.completed = True
        game_state.display_word = current_word
        game_state.mistake_count = mistake_count
        db.session.commit()

        image_path = show_image(mistake_count)

        return jsonify({
        "message": f"Glückwunsch! Du hast das Wort '{current_word}' erraten.",
        "word_display": " ".join(list(current_word)),
        "mmr_change": mmr_change + mmr_gain,
        "mmr": current_user.mmr,
        "rank": current_user.rank,
        "image_path": image_path,  # Bild bleibt gleich
        "winstreak": current_user.winstreak,
        "coins": current_user.coins,  # Münzen zurückgeben
        "coins_earned": coins_earned,
        "difficulty": difficulty_stars,  # Schwierigkeit immer zurückgeben
        "game_over": True
        })

    game_state.display_word = "".join(display_word)
    game_state.mistake_count = mistake_count
    game_state.wrong_letters = ",".join(wrong_letters)
    db.session.commit()

    image_path = show_image(mistake_count)
    #difficulty_stars = convert_to_stars(game_state.difficulty)

    print(f"[DEBUG] Neue MMR: {current_user.mmr}")
    return jsonify({
        "word_display": " ".join(display_word),
        "wrong_letters": wrong_letters,
        "mistake_count": mistake_count,
        "image_path": image_path,
        "mmr": current_user.mmr,
        "rank": current_user.rank,
        "mmr_change": mmr_change,
        "message": "Weiter raten!",
        "difficulty": difficulty_stars
    })


@app.route('/reveal_letter', methods=['POST'])
@login_required
def reveal_letter():
    result = reveal_random_letter(current_user.id)
    if "error" in result:
        return jsonify({"error": result["error"]}), 400
    return jsonify(result)



@app.route('/game_state', methods=['GET'])
@login_required
def game_state():
    game_state = GameState.query.filter_by(user_id=current_user.id, completed=False).first()
    if not game_state:
        print("[DEBUG] Kein aktives Spiel gefunden.")
        return jsonify({"error": "Kein aktives Spiel gefunden"}), 404

    # Bildpfad generieren
    image_path = show_image(game_state.mistake_count)
    print(f"[DEBUG] Fehleranzahl: {game_state.mistake_count}")
    print(f"[DEBUG] Bildpfad: {image_path}")

    # Daten zurückgeben
    return jsonify({
        "word_display": " ".join(game_state.display_word),
        "wrong_letters": game_state.wrong_letters.split(",") if game_state.wrong_letters else [],
        "mistake_count": game_state.mistake_count,
        "image_path": image_path,
        "mmr": current_user.mmr,
        "rank": current_user.rank,
        "winstreak": current_user.winstreak,
    })



@app.route('/letter_difficulty', methods=['POST'])
@login_required
def letter_difficulty():
    """
    Berechnet die Schwierigkeit eines Buchstabens und gibt die Sternebewertung zurück.
    """
    data = request.json
    letter = data.get("letter", "").lower()
    language = session.get("language", "Deutsch")

    if len(letter) != 1 or not letter.isalpha():
        return jsonify({"error": "Ungültiger Buchstabe"}), 400

    difficulty = calculate_letter_difficulty(letter, language)
    stars = convert_to_stars(difficulty)
    
    return jsonify({"difficulty": difficulty, "stars": stars})

@app.route('/highscore', methods=['GET'])
@login_required
def highscore():
    highscore = update_highscore(current_user)
    return jsonify({"highscore": highscore})

@app.route('/rank', methods=['GET'])
@login_required
def rank():
    rank, color = define_rank(current_user)
    return jsonify({"rank": rank, "color": color})

@app.route('/reset-game-data', methods=['GET'])
@login_required
def reset_game_data():
    # Zeigt die Bestätigungsseite an
    return render_template('reset_confirm.html')


@app.route('/reset-game-data-confirm', methods=['POST'])
@login_required
def reset_game_data_confirm():
    # Spielstand zurücksetzen
    GameState.query.filter_by(user_id=current_user.id).delete()
    current_user.mmr = 0
    current_user.coins = 0
    current_user.winstreak = 0
    current_user.highscore = 0
    db.session.commit()

    return render_template('reset_success.html')

@app.route('/leaderboard/json')
def leaderboard_json():
    top_players = User.query.order_by(User.mmr.desc()).limit(10).all()
    players = [
        {"username": player.username, "mmr": player.mmr, "rank": player.rank}
        for player in top_players
    ]
    return jsonify(players)



# Hauptfunktion
if __name__ == '__main__':
    words = load_words("words_Deutsch.txt")
    app.run(debug=True)
