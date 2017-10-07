from flask import Blueprint, session, request, jsonify

api = Blueprint('api', __name__)
from models import *
@api.route('/create_deck', methods=['POST'])
def create_deck_function():
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
    return "New deck created."

@api.route('/get_all_decks', methods=['GET'])
def get_all_decks():
    # Check if user has logged in.
    if 'email' not in session:
        return "Please login first!"

    # Get all decks from this user
    user = User.query.filter_by(user_email=session['email']).first()
    decks = Deck.query.filter_by(owner_id=user.id).all()
    # json_list = [i.serialize for i in qryresult.all()]
    return jsonify(json_list=[i.serialize for i in decks])
