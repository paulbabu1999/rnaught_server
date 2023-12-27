# handlers.py
from flask import request, jsonify
from services import UserService, ContactService, ProbabilityService, PoliceService

class UserHandler:
    def __init__(self):
        self.user_service = UserService()

    def register_user(self):
        return self.user_service.register_user(request)

class ContactHandler:
    def __init__(self):
        self.contact_service = ContactService()

    def new_contact(self):
        return self.contact_service.new_contact(request)

class ProbabilityHandler:
    def __init__(self):
        self.probability_service = ProbabilityService()

    def check_probability(self):
        return self.probability_service.check_probability(request)

    def is_positive(self):
        return self.probability_service.is_positive(request)

class PoliceHandler:
    def __init__(self):
        self.police_service = PoliceService()

    def police(self):
        return self.police_service.police(request)
