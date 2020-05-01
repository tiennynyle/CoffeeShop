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

## ROUTES

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)
    result = {
        'success': True,
        'drinks': list(map(lambda drink: drink.short(), drinks))
    }
    return jsonify(result)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)
    result = {
            'success': True,
            'drinks': list(map(lambda drink: drink.long(), drinks))
            }
    return jsonify(result)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = request.get_json()
    try:
        title, recipe = body['title'], str(body['recipe'])
        recipe = recipe.replace("\'", "\"")
        drink = Drink(title=title, recipe=str(recipe))
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': drink.long()
        })
    except:
        abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def replace_drink(payload, id):
    drink = Drink.query.filter_by(id=id).first()
    if drink is None:
        abort(404)
    else:
        body = request.get_json()
        title, recipe = body['title'], str(body['recipe'])
        recipe = recipe.replace("\'", "\"")
        drink.title = title
        drink.recipe = recipe
        drink.update()
    return jsonify({
        'success': True,
        "drinks": drink.long()
    })


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink_by_id(payload, id):
    drink = Drink.query.filter_by(id=id).first()
    if drink is None:
        abort(404)
    else:
        drink.delete()
    return jsonify({
        'success': True,
        "delete": id
    })

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def notfound(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "Not Found"
                    }), 404


@app.errorhandler(AuthError)
def authentification_failed(AuthError):
    return jsonify({
                    "success": False,
                    "error": AuthError.status_code,
                    "message": "authentification fails"
                    }), 401
