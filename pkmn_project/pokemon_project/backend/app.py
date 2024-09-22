from flask import jsonify, request
from models import *
from db_init import db, app

from sqlalchemy.orm import joinedload
from flask_cors import cross_origin
import json

from cardtype import filtered_cards
from expansions import get_expansions, get_expansion_percentage, all_expansions, min_allowed_date
from cardinstance import update_card, add_new_acq_cards, itrade_away, delete_card_instance, get_my_cardinstances, get_cards_pending_or_sold, insert_selling_cards, get_sold, isold
from gradingcompany import get_grad_comps
from version import get_vers, cards_versions
from language import get_lang, cards_languages
from rarity import rarities
from transactions import get_exp_transactions, update_transaction_comment, delete_transaction, get_transactions_info, get_bought_sold_stats_per_time, get_sold_per_bought_date_earnings
from counterparty import counterparties, counterparty, update_counterparty
from source import sources
from factoryerror import factory_errors
from sellingcollectable import delete_selling

@app.route('/api/expansions/', methods=['GET'])
def return_expansions():
    is_japanese_str = request.args.get('isJapanese')
    is_japanese = is_japanese_str.lower() == 'true' if is_japanese_str is not None else False
    return get_expansions(is_japanese)
    
# returns a dictionary of dictionaries that maps teh state (in collection, to be sold cards) to the expansion, number of owned cards, number of total cards of that expansion, percentage of completion
@app.route('/api/get_percentage_per_expansion/', methods=['GET'])
def get_cards_collection_and_percentage():
    try:
        #cards_number_by_expansion = get_cards_number_by_expansion(db)
        percentage_per_expansion = get_expansion_percentage(db)
        return jsonify(percentage_per_expansion)
    except Exception as e:
        return jsonify({'error': 'Failed to fetch the number of cards by expansion: ' + str(e)}), 500


@app.route('/api/update-card-instance', methods=['PUT'])
def update_card_instance():
    data = json.loads(request.data)
    card_id = request.args.get('id')
    return update_card(db, card_id, data)

@app.route('/api/get_cardinstances')
def card_instances():
    expansion = request.args.get('expansion')
    number = request.args.get('number')
    expansion_number_map = [{'number': number, 'expansion': expansion}]
    return get_my_cardinstances(db, expansion_number_map)

# deprecated to make the queries lighter. now a cardinstance is retrieved only when requested 
# and to each cardtype corresponds two booleans: in_collection, owned
# @app.route('/api/get_my_cards', methods=['GET'])
# def get_my_cards():
#     page = request.args.get('page', default=1, type=int)
#     per_page = request.args.get('per_page', default=100, type=int)

#     generations = request.args.get('generations').split(',') if request.args.get('generations') else []
#     expansions = request.args.get('expansions').split(',') if  request.args.get('expansions') else []
#     start_date = request.args.get('startDate') 
#     end_date = request.args.get('endDate')
#     card_name = request.args.get('cardName')
#     rarity = request.args.get('rarity')

#     try:
#         return jsonify(my_cards = my_cards(db, page, per_page, generations, expansions, start_date, end_date, card_name, rarity))
#     except Exception as e:
#         return jsonify({'error': 'Failed to fetch cards in collection: ' + str(e)}), 500
    

@app.route('/api/filtered_cards', methods=['GET'])
def get_filtered_cards():
    generations = request.args.get('generations').split(',') if request.args.get('generations') else []
    expansions = request.args.get('expansions').split(',') if  request.args.get('expansions') else []
    start_date = request.args.get('startDate') 
    end_date = request.args.get('endDate')
    card_name = request.args.get('cardName')
    rarity = request.args.get('rarity')
    owned_only = request.args.get('ownedOnly')
    page = request.args.get('currentPage', type=int)
    per_page = request.args.get('itemsPerPage', type=int)
    get_my_data = request.args.get('getMyData', type=bool)

    return filtered_cards(db, get_my_data, generations, expansions, start_date, end_date, card_name, rarity, owned_only, page, per_page)

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
    acquired_date = data.get('acquiredDate') 
    seller = data.get('seller')             
    source = data.get('source')
    trans_comment = data.get('transComment')
    seller_comment = data.get('sellerComment')
    seller_comment = 'as buyer: '+seller_comment if len(seller_comment)>0 else ''
    new_cards = data.get('cardsData')
    shipping_cost = data.get('shippingcost')

    tax_cost = data.get('taxcost')
    is_a_transaction = data.get('isATransaction')

    message, status, transaction_id =  add_new_acq_cards(db, acquired_date, seller, source, trans_comment, seller_comment, new_cards, shipping_cost, tax_cost, is_a_transaction)
    return message, status

@app.route('/api/insert_trade', methods=['POST'])
def insert_trade():
    data = request.json
    acquired_date = data.get('acquiredDate') 
    trader = data.get('trader')             
    source = data.get('source')
    trans_comment = data.get('transComment')
    trader_comment = data.get('traderComment')
    trader_comment = 'as trader: '+trader_comment if len(trader_comment)>0 else ''
    new_cards = data.get('tradingIn')
    sold_cards = data.get('tradingOut')
    shipping_cost = data.get('shippingcost')
    tax_cost = data.get('taxcost')

    # first add the cards traded in as bought
    # this doesn't commit
    responsemsg, status, transaction_id = add_new_acq_cards(db, acquired_date, trader, source, trans_comment, trader_comment, new_cards, shipping_cost, tax_cost, is_a_transaction=True, commit=False)
    if status==200:
        return itrade_away(db, sold_cards, transaction_id)  # this commits
    else:
        return jsonify({'message': 'Error while adding trading in cards.'}), 500


@app.route('/api/get_grading_companies', methods=['GET'])
def get_grading_companies():
    return get_grad_comps(db)

@app.route('/api/get_pending_cards', methods=['GET'])
def get_pending_cards():
    instance = Cardinstance.query.first()
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=25, type=int)
    # Extract filter parameters from the request
    card_name = request.args.get('cardname')
    expansions = request.args.get('expansions').split(',') if  request.args.get('expansions') else []
    number = request.args.get('number')
    
    return get_cards_pending_or_sold(db, page, per_page, card_name_filter=card_name, expansions_filter=expansions, number=number, is_selling_already=False)

    #return get_cards_pending(db, page, per_page)

@app.route('/api/sell_cards', methods=['POST'])
def sell_cards():
    cards = request.json.get('selectedCardIds')
    date = request.json.get('sellingDate')
    return insert_selling_cards(db, cards, date)

@app.route('/api/get_selling_cards', methods=['GET'])
def get_selling_cards():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    # Extract filter parameters from the request
    card_name = request.args.get('cardname')
    expansions = request.args.get('expansions').split(',') if  request.args.get('expansions') else []
    number = request.args.get('number')
    # Pass the filter parameters to get_cards_pending
    return get_cards_pending_or_sold(db, page, per_page, card_name_filter=card_name, expansions_filter=expansions, number=number, is_selling_already=True)


@app.route('/api/sold_cards', methods=['POST'])
def dispose_cards():
    cards = request.json.get('selectedCards')
    date = request.json.get('sellingDate')
    buyer = request.json.get('buyer')
    buyer_comment = str(request.json.get('buyerComment'))
    buyer_comment = 'as buyer: '+buyer_comment if len(buyer_comment)>0 else ''
    source = request.json.get('source')
    trans_comment = request.json.get('transComment')
    return isold(db, cards, date, buyer, buyer_comment, source, trans_comment) 

@app.route('/api/rarities', methods=['GET'])
def get_rarities():
    return rarities(db)

@app.route('/api/last_sold_cards', methods=['GET'])
def get_sold_cards():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=25, type=int)
    return get_sold(db, page, per_page)

@app.route('/api/get_transactions_info', methods=['GET'])
def get_transaction_info():
    bought_sold_filter = request.args.get('bought_sold_filter', default='both', type=str)
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=25, type=int)
    sort_by = request.args.get('sort_by', default='date', type=str)
    sort_order = request.args.get('sort_order', default='asc', type=str)

    card_name = request.args.get('cardname')
    expansions = request.args.get('expansions').split(',') if  request.args.get('expansions') else []
    number = request.args.get('number')
    counterparty = request.args.get('counterparty')
    source = request.args.get('source')

    return get_transactions_info(db, sort_by, sort_order, page, per_page, bought_sold_filter, card_name, expansions, number, counterparty, source)

@app.route('/api/get_expansions_transactions')
def get_expansions_transations():
    return get_exp_transactions(db)

