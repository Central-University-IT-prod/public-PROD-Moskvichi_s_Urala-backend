import random
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required
from app.api.tools.map import (get_city_by_coordinates)
from app.api.tools.sms import send_sms
from app.database.models import User
from app.database.requests import (create_meet, get_all_products, get_last_user_locations, get_city_employees,
                                   get_employees_busy_time, get_product_documents, get_busy_employees)

create_meet_route = Blueprint('create_meet_route', __name__)

current_user: User


@create_meet_route.route("/products/all", methods=['GET'])
@jwt_required()
def get_products():
    products = get_all_products()
    response = []
    for product in products:
        res = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "documents": get_product_documents(product.id)
        }
        response.append(res)
    return jsonify({"products": response}), 200


@create_meet_route.route("/user/locations", methods=['GET'])
@jwt_required()
def get_last_locations():
    locations = get_last_user_locations(current_user.id)
    return jsonify(dict(locations=locations)), 200


@create_meet_route.route("/locations/check", methods=['GET'])
@jwt_required()
def is_location_available():
    args = request.args
    print(args)
    lon = args["lon"]
    lat = args["lat"]
    product_id = args["product_id"]
    city, address = get_city_by_coordinates(lat, lon)
    employers = get_city_employees(city, product_id)
    print(employers, city)
    if city == -1 or (not employers):
        return jsonify({'error': "К сожалению доставка в данной области не доступна :(", "employers": []}), 200

    return jsonify({"employers": employers}), 200


@create_meet_route.route("/user/available_times", methods=['GET'])
@jwt_required()
def get_available_times():
    args = request.args
    employers = args["employers"][1:-1].split(",")
    return jsonify(get_employees_busy_time(employers)), 200


@create_meet_route.route("/meet/create", methods=['POST'])
@jwt_required()
def create_meet_point():
    args = request.json
    user_id = current_user.id
    product_id = args["product_id"]
    date = datetime.strptime(args["date"], "%Y-%m-%d %H:%M")
    lon = args["lon"]
    lat = args["lat"]
    agent = args.get("agent", None)

    city, address = get_city_by_coordinates(lat, lon)
    emp = get_city_employees(city, product_id)
    busy_emp = get_busy_employees(date)
    create_meet(user_id, product_id, lat, lon, address, date, agent, random.choice(list(set(emp) - busy_emp)))
    send_sms(current_user.phone, "ррр", date - timedelta(hours=1))
    return jsonify(), 200
