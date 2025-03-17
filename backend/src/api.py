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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
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
        title = request_data['title'],
        recipe = json.dumps(request_data['recipe'])
    )

    # Insert Drink to the Db
    try:
        new_drink.insert()
    except:
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
    drink.title = request_data['title']
    drink.recipe = json.dumps(request_data['recipe'])
    try:
        drink.update()
    except:
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
    except:
        abort(500)

    # Response JSON
    data = {
        'success': True,
        'delete': drink_id
    }
    return data

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5000)