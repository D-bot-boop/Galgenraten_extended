from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

# Datenbankinitialisierung
db = SQLAlchemy()
bcrypt = Bcrypt()

# Datenbankmodelle
class User(db.Model, UserMixin):
    """
    Repräsentiert einen registrierten Benutzer in der Anwendung.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    # Benutzerstatistiken
    mmr = db.Column(db.Integer, default=0)
    rank = db.Column(db.String(50), default='Bronze')
    coins = db.Column(db.Float, default=0.0)
    winstreak = db.Column(db.Integer, default=0)
    highscore = db.Column(db.Integer, default=0)

    # Beziehung zu GameState
    games = db.relationship('GameState', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class GameState(db.Model):
    """
    Repräsentiert den Zustand eines laufenden oder beendeten Spiels.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Spielbezogene Felder
    current_word = db.Column(db.String(50), nullable=False)  # Das zu erratende Wort
    display_word = db.Column(db.String(50), nullable=False)  # Das aktuelle Fortschrittswort (_ _ _ _)
    mistake_count = db.Column(db.Integer, default=0)  # Anzahl der Fehler
    wrong_letters = db.Column(db.String(255), nullable=True)  # Falsche Buchstaben (CSV-String)
    difficulty = db.Column(db.Float, default=0.0)  # Schwierigkeitsgrad des aktuellen Spiels

    # Status des Spiels
    completed = db.Column(db.Boolean, default=False)  # Ob das Spiel abgeschlossen ist
    coins = db.Column(db.Float, default=0.0)  # Münzen, die im Spiel gesammelt wurden

    def __repr__(self):
        return f'<GameState for User {self.user_id}, Word: {self.current_word}>'
