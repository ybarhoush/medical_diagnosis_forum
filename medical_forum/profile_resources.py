"""
Public and restricted profiles resource API implementation
"""

import json
from werkzeug.exceptions import NotFound

from flask import request, Response, g
from flask_restful import Resource

from .resources import API, hyper_const
from .error_handlers import create_error_response

from . import forum_object as forum_obj
from . import user_resources as user_res


class UserPublic(Resource):
    """User public profile API implementation"""

    def get(self, username):
        """

        Get the public profile (picture and lastname) of a single user.

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Forum_User_Profile
        """

        user_db = g.con.get_user(username)
        if not user_db:
            return create_error_response(404, "Unknown user",
                                         "There is no a user with username %s"
                                         % username)

        pub_profile = user_db["public_profile"]

        envelope = forum_obj.ForumObject(
            username=username,
            reg_date=pub_profile["reg_date"]
        )

        envelope.add_namespace("forum", hyper_const.LINK_RELATIONS_URL)
        envelope.add_control("self", href=API.url_for(
            UserPublic, username=username))
        envelope.add_control("up", href=API.url_for(
            user_res.User, username=username))
        envelope.add_control(
            "forum:private-data", href=API.url_for(UserRestricted, username=username))
        envelope.add_control_edit_public_profile(username)

        return Response(json.dumps(envelope), 200, mimetype=hyper_const.MASON + ";" +
                        hyper_const.FORUM_USER_PROFILE)

    def put(self, username):
        """
        Modify the public profile of a user.

        REQUEST ENTITY BODY:
        * Media type: JSON

        """

        if not g.con.contains_user(username):
            return create_error_response(404, "Unknown user",
                                         "There is no user with username {}".format(username))

        request_body = request.get_json()
        if not request_body:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format")

        try:
            picture = request_body["picture"]
            lastname = request_body["lastname"]
        except KeyError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure to include all mandatory properties")

        user_public = {
            "picture": picture,
            "lastname": lastname
        }

        if not g.con.modify_user(username, user_public, None):
            return create_error_response(404, "Unknown user",
                                         "There is no user with username {}".format(username))

        return "", 204


class UserRestricted(Resource):
    """User restricted profile API implementation"""

    def get(self, username):
        """
        Get the private profile of a user

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Forum_User_Profile
        """

        user_db = g.con.get_user(username)
        if not user_db:
            return create_error_response(404, "Unknown user",
                                         "There is no a user with username %s"
                                         % username)

        priv_profile = user_db["restricted_profile"]
        public_profile = user_db["public_profile"]

        envelope = forum_obj.ForumObject(
            username=username,
            user_type=priv_profile["user_type"],
            firstname=priv_profile["firstname"],
            lastname=priv_profile["lastname"],
            work_address=priv_profile["work_address"],
            gender=priv_profile["gender"],
            age=priv_profile["age"],
            email=priv_profile["email"],
            phone=priv_profile["phone"],
            diagnosis_id=priv_profile["diagnosis_id"],
            height=priv_profile["height"],
            weight=priv_profile["weight"],
            speciality=priv_profile["speciality"],
            picture=public_profile["picture"],
            reg_date=public_profile['reg_date']
        )

        envelope.add_namespace("forum", hyper_const.LINK_RELATIONS_URL)
        envelope.add_control("self", href=API.url_for(
            UserRestricted, username=username))
        envelope.add_control("up", href=API.url_for(
            user_res.User, username=username))
        envelope.add_control("forum:public-data",
                             href=API.url_for(UserPublic, username=username))
        envelope.add_control_edit_private_profile(username)

        return Response(json.dumps(envelope), 200, mimetype=hyper_const.MASON + ";" +
                        hyper_const.FORUM_USER_PROFILE)

    def put(self, username):
        """
        Edit the private profile of a user

        REQUEST ENTITY BODY:
        * Media type: JSON
        """

        if not g.con.contains_user(username):
            return create_error_response(
                404, "Unknown user", "There is no user with username {}".format(username))

        request_body = request.get_json()
        if not request_body:
            return create_error_response(415, "Unsupported Media Type", "Use  JSON format")

        try:
            priv_profile = dict(
                user_id=request_body["user_id"],
                user_type=request_body["user_type"],
                work_address=request_body["work_address"],
                email=request_body["email"],
                firstname=request_body["firstname"],
                gender=request_body["gender"],
                age=request_body["age"],
                phone=request_body["phone"],
                diagnosis_id=request_body.get("diagnosis_id", ""),
                height=request_body.get("height", ""),
                weight=request_body.get("weight", ""),
                speciality=request_body.get("speciality", ""))
        except KeyError:
            return create_error_response(
                400, "Wrong request format", "Be sure to include all mandatory properties")

        if not g.con.modify_user(username, None, priv_profile):
            return NotFound()
        return "", 204
