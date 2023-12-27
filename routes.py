# routes.py
from flask import request, jsonify
from handlers import UserHandler, ContactHandler, ProbabilityHandler, PoliceHandler

def register_routes(app):
    user_handler = UserHandler()
    contact_handler = ContactHandler()
    probability_handler = ProbabilityHandler()
    police_handler = PoliceHandler()

    app.route("/register", methods=['POST'])(user_handler.register_user)
    app.route("/new_contact", methods=['POST'])(contact_handler.new_contact)
    app.route("/probability", methods=['POST'])(probability_handler.check_probability)
    app.route("/positive", methods=['POST'])(probability_handler.is_positive)
    app.route("/police", methods=['POST'])(police_handler.police)
