# models.py
from flask import jsonify
from repository import UserRepository, ContactRepository, ProbabilityRepository, PoliceRepository

class UserModel:
    def register_user(self, request):
        user_repository = UserRepository()
        return user_repository.register_user(request)

class ContactModel:
    def new_contact(self, request):
        contact_repository = ContactRepository()
        return contact_repository.new_contact(request)

class ProbabilityModel:
    def check_probability(self, request):
        probability_repository = ProbabilityRepository()
        return probability_repository.check_probability(request)

    def is_positive(self, request):
        probability_repository = ProbabilityRepository()
        return probability_repository.is_positive(request)

class PoliceModel:
    def police(self, request):
        police_repository = PoliceRepository()
        return police_repository.police(request)
