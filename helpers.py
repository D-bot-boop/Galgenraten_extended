import os
import random
import math
from models import *
exe_path = os.path.dirname(os.path.abspath(__file__))
words_file = os.path.join(exe_path, "words_Deutsch.txt")

def load_words(filepath):
    """
    Lädt Wörter aus der angegebenen Datei.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
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

def choose_random_word(user_id, words, language="Deutsch"):
    """
    Wählt ein zufälliges Wort aus der Liste, initialisiert den Spielstatus und speichert ihn in der Datenbank.
    """
    if not words:
        return None

    # Filtere Wörter mit mindestens 4 Buchstaben
    filtered_words = [word for word in words if len(word) >= 4]
    if not filtered_words:
        return None  # Kein gültiges Wort gefunden

    # Zufälliges Wort auswählen
    current_word = random.choice(words)
    display_word = ["_" if char != "-" else "-" for char in current_word]
    mistake_count = 0
    wrong_letters = []
    difficulty = calculate_word_difficulty(current_word)

    # Spielstatus speichern
    game_state = GameState(
        user_id=user_id,
        current_word=current_word,
        display_word="".join(display_word),
        mistake_count=mistake_count,
        wrong_letters="",
        difficulty=difficulty,
        completed=False
    )
    db.session.add(game_state)
    db.session.commit()

    return game_state




def guess_letter(user_id, letter):
    """
    Prüft einen geratenen Buchstaben und aktualisiert den Spielstatus in der Datenbank.
    """
    game_state = GameState.query.filter_by(user_id=user_id).first()
    if not game_state:
        return {"error": "Kein aktives Spiel gefunden"}, 404

    current_word = game_state.current_word
    display_word = list(game_state.display_word)
    wrong_letters = game_state.wrong_letters.split(",") if game_state.wrong_letters else []
    mistake_count = game_state.mistake_count

    if letter in current_word:
        for i, char in enumerate(current_word):
            if char == letter:
                display_word[i] = letter
    else:
        if letter not in wrong_letters:
            wrong_letters.append(letter)
            mistake_count += 1

    # Aktualisiere den Spielstatus
    game_state.display_word = "".join(display_word)
    game_state.wrong_letters = ",".join(wrong_letters)
    game_state.mistake_count = mistake_count
    db.session.commit()

    return {
        "word": " ".join(display_word),
        "mistake_count": mistake_count,
        "wrong_letters": wrong_letters
    }

def calculate_word_difficulty(word, language="Deutsch"):
    """
    Berechnet die Schwierigkeit eines Wortes basierend auf seinen Buchstaben.
    """
    if language == "Deutsch":
        easy_letters = {'a', 'e', 'i', 'u', 's', 'r', 't', 'n', 'l', 'h', 'g'}
        medium_letters = {'m', 'k', 'b', 'f', 'c', 'o', 'w', 'd'}
        hard_letters = {'y', 'x', 'q', 'v', 'j', 'ü', 'ö', 'ß', 'ä', 'p', 'z'}
    else:
        # Fallback zu Standardbuchstaben
        easy_letters = {'a', 'e', 'i', 'u', 's', 'r', 't', 'n', 'l', 'h', 'g'}
        medium_letters = {'m', 'k', 'b', 'f', 'c', 'o', 'w', 'd'}
        hard_letters = {'y', 'x', 'q', 'v', 'j', 'ü', 'ö', 'ß', 'ä', 'p', 'z'}

    medium_count = sum(1 for char in word.lower() if char in medium_letters)
    hard_count = sum(1 for char in word.lower() if char in hard_letters)
    total_letters = len(word)

    difficulty = 0
    for char in word.lower():
        if char in hard_letters:
            difficulty += 3
        elif char in medium_letters:
            difficulty += 2
        elif char in easy_letters:
            difficulty += 1
        else:
            difficulty += 1

    difficulty_per_letter = difficulty / total_letters
    return difficulty_per_letter

def convert_to_stars(difficulty_per_letter):
    """
    Konvertiert die Schwierigkeit eines Buchstabens in eine Sternebewertung.
    """
    if difficulty_per_letter >= 1.55:
        return "★★★★★"
    elif difficulty_per_letter <= 1.2:
        return "★☆☆☆☆"
    elif difficulty_per_letter <= 1.3:
        return "★★☆☆☆"
    elif difficulty_per_letter <= 1.4:
        return "★★★☆☆"
    else:
        return "★★★★☆"

def calculate_letter_difficulty(letter, language="Deutsch"):
    """
    Berechnet die Schwierigkeit eines Buchstabens basierend auf seiner Sprache und Häufigkeit.
    """
    if language == "Deutsch":
        easy_letters = {'a', 'e', 'i', 'u', 's', 'r', 't', 'n', 'l', 'h', 'g'}
        medium_letters = {'m', 'k', 'b', 'f', 'c', 'o', 'w', 'd'}
        hard_letters = {'y', 'x', 'q', 'v', 'j', 'ü', 'ö', 'ß', 'ä', 'p', 'z'}
    elif language == "Englisch":
        easy_letters = {'a', 'e', 'i', 'r', 'n', 'l', 'b', 'd', 'o'}
        medium_letters = {'m', 't', 's', 'y', 'g', 'u', 'v', 'h'}
        hard_letters = {'x', 'q', 'j', 'p', 'z', 'c', 'k', 'w', 'f'}
    elif language == "Französisch":
        easy_letters = {'e', 's', 'a', 'i', 't', 'n', 'r', 'u', 'l'}
        medium_letters = {'o', 'd', 'c', 'p', 'm', 'v', 'q', 'f'}
        hard_letters = {'é', 'b', 'g', 'h', 'j', 'à', 'x', 'y', 'w', 'k', 'z'}
    elif language == "Spanisch":
        easy_letters = {'e', 'a', 'o', 's', 'r', 'n', 'i', 'd', 'l'}
        medium_letters = {'c', 't', 'u', 'm', 'p', 'b', 'g'}
        hard_letters = {'v', 'y', 'q', 'h', 'f', 'z', 'j', 'x', 'w'}
    else:
        easy_letters = {'a', 'e', 'i', 'u', 's', 'r', 't', 'n', 'l', 'h', 'g'}
        medium_letters = {'m', 'k', 'b', 'f', 'c', 'o', 'w', 'd'}
        hard_letters = {'y', 'x', 'q', 'v', 'j', 'ü', 'ö', 'ß', 'ä', 'p', 'z'}

    if letter in hard_letters:
        return 3
    elif letter in medium_letters:
        return 2
    elif letter in easy_letters:
        return 1
    else:
        return 1
    
def load_words(language="Deutsch"):
    """
    Lädt Wörter aus der Datei basierend auf der Sprache.
    """
    filename = os.path.join("static", "words", f"words_{language}.txt")
    try:
        with open(filename, "r", encoding="utf-8") as file:
            words = file.read().splitlines()
            return [word for word in words if len(word) >= 4]  # Nur Wörter mit mindestens 4 Buchstaben
    except FileNotFoundError:
        print(f"[ERROR] Wörterliste für '{language}' nicht gefunden.")
        return []



def reveal_random_letter(user_id):
    """
    Deckt einen zufälligen Buchstaben im aktuellen Wort auf.
    """
    game_state = GameState.query.filter_by(user_id=user_id, completed=False).first()
    if not game_state:
        return {"error": "Kein aktives Spiel gefunden"}, 404

    display_word = list(game_state.display_word)
    current_word = game_state.current_word

    # Prüfen, ob der Benutzer genügend Münzen hat
    user = User.query.get(user_id)
    if user.coins < 50:
        return {"error": "Nicht genügend Münzen für einen Tipp"}, 400

    # Suche nach unaufgedeckten Buchstaben
    remaining_indices = [i for i, char in enumerate(display_word) if char == "_"]
    if not remaining_indices:
        return {"error": "Alle Buchstaben sind bereits aufgedeckt"}, 400

    # Zufällig einen Buchstaben aufdecken
    random_index = random.choice(remaining_indices)
    letter_to_reveal = current_word[random_index]
    for i, char in enumerate(current_word):
        if char.lower() == letter_to_reveal.lower():  # Groß-/Kleinschreibung beachten
            display_word[i] = current_word[i]  # Behalte die Originalbuchstaben

    # Update Benutzer-Münzen und Spielstatus
    user.coins = round(user.coins - 50, 1)
    game_state.display_word = "".join(display_word)
    
    if "_" not in display_word:
            # Spiel als gewonnen markieren und Logik für Gewinn ausführen
            word_difficulty = calculate_word_difficulty(current_word)
            winstreak_bonus = 1 + (user.winstreak * 0.05 if user.winstreak >= 3 else 0)
            mmr_gain = round((max(20, word_difficulty * 20) * winstreak_bonus) * ((-2 * math.sqrt(abs(user.mmr))) * 0.01 + 1.5))
            coins_earned = round(2 * word_difficulty * winstreak_bonus)

            user.mmr += mmr_gain
            user.winstreak += 1
            user.coins += coins_earned  # Münzen für den Sieg hinzufügen
            game_state.completed = True
            db.session.commit()

            return {
                "message": f"Das Wort '{current_word}' wurde vollständig erraten! Du hast {coins_earned} ◎ verdient!",
                "word": " ".join(display_word),
                "coins": user.coins,
                "mmr": user.mmr,
                "winstreak": user.winstreak,
                "game_over": True  # Spiel ist beendet
            }

        # Normale Rückgabe, wenn das Spiel nicht beendet ist
    db.session.commit()
    return {
            "message": f"Der Buchstabe '{letter_to_reveal}' wurde aufgedeckt!",
            "word": " ".join(display_word),
            "coins": user.coins,
            "game_over": False  # Spiel geht weiter
        }

def update_highscore(user):
    """
    Aktualisiert den Highscore eines Benutzers, falls der aktuelle MMR höher ist.
    """
    if user.mmr > user.highscore:
        user.highscore = user.mmr
        db.session.commit()
    return user.highscore

def update_mmr_change_label(mmr_change):
    """
    Gibt das Label für die MMR-Änderung zurück.
    """
    if mmr_change > 0:
        return f"+{mmr_change} MMR", "green"
    elif mmr_change < 0:
        return f"{mmr_change} MMR", "red"
    else:
        return "0 MMR", "black"

def update_winstreak_label(user):
    """
    Gibt die Winstreak eines Benutzers zurück.
    """
    if user.winstreak > 2:
        return f"Winstreak: {user.winstreak}"
    else:
        return ""

def update_coins_label(user):
    """
    Gibt die Münzen eines Benutzers zurück.
    """
    if user.coins:
        return f"{user.coins} ◎"
    else:
        return "0 ◎"

def define_rank(user):
    """
    Berechnet den Rang eines Benutzers basierend auf seinem MMR und aktualisiert ihn in der Datenbank.
    """
    mmr = user.mmr
    if mmr < 133:
        rank, subdivision, color = "Bronze", "III", "#cd7f32"
    elif mmr < 266:
        rank, subdivision, color = "Bronze", "II", "#cd7f32"
    elif mmr < 400:
        rank, subdivision, color = "Bronze", "I", "#cd7f32"
    elif mmr < 533:
        rank, subdivision, color = "Silber", "III", "#c0c0c0"
    elif mmr < 666:
        rank, subdivision, color = "Silber", "II", "#c0c0c0"
    elif mmr < 800:
        rank, subdivision, color = "Silber", "I", "#c0c0c0"
    elif mmr < 933:
        rank, subdivision, color = "Gold", "III", "#ffd700"
    elif mmr < 1066:
        rank, subdivision, color = "Gold", "II", "#ffd700"
    elif mmr < 1200:
        rank, subdivision, color = "Gold", "I", "#ffd700"
    elif mmr < 1333:
        rank, subdivision, color = "Platin", "III", "#e5e4e2"
    elif mmr < 1466:
        rank, subdivision, color = "Platin", "II", "#e5e4e2"
    elif mmr < 1600:
        rank, subdivision, color = "Platin", "I", "#e5e4e2"
    elif mmr < 1733:
        rank, subdivision, color = "Diamant", "III", "#b9f2ff"
    elif mmr < 1866:
        rank, subdivision, color = "Diamant", "II", "#b9f2ff"
    elif mmr < 2000:
        rank, subdivision, color = "Diamant", "I", "#b9f2ff"
    elif mmr < 2133:
        rank, subdivision, color = "Champion", "III", "#91DFFF"
    elif mmr < 2266:
        rank, subdivision, color = "Champion", "II", "#91DFFF"
    elif mmr < 2400:
        rank, subdivision, color = "Champion", "I", "#91DFFF"
    else:
        rank, subdivision, color = "Grand Champion", "", "#ffdf00"

    user.rank = f"{rank} {subdivision}"
    db.session.commit()
    return user.rank, color


def show_image(mistake_count):
    image_name = f"{mistake_count}.png"
    image_path = os.path.join("static", "images", image_name)

    if os.path.exists(image_path):
        print(f"[DEBUG] Bild gefunden: {image_path}")
        return f"/static/images/{image_name}"
    else:
        print("[DEBUG] Standardbild wird verwendet.")
        return "/static/images/5.png"


def save_mmr(user, new_mmr):
    """
    Speichert den neuen MMR-Wert des Benutzers in der Datenbank.
    """
    user.mmr = new_mmr
    db.session.commit()

def load_mmr(user):
    """
    Lädt den MMR-Wert aus der Datenbank.
    """
    return user.mmr

def save_coins(user, new_coins):
    """
    Speichert die Münzen des Benutzers in der Datenbank.
    """
    user.coins = new_coins
    db.session.commit()

def load_coins(user):
    """
    Lädt die Münzen des Benutzers aus der Datenbank.
    """
    return user.coins

def save_winstreak(user, new_winstreak):
    """
    Speichert die aktuelle Winstreak des Benutzers.
    """
    user.winstreak = new_winstreak
    db.session.commit()

def load_winstreak(user):
    """
    Lädt die aktuelle Winstreak des Benutzers.
    """
    return user.winstreak

def save_highscore(user, new_highscore):
    """
    Speichert den neuen Highscore des Benutzers.
    """
    user.highscore = new_highscore
    db.session.commit()

def load_highscore(user):
    """
    Lädt den Highscore des Benutzers.
    """
    return user.highscore

def update_difficulty_label(difficulty_rating):
    """
    Gibt die Sternebewertung basierend auf dem Schwierigkeitsgrad zurück.
    """
    stars = convert_to_stars(difficulty_rating)
    return {"difficulty": difficulty_rating, "stars": stars}


