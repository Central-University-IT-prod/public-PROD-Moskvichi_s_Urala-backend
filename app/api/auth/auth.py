import random
from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token, jwt_required, current_user
from flask_restful import reqparse

from app.database.requests import *

auth_route = Blueprint('auth_route', __name__)
NAMES = ["Петр", "Василий", "Игорь"]


@auth_route.route('/login', methods=['POST'])
def login():
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('password', required=True)
    parser.add_argument('phone', required=True)
    data = parser.parse_args()
    user = get_user_by_phone(data.get('phone'))
    if user is None:
        user = create_user(random.choice(NAMES), "Тиньковович", data.get('phone'), data.get('password'))
        print(user.jwt_id)
    elif not user.check_password(data.get("password")):
        return jsonify({"reason": "Bad credentials"}), 401

    access_token = create_access_token(identity=user.jwt_id, expires_delta=timedelta(hours=24))

    return jsonify({"token": access_token}), 200


@auth_route.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    revoke_user_jwt(user_id=current_user.id)

    return jsonify({'message': 'success'}), 200
