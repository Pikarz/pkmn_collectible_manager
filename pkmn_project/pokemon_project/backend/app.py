from flask import jsonify, request
from models import *
from db_init import db, app

from sqlalchemy.orm import joinedload
from flask_cors import cross_origin
import json

from expansions import get_expansions, get_expansion_cards, get_cards_number_by_expansion, get_expansion_completion_percentage
from cardinstance import update_card, add_new_acq_cards, get_my_cards, get_cards_pending, insert_selling_cards, get_cards_pending, get_selling_cards, get_sold, isold
from gradingcompany import get_grad_comps
from version import get_vers
from language import get_lang


@app.route('/api/expansions/', methods=['GET'])
def return_expansions():
    return get_expansions()
    
# TODO: manage graded, signed and factory errors
@app.route('/api/get_collection_cards/', methods=['GET'])
def get_cards_collection_and_percentage():
    try:
        cards_number_by_expansion = get_cards_number_by_expansion(db)
    except Exception as e:
        return jsonify({'error': 'Failed to fetch the number of cards by expansion: ' + str(e)}), 500

    try:
        my_cards = get_my_cards(db)   
    except Exception as e:
        return jsonify({'error': 'Failed to fetch cards in collection: ' + str(e)}), 500
    
    expansion_completion = get_expansion_completion_percentage(cards_number_by_expansion, my_cards)
    return  jsonify({'collection_cards': my_cards, 'expansion_completion': expansion_completion})

@app.route('/api/update-card-instance', methods=['PUT'])
def update_card_instance():
    data = json.loads(request.data)
    card_id = request.args.get('id')
    update_card(db, card_id, data)

@app.route('/api/expansion_cards', methods=['GET'])
def get_exp_cards():
    selected_expansion = request.args.get('expansion')
    return get_expansion_cards(selected_expansion)

@app.route('/api/get_versions', methods=['GET'])
def get_versions():
    expansion = request.args.get('expansion')
    number = request.args.get('number')
    return get_vers(db, expansion, number)

@app.route('/api/get_languages', methods=['GET'])
def get_languages():
    expansion = request.args.get('expansion')
    return get_lang(db, expansion)

@app.route('/api/add_new_acquired_cards', methods=['POST'])
def add_new_acquired_cards():
    data = request.json
    return add_new_acq_cards(db, data)
    
# @app.route('/api/add_new_acquired_card', methods=['POST'])
# @cross_origin()
# def add_new_acquired_card():
#     data = request.json
#     add_new_acquired_card(db, data)

@app.route('/api/get_grading_companies', methods=['GET'])
def get_grading_companies():
    return get_grad_comps(db)

@app.route('/api/get_pending_cards', methods=['GET'])
def get_pending_cards():
    return get_cards_pending(db)

@app.route('/api/sell_cards', methods=['POST'])
def sell_cards():
    cards = request.json.get('selectedCardIds')
    date = request.json.get('sellingDate')
    return insert_selling_cards(db, cards, date)

@app.route('/api/get_selling_cards', methods=['GET'])
def get_sellin_cards():
    return get_selling_cards(db)

@app.route('/api/sold_cards', methods=['POST'])
def dispose_cards():
    cards = request.json.get('selectedCards')
    date = request.json.get('sellingDate')
    buyer = request.json.get('buyer')
    buyer_comment = 'as buyer: ' + str(request.json.get('buyerComment'))
    source = request.json.get('source')
    trans_comment = request.json.get('transComment')
    return isold(db, cards, date, buyer, buyer_comment, source, trans_comment) 

@app.route('/api/last_sold_cards', methods=['GET'])
def get_sold_cards():
    return get_sold(db)

if __name__ == '__main__':
    # DEV SERVER
    app.run(host='192.168.1.58', port=5000, debug=True)

    # PROD SERVER
    # from waitress import serve
    # serve(app, host='192.168.1.58', port=5000)
