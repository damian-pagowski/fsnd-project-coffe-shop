import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks_short():
    drinks = []
    print("ROUTE")
    try:
        drinks_data = Drink.query.all()
        drinks = list(map(Drink.short, drinks_data))
    except:
        abort(422)
    return jsonify({
        'success': True,
        'drinks': drinks
    })

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    drinks = []
    try:
        drinks_data = Drink.query.all()
        drinks = list(map(Drink.long, drinks_data))
    except:
        abort(422)
    return jsonify({
        'success': True,
        'drinks': drinks
    })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    req_title = body.get('title')
    req_recipe = body.get('recipe')
    if not isinstance(req_recipe, list):
        abort(422)
    for each in req_recipe:
        if not('color' in each and 'parts' in each):
            abort(422)

    try:
        drink = Drink(title=req_title, recipe=json.dumps(req_recipe))
        drink.insert()
        return jsonify({"success": True, "drinks": [drink.long()]})
    except:
        abort(422)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()
    req_title = body.get('title')
    req_recipe = body.get('recipe')
    drink = None

    try:
        drink = Drink.query.get(id)
        drink.title = req_title
        drink.recipe = json.dumps(req_recipe)
        drink.update()
        return jsonify({"success": True, "drinks": [drink.long()]})
    except:
        if drink == None:
            abort(404)
        else:
            abort(422)

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = None
    try:
        drink = Drink.query.get(id)
        drink.delete()
        return jsonify({"success": True, "delete": id})
    except:
        if drink == None:
            abort(404)
        else:
            abort(422)

# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 403