@app.route('/api/get_stats', methods=['GET'])
def get_stats():
    time_filter_days = int(request.args.get('timeFilterDays')) if request.args.get('timeFilterDays') else None
    sold_per_bought_date_earnings_result = get_sold_per_bought_date_earnings(db, time_filter_days)
    bought_sold_stats_per_time_result = get_bought_sold_stats_per_time(db, time_filter_days)

    return jsonify({
        "single_card_stats_per_date": sold_per_bought_date_earnings_result,
        "cards_stats_per_date": bought_sold_stats_per_time_result
    })

@app.route('/api/get_counterparties', methods=['GET'])
def get_counterparties():
    cp =  counterparties(db)
    return cp

@app.route('/api/get_sources', methods=['GET'])
def get_sources():
    src =  sources(db)
    return src


@app.route('/api/get_factory_errors', methods=['GET'])
def get_factory_errors():
    fe =  factory_errors(db)
    return fe

@app.route('/api/deletecard', methods=['DELETE'])
def delete_card():
    data = request.get_json()

    # Extract the card information from the request data
    card_to_delete = data.get('card')
    # Due to ON DELETE CASCADE it will delete the corresponding rows in associated tables (selling, sold, acquired, etc)
    # this function also deletes the related transactions if they become empty (no cards in it).
    _, response = delete_card_instance(db, card_to_delete)
    if response == 200:
        return jsonify({'message': 'Cardinstance and related rows deleted successfully'}), 200
    else:
        return jsonify({'message': 'Error deleting a cardinstance'}), 500
    # db.commit()
    # return jsonify({'message': 'Cardinstance and related rows deleted successfully'}), 200

@app.route('/api/remove_from_selling', methods=['DELETE'])
def remove_from_selling():
    data = request.get_json()

    listing_to_delete = data.get('listing')
    _, response = delete_selling(db, listing_to_delete)
    if response == 200:
        return jsonify({'message': 'listing deleted successfully'}), 200
    else:
        return jsonify({'message': 'Error deleting a cardinstance'}), 500
    
@app.route('/api/deletetransaction', methods=['DELETE'])
def remove_transaction():
    data = request.get_json()

    transaction_to_delete = data.get('transaction')
    _, response = delete_transaction(db, transaction_to_delete)
    if response == 200:
        return jsonify({'message': 'transaction deleted successfully'}), 200
    else:
        return jsonify({'message': 'Error deleting transaction'}), 500
    
@app.route('/api/get_all_expansions', methods=['GET'])
def get_all_exp():
    return all_expansions(db)

@app.route('/api/update_transaction_comment', methods=['POST'])
def update_trans_comment():
    data = request.get_json()

    transaction = data.get('transaction')
    new_comment = data.get('new_comment')
    return update_transaction_comment(db, transaction, new_comment)

@app.route('/api/get_counterparty', methods=['GET'])
def get_counterparty():
    counterparty_name = request.args.get('name')
    return counterparty(db, counterparty_name)

@app.route('/api/update_counterparty', methods=['POST'])
def update_counterpart():
    data = request.get_json()

    counterparty = data.get('name')
    new_comment = data.get('new_comment')
    return update_counterparty(db, counterparty, new_comment)

@app.route('/api/get_cards_versions', methods=['GET'])
def get_cards_version():
    cards_json = request.args.get('cards')
    cards = json.loads(cards_json)
    return cards_versions(db, cards)

@app.route('/api/get_cards_languages', methods=['GET'])
def get_cards_languages():
    cards_json = request.args.get('cards')
    cards = json.loads(cards_json)
    return cards_languages(db, cards)

@app.route('/api/get_min_allowed_date', methods=['GET'])
def get_min_allowed_date():
    cards_json = request.args.get('cards')
    cards = json.loads(cards_json)
    expansions = set(card['expansion'] for card in cards)
    return min_allowed_date(db, expansions)

@app.route('/api/check_my_current_collection', methods=['GET'])
def get_my_current_collection():
    cards_json = request.args.get('cards')
    cards = json.loads(cards_json)
    return get_my_cardinstances(db, cards)


if __name__ == '__main__':
    # DEV SERVER
    #run(host='0.0.0.0', port=5000, debug=True)

    # PROD SERVER
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
