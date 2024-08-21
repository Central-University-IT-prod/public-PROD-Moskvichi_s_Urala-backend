from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin

from app import admin, get_user_by_jwt, init_db, routes


def create_app():
    app = Flask(__name__)
    CORS(app)
    jwt = JWTManager()
    app.config.from_object("app.config")

    init_db()
    jwt.init_app(app)
    admin.init_app(app)

    for route in routes:
        app.register_blueprint(route, url_prefix="/api/v1")

    # jwt
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_headers, jwt_data):
        identity = jwt_data["sub"]
        user = get_user_by_jwt(identity)

        return user

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({"reason": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"reason": "Access denied"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"reason": "Request doesnt contain valid token"}), 401
    
    @jwt.user_lookup_error_loader
    def user_lookup_error(*args):
        return jsonify({"reason": "Access denied"}), 401

    return app
