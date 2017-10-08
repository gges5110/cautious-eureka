from app import db

class Deck(db.Model):
    __tablename__ = 'deck_table'

    id = db.Column(db.Integer, primary_key=True)
    deck_name = db.Column(db.String(), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user_table.id'), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'deck_name': self.deck_name,
            'owner_id': self.owner_id
        }

class User(db.Model):
    __tablename__ = 'user_table'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(), nullable=False)

class Card(db.Model):
    __tablename__ = 'card_table'

    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck_table.id'), nullable=False)


