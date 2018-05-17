"""
Users and User resource API implementation
"""

import json
from flask import request, Response, g
from flask_restful import Resource, abort
from .resources import API, hyper_const
from .error_handlers import create_error_response

from . import forum_object as forum_obj
from . import profile_resources as profile_res
from . import diagnosis_resources as diagnosis_res


class Users(Resource):
    """Users resource implementation"""

    def get(self):
        """
        Gets a list of all the users in the database.

        It returns always status code 200.

        RESPONSE ENTITY BODY:

         OUTPUT:
            * Media type: application/vnd.mason+json
                https://github.com/JornWildt/Mason
            * Profile: Forum_User
                /profiles/user-profile

        Link relations used in items: messages

        Semantic descriptions used in items: username, reg_date

        Link relations used in links: messages-all

        Semantic descriptors used in template: speciality, weight, Height, diagnosis_id
        phone, picture, email, age, gender, work_address, firstname, lastname, user_type

        NOTE:
         * Attributes match one-to-one with column names in the database.
        """
        # PERFORM OPERATIONS
        # Create the messages list
        users_db = g.con.get_users()

        # FILTER AND GENERATE THE RESPONSE
        # Create the envelope
        envelope = forum_obj.ForumObject()

        envelope.add_namespace("forum", hyper_const.LINK_RELATIONS_URL)

        envelope.add_control_add_user()
        envelope.add_control_messages_all()
        envelope.add_control_diagnoses_all()
        envelope.add_control("self", href=API.url_for(Users))

        items = envelope["items"] = []

        for user in users_db:
            item = forum_obj.ForumObject(
                username=user["username"],
                reg_date=user["reg_date"],
                user_id=user["user_id"],
                user_type=user["user_type"],
                speciality=user["speciality"]
            )
            item.add_control("self", href=API.url_for(
                User, username=user["username"]))
            item.add_control("profile", href=hyper_const.FORUM_USER_PROFILE)
            items.append(item)

        # RENDER
        return Response(json.dumps(envelope), 200, mimetype=hyper_const.MASON + ";" +
                        hyper_const.FORUM_USER_PROFILE)

    def post(self):
        """
        Adds a new user to the database.

        REQUEST ENTITY BODY:
         * Media type: JSON
         * Profile: Forum_User

        Semantic descriptors used in template:
        # NOTE mandatory/optional fields

        RESPONSE STATUS CODE:
         * Returns 201 + the url of the new resource in the Location header
         * Return 409 Conflict if there is another user with the same username
         * Return 400 if the body is not well formed
         * Return 415 if it receives a media type != application/json

        NOTE:
         * The attributes match one-to-one with column names in the database.

        NOTE:
        The: py: method:`Connection.append_user()` receives as a parameter a
        dictionary with the following format.
               {'public_profile':{'reg_date':,'username':'',
                                   'speciality':'','user_type':''},
                'restricted_profile':{'firstname':'','lastname':'',
                                      'work_address':'','gender':'',
                                      'picture':'', age':'', email':''}
                }

        """

        if hyper_const.JSON != request.headers.get("Content-Type", ""):
            abort(415)
        # PARSE THE REQUEST:
        request_body = request.get_json(force=True)
        if not request_body:
            return create_error_response(
                415, "Unsupported Media Type", "Use a JSON compatible format", )

        # Get the request body and serialize it to object
        # We should check that the format of the request body is correct. Check
        # That mandatory attributes are there.

        # pick up username so we can check for conflicts
        try:
            username = request_body["username"]
        except KeyError:
            return create_error_response(
                400, "Wrong request format", "User username was missing from the request")

        # Conflict if user already exist
        if g.con.contains_user(username):
            return create_error_response(
                409, "Username already exist", "There is already a user with same username:%s."
                % username)

        # pick up rest of the mandatory fields
        try:
            speciality = request_body["speciality"]
            user_type = request_body["user_type"]
            firstname = request_body["firstname"]
            lastname = request_body["lastname"]
            work_address = request_body["work_address"]

        except KeyError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure to include all mandatory properties")

        # pick up rest of the optional fields
        picture = request_body.get("picture", "")
        gender = request_body.get("gender", "")
        age = request_body.get("age", "")
        email = request_body.get("email", "")
        weight = request_body.get("weight", "")
        height = request_body.get("height", "")
        phone = request_body.get("phone", "")
        print(phone + " " + height + " " + weight)

        user = {'public_profile': {'username': username,
                                   'speciality': speciality, 'user_type': user_type},

                'restricted_profile': {'firstname': firstname, 'lastname': lastname,
                                       'work_address': work_address, 'gender': gender,
                                       'picture': picture, 'age': age, 'email': email,
                                       'phone': phone, 'weight': weight, 'height': height}}
        try:
            username = g.con.append_user(username, user)
        except ValueError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include all"
                                         " mandatory properties")

        # CREATE RESPONSE AND RENDER
        return Response(status=201,
                        headers={"Location": API.url_for(User, username=username)})


