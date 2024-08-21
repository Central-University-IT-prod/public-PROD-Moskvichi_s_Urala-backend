from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, jwt_required
from app.database.requests import *

profile_route = Blueprint('profile_route', __name__)
current_user: User


@profile_route.route('/profile', methods=["GET"])
@jwt_required()
def profile():
    user_docs = get_user_documents(user_id=current_user.id)
    documents = [
        {
            "document_id": doc.document_id,
            "expired_date": doc.expire
         }
        for doc in user_docs
    ]
    response = {
        "name": f"{current_user.first_name} {current_user.last_name}",
        "phone": current_user.phone,
        "documents": documents
    }

    return jsonify({"profile": response}), 200


@profile_route.route("/profile/get_user_documents", methods=["GET"])
@jwt_required()
def get_users_documents():
    documents = get_user_documents(current_user.id)
    response = [
        {
            "user_docs": doc.document_id
        } for doc in documents
    ]
    return jsonify({"user_docs": response}), 200
