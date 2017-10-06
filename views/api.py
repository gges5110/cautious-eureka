from flask import Blueprint, session, request

api = Blueprint('api', __name__)
from models import *
@api.route('/create_deck', methods=['POST'])
def create_table_function():
    # Check if user has logged in.
    if 'email' not in session:
        return "Please login first!"

    # Check create deck params
    if not request.is_json:
        return "Please send data in json format."

    content = request.get_json()
    if 'deck_name' not in content:
        return "Missing params: deck_name"

    # TODO: Check if a deck with the same name has already existed before creating a new one.

    # Create new deck
    user = User.query.filter_by(user_email=session['email']).first()
    new_deck = Deck(deck_name=content['deck_name'], owner_id=user.id)
    db.session.add(new_deck)
    db.session.commit()
    return "haha"
