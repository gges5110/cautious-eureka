from app import db

class Deck(db.Model):
    __tablename__ = 'deck_table'

    id = db.Column(db.Integer, primary_key=True)
    deck_name = db.Column(db.String(), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user_table.id'), nullable=False)

class User(db.Model):
    __tablename__ = 'user_table'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(), nullable=False)
