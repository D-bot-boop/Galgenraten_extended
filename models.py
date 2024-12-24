from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

# Datenbankinitialisierung
db = SQLAlchemy()
bcrypt = Bcrypt()

# Datenbankmodelle
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    #email = db.Column(db.String(150), nullable=True, unique=True)
    password = db.Column(db.String(200), nullable=False)
    mmr = db.Column(db.Integer, default=0)
    rank = db.Column(db.String(50), default='Bronze')

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word = db.Column(db.String(50), nullable=False)
    mistake_count = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