class User(Resource):
    """
    User Resource. Public and private profile are separate resources.
    """

    def get(self, username):
        """
        Get basic information of a user:

        INPUT PARAMETER:
       : param str username: username of the required user.

        OUTPUT:
         * Return 200 if the username exists.
         * Return 404 if the username is not stored in the system.

        RESPONSE ENTITY BODY:

        * Media type recommended: application/vnd.mason+json
        * Profile recommended: application/vnd.mason+json

        Link relations used: self, collection, public-data, private-data,
        messages.

        Semantic descriptors used: username and reg_date

        NOTE:
        The: py: method:`Connection.get_user()` returns a dictionary with the
        the following format.

               {'public_profile':{'reg_date':,'username':'',
                                   'speciality':'','user_type':''},
                'restricted_profile':{'firstname':'','lastname':'',
                                      'work_address':'','gender':'',
                                      'picture':'', age':'', email':''}
                }
        """

        user_db = g.con.get_user(username)
        if not user_db:
            return create_error_response(
                404, "Unknown user", "There is no user with username %s" % username)

        envelope = forum_obj.ForumObject(
            username=username,
            reg_date=user_db["public_profile"]["reg_date"],
            user_id=user_db["restricted_profile"]["user_id"],
            user_type=user_db["public_profile"]["user_type"],
            speciality=user_db["public_profile"]["speciality"]
        )

        envelope.add_namespace("forum", hyper_const.LINK_RELATIONS_URL)
        envelope.add_control("self", href=API.url_for(User, username=username))
        envelope.add_control("profile", href=hyper_const.FORUM_USER_PROFILE)
        envelope.add_control("medical_forum:private-data",
                             href=API.url_for(profile_res.UserRestricted, username=username))
        envelope.add_control("medical_forum:public-data",
                             href=API.url_for(profile_res.UserPublic, username=username))
        envelope.add_control_messages_all()
        envelope.add_control_messages_history(username=username)
        envelope.add_control_diagnoses_all()
        envelope.add_control("medical_forum:diagnoses-history",
                             href=API.url_for(diagnosis_res.DiagnosesHistory,
                                              user_id=user_db["restricted_profile"]["user_id"]))
        envelope.add_control("collection", href=API.url_for(Users))
        envelope.add_control_delete_user(username)

        return Response(json.dumps(envelope), 200, mimetype=hyper_const.MASON + ";" +
                        hyper_const.FORUM_USER_PROFILE)

    def delete(self, username):
        """
        Delete a user in the system.

       : param str username: username of the required user.

        RESPONSE STATUS CODE:
         * If the user is deleted returns 204.
         * If the username does not exist return 404
        """

        print('test delete')

        # PEROFRM OPERATIONS
        # Try to  delete the user. If it could not be deleted, the database
        # returns None.
        if g.con.delete_user(username):
            # RENDER RESPONSE
            return '', 204
        else:
            # GENERATE ERROR RESPONSE
            return create_error_response(
                404, "Unknown user", "There is no user with username %s" % username)
