from app.database.models import *
from app.database.requests import *
from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required

meet_route = Blueprint('meet_route', __name__)


@meet_route.route("/meet/active", methods=["GET"])
@jwt_required()
def active_meets():
    user_meets = get_user_meets(
        current_user.id,
        status=[MeetStatusEnum.CREATED, MeetStatusEnum.IN_PROGRESS, MeetStatusEnum.ARRIVED]
    )
    response = []
    for user_meet in user_meets:
        employee_profile = get_employee(user_meet.employee_id)
        product = get_product_by_id(user_meet.product_id)
        documents = get_product_documents(product.id)
        if user_meet.status == MeetStatusEnum.ARRIVED:
            status = "Представитель прибыл"
        elif user_meet.status == MeetStatusEnum.IN_PROGRESS:
            status = "Представитель выехал к вам"
        else:
            status = ""
        res = {
            "id": user_meet.id,
            "employee_name": f"{employee_profile.first_name} {employee_profile.last_name}",
            "employee_phone": employee_profile.phone,
            "date": user_meet.date,
            "address": user_meet.address,
            "product_name": product.name,
            "product_description": product.description,
            "documents": documents,
            "status2": status
        }
        response.append(res)
    return jsonify({"meets": response}), 200


@meet_route.route("/meet/history", methods=["GET"])
@jwt_required()
def history_meets():
    user_meets = get_user_meets(
        current_user.id, status=[MeetStatusEnum.CANCELED, MeetStatusEnum.DONE]
    )
    response = []
    for user_meet in user_meets:
        employey_profile = get_employee(user_meet.employee_id)
        product = get_product_by_id(user_meet.product_id)
        status = "Встреча отменена" if user_meet.status == MeetStatusEnum.CANCELED else ""
        res = {
            "id": user_meet.id,
            "employee_name": f"{employey_profile.first_name} {employey_profile.last_name}",
            "employee_phone": employey_profile.phone,
            "date": user_meet.date,
            "address": user_meet.address,
            "product_name": product.name,
            "product_description": product.description,
            "status2": status
        }
        response.append(res)

    return jsonify({"meets": response}), 200


@meet_route.route("/meet/<id_meet>", methods=["GET"])
@jwt_required()
def get_meet_by_id_route(id_meet: int):
    user_id = current_user.id
    meet = get_meet_by_id(meet_id=id_meet)
    if (meet is None) or meet.user_id != user_id:
        return jsonify({"error": "Такой встречи не найдено", "meet": {}}), 200
    response = [
        {
            "id": meet.id,
            "employer_id": get_employee(meet.employee_id).id,
            "employer_name": f"{get_employee(meet.employee_id).first_name} {get_employee(meet.employee_id).last_name}",
            "employer_phone": get_employee(meet.employee_id).phone,
            "product_name": get_product_by_id(meet.product_id).name,
            "product_description": get_product_by_id(meet.product_id).description,
            "date": meet.date,
            "rate": meet.rate,
            "address": meet.address,
            "documents": get_product_documents(meet.product_id),
            "status": meet.status in [MeetStatusEnum.CANCELED, MeetStatusEnum.DONE]
        }
    ]
    return jsonify({"meet": response}), 200


@meet_route.route("/meet/all_documents", methods=["GET"])
@jwt_required()
def get_all_documents_endpoint():
    documents = get_all_documents()
    response = [
        {
            "id": doc.id,
            "name": doc.name,
            "live_time": doc.life_time
        } for doc in documents
    ]
    return jsonify({"documents": response}), 200


@meet_route.route("/meet/cancel", methods=["POST"])
@jwt_required()
def cancel_meet():
    data = request.json
    meet_id = data.get("id", None)
    user_id = current_user.id
    meet = get_meet_by_id(meet_id)
    if meet.user_id != user_id or not meet:
        return jsonify({"error": "Такой встречи не найдено"}), 200
    if meet_id is None:
        return jsonify({"error": "Не передан параметр 'id'"}), 200
    change_meet_status(meet_id=meet_id, status=MeetStatusEnum.CANCELED)

    return jsonify({"ok": "Встреча отменена"}), 201


# перенос встречи
@meet_route.route("/meet/transfer", methods=["POST"])
@jwt_required()
def meet_transfer():
    data = request.json
    date = datetime.strptime(data.get("date"), "%Y-%m-%d %H:%M")
    print(date)
    meet_id = data.get("meet_id")
    change_meet_date(meet_id, date)

    return jsonify({"status": "ok"}), 201


@meet_route.route("/meet/rate", methods=["POST"])
@jwt_required()
def rate_meet():
    data = request.json
    rate = data.get("rate")
    meet_id = data.get("id")
    set_rate_meet(meet_id, rate)
    return jsonify({"status": "ok"}), 201
