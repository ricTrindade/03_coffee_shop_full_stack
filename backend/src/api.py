import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from src.database.models import db_drop_and_create_all, setup_db, Drink
from src.auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES
@app.route('/drinks')
def drinks():
    drinks_in_db = Drink.query.all()
    drinks_json = [drink.short() for drink in drinks_in_db]
    data = {
        'success' : True,
        'drinks' : drinks_json
    }
    return jsonify(data)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(jwt_payload):
    drinks_in_db = Drink.query.all()
    drinks_json = [drink.long() for drink in drinks_in_db]
    data = {
        'success': True,
        'drinks': drinks_json
    }
    return jsonify(data)



@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt_payload):

    # Get Request Data
    request_data = request.json

    # Create new Drink
    new_drink = Drink(
        title=request_data['title'],
        recipe=json.dumps(request_data['recipe']) if 'recipe' in request_data else ''
    )

    # Insert Drink to the Db
    try:
        new_drink.insert()
    except Exception as e:
        print(e)
        abort(500)

    # Response JSON
    data = {
        'success': True,
        'drinks': [new_drink.long()]
    }
    return data



@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt_payload, drink_id):

    # Get Request Data
    request_data = request.json

    # Get and Update the Drink
    drink = Drink.query.get_or_404(drink_id)
    if 'title' in request_data:
        drink.title = request_data['title']
    if 'recipe' in request_data:
        drink.recipe = json.dumps(request_data['recipe'])
    try:
        drink.update()
    except Exception as e:
        print(e)
        abort(500)

    # Response JSON
    data = {
        'success': True,
        'drinks': [drink.long()]
    }
    return data


@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt_payload, drink_id):

    # Get and Delete the Drink
    drink = Drink.query.get_or_404(drink_id)
    try:
        drink.delete()
    except Exception as e:
        print(e)
        abort(500)

    # Response JSON
    data = {
        'success': True,
        'delete': drink_id
    }
    return data

# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(403)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "not authorised to perform this action"
    }), 403

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5000)