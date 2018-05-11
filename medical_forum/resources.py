# coding= utf-8
'''
Created on 26.01.2013
Modified on 26.03.2018
@author: mika oja
@author: ivan
@author: yazan
@author: Issam
'''

from flask import redirect, send_from_directory
from . import hypermedia_formats as hyper_const
from .api import API, APP
from .user_resources import User, Users
from .profile_resources import UserPublic, UserRestricted
from .message_resources import Message, Messages
from .diagnosis_resources import Diagnoses, Diagnosis, DiagnosesHistory


def add_resources_routes():
    """
    Add all routes of the resources of the medical forum
    """
    API.add_resource(Messages, "/medical_forum/api/messages/",
                     endpoint="messages")
    API.add_resource(Message, "/medical_forum/api/messages/<regex('msg-\d+'):message_id>/",
                     endpoint="message")
    API.add_resource(UserPublic, "/medical_forum/api/users/<username>/public_profile/",
                     endpoint="public_profile")
    API.add_resource(UserRestricted, "/medical_forum/api/users/<username>/restricted_profile/",
                     endpoint="restricted_profile")
    API.add_resource(User, "/medical_forum/api/users/<username>/",
                     endpoint="user")
    API.add_resource(Users, "/medical_forum/api/users/",
                     endpoint="users")
    API.add_resource(Diagnoses, "/medical_forum/api/diagnoses/",
                     endpoint="diagnoses")
    API.add_resource(Diagnosis, "/medical_forum/api/diagnoses/<regex('dgs-\d+'):diagnosis_id>/",
                     endpoint="diagnosis")
    API.add_resource(DiagnosesHistory, "/medical_forum/api/diagnoses/<user_id>/",
                     endpoint="diagnoses_user")


add_resources_routes()


@APP.route("/profiles/<profile_name>/")
def redirect_to_profile(profile_name):
    """Redirect to the given profile"""
    return redirect(hyper_const.APIARY_PROFILES_URL + profile_name)


@APP.route("/medical_forum/link-relations/<rel_name>/")
def redirect_to_rels(rel_name):
    """Redirect to relations name"""
    return redirect(hyper_const.APIARY_RELS_URL + rel_name)


@APP.route("/medical_forum/schema/<schema_name>/")
def send_json_schema(schema_name):
    """Send json schema"""
    return send_from_directory(APP.static_folder, "schema/{}.json".format(schema_name))
