from flask import Flask, render_template, request, jsonify
import random

from dotenv import load_dotenv
import os

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy


# Flask-Initialisierung
app = Flask(__name__)

# Globale Variablen
mmr_points = 0
coins = 0
winstreak = 0
highscore = 0
rank = "Bronze"
words = []
current_word = ""
wrong_letters = []
display_word = []
mistake_count = 0

# Datenpfade
exe_path = os.path.dirname(os.path.abspath(__file__))
mmr_file = os.path.join(exe_path, "mmr.txt")
winstreak_file = os.path.join(exe_path, "winstreak.txt")
highscore_file = os.path.join(exe_path, "highscore.txt")
coins_file = os.path.join(exe_path, "coins.txt")
words_file = os.path.join(exe_path, "words_Deutsch.txt")

# Helper-Funktionen
def load_words():
    try:
        with open(words_file, "r", encoding="utf-8") as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        return []

def save_value(file_path, value):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(str(value))

def load_value(file_path, default=0):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return default

# Spiel-Logik
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

# Flask-Routen
@app.route('/')
def index():
    leaderboard = User.query.order_by(User.mmr.desc()).limit(10).all()
    player_stats = {
        "name": current_user.username if current_user.is_authenticated else "Gast",
        "mmr": current_user.mmr if current_user.is_authenticated else 0,
        "rank": current_user.rank if current_user.is_authenticated else "Unranked"
    }
    return render_template('index.html', leaderboard=leaderboard, player_stats=player_stats)


@app.route('/game')
@login_required
def game():
    return render_template('game.html')

@app.route('/start_game', methods=['POST'])
@login_required
def start_game():
    choose_random_word()
    return jsonify({
        "word": " ".join(display_word),
        "wrong_letters": wrong_letters,
        "mistake_count": mistake_count
    })


@app.route('/guess_letter', methods=['POST'])
def handle_guess():
    letter = request.json.get("letter")
    if not letter or len(letter) != 1:
        return jsonify({"error": "Ungültiger Buchstabe."}), 400

    result = guess_letter(letter)
    return jsonify({
        "word_display": " ".join(display_word),
        "wrong_letters": wrong_letters,
        "mistake_count": mistake_count,
        "success": result
    })

@app.route('/save_game', methods=['POST'])
def save_game():
    save_value(mmr_file, mmr_points)
    save_value(winstreak_file, winstreak)
    save_value(highscore_file, highscore)
    save_value(coins_file, coins)
    return jsonify({"status": "Spiel gespeichert"})

@app.route('/reset_game', methods=['POST'])
def reset_game():
    global mmr_points, winstreak, highscore, coins
    mmr_points = 0
    winstreak = 0
    highscore = 0
    coins = 0
    save_game()
    return jsonify({"status": "Spiel zurückgesetzt"})

if __name__ == '__main__':
    words = load_words()
    mmr_points = load_value(mmr_file)
    winstreak = load_value(winstreak_file)
    highscore = load_value(highscore_file)
    coins = load_value(coins_file)
    app.run(debug=True)
