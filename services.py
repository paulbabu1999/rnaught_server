# services.py
from flask import jsonify
from models import UserModel, ContactModel, ProbabilityModel, PoliceModel

class UserService:
    def register_user(self, request):
        user_model = UserModel()
        return user_model.register_user(request)

class ContactService:
    def new_contact(self, request):
        contact_model = ContactModel()
        return contact_model.new_contact(request)

class ProbabilityService:
    def check_probability(self, request):
        probability_model = ProbabilityModel()
        return probability_model.check_probability(request)

    def is_positive(self, request):
        probability_model = ProbabilityModel()
        return probability_model.is_positive(request)

class PoliceService:
    def police(self, request):
        police_model = PoliceModel()
        return police_model.police(request)
