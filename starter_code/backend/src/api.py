import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'ContentType, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, PUT, DELETE')
        return response



    ## ROUTES
    '''
    @TODO implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''

    @app.route('/drinks', methods=['GET'])
    def drinks():
        try:
            coffee_drinks = Drink.query.all()
            drinks = []
            for drink in coffee_drinks:
                print(drink.short())
                drinks.append(drink.short())

            return jsonify({
                "success": True,
                "drinks": drinks
            })
        except:
            abort(404)

    '''
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks', methods = ['POST'])
    @requires_auth('post:drinks')
    def post_drinks(AuthToken):
        try:
            body = request.get_json()
            title = body.get('title')
            recipe = body.get('recipe')
            print(title, recipe)
            new_drink = Drink(
                title = title,
                recipe = recipe
            )
            new_drink.insert()
            coffee_drinks = Drink.query.all()
            drinks = []
            for drink in coffee_drinks:
                print(drink.short())
                drinks.append(drink.long())
            return jsonify({
                'success': True,
                'drinks': drinks
            })

        except:
            abort(422)
            db.session.rollback()

        finally:
            db.session.close()

    '''
    @TODO implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks-detail', methods = ['GET'])
    @requires_auth('get:drinks-detail')
    def drink_details(AuthToken):
        try:
            coffee_drinks = Drink.query.all()
            drinks = []
            for drink in coffee_drinks:
                drinks.append(drink.long())
            return jsonify({
                "success": True,
                "drinks": drinks
            })
        except BaseException:
            abort(404)


    '''
    @TODO implement endpoint
        PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    '''
    @app.route('/drinks/<int:id>', methods = ['PATCH'])
    @requires_auth('patch:drinks')
    def patch_drinks(AuthToken, id):
        drink = Drink.query.get(id)
        if drink:
            try:
                body = request.get_json()
                if body.get('title'):
                    title = body.get('title')
                    drink.title = title
                if body.get('recipe'):
                    recipe = body.get('recipe')
                    drink.recipe = recipe
                drink.update()
                print(drink)
                coffee_drinks = Drink.query.all()
                drinks = []
                for drink in coffee_drinks:
                    drinks.append(drink.long())
                return jsonify({
                    "success": True,
                    "drinks": drinks
                })
            except:
                abort(404)
                db.session.rollback
            finally:
                db.session.close()

    '''
    @TODO implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''

    @app.route('/drinks/<int:id>', methods = ['DELETE'])
    @requires_auth('delete:drinks')
    def delete_drinks(AuthToken, id):
        drink = Drink.query.get(id)
        if drink:
            try:
                drink.delete()
                db.session.commit()
                return jsonify({
                    "success": True,
                    "drinks": id
                })
            except:
                abort(404)
                db.session.rollback
            finally:
                db.session.close()
        else:
            abort(404)

    ## Error Handling

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
                        "success": False,
                        "error": 422,
                        "message": "unprocessable"
                        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "resource not found"
        }), 404

    @app.errorhandler(401)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 401,
            'message': "unauthorized"
        }), 401

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': "method not allowed"
        }), 405

    @app.errorhandler(403)
    def fobidden(error):
        return jsonify({
            'success': False,
            'error': 403,
            'message': "You do not have permission to access resources"
        }), 403

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': "internal server error"
        }), 500

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
    @app.errorhandler(AuthError)
    def auth_error(AuthError):
        error = AuthError.error
        status_code = AuthError.status_code
        return jsonify({
            'success': False,
            'error': error,
        }), status_code
    return app
