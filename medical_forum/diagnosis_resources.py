"""
Diagnosis and Diagnoses resource API implementation
"""

import json
from flask import request, Response, g
from flask_restful import Resource, abort
from .resources import API, hyper_const
from . import forum_object as forum_obj
from .error_handlers import create_error_response
from . import user_resources as user_res


class Diagnoses(Resource):
    """
    Resource Diagnoses implementation
    """

    def get(self):
        """
        Get all diagnoses.

        INPUT parameters:
          None

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Forum_Diagnosis
          /profiles/diagnosis_profile

        NOTE:
         * The attribute disease is obtained from the column diagnoses.disease
         * The attribute diagnosis is obtained from the column diagnoses.diagnosis_description
         * The attribute message_id is obtained from the column diagnoses.message_id
         * The attribute user_id is obtained from the column diagnoses.user_id
        """

        # Extract diagnoses from database
        diagnoses_db = g.con.get_diagnoses()

        envelope = forum_obj.ForumObject()
        envelope.add_namespace("medical_forum", hyper_const.LINK_RELATIONS_URL)

        envelope.add_control("self", href=API.url_for(Diagnoses))
        envelope.add_control_users_all()
        envelope.add_control_add_diagnosis()

        items = envelope["items"] = []

        for dgs in diagnoses_db:
            item = forum_obj.ForumObject(
                id=dgs["diagnosis_id"], disease=dgs["disease"])
            item.add_control("self", href=API.url_for(
                Diagnosis, diagnosis_id=dgs["diagnosis_id"]))
            item.add_control(
                "profile", href=hyper_const.FORUM_DIAGNOSIS_PROFILE)
            items.append(item)

        # RENDER
        return Response(json.dumps(envelope), 200, mimetype=hyper_const.MASON + ";" +
                        hyper_const.FORUM_DIAGNOSIS_PROFILE)

    def post(self):
        """
        Adds a a new diagnosis.

        REQUEST ENTITY BODY:
         * Media type: JSON:
         * Profile: Forum_Diagnosis
          /profiles/diagnosis_profile

        NOTE:
         * The attribute disease is obtained from the column diagnoses.disease
         * The attribute diagnosis_description is obtained from the column
         * diagnoses.diagnosis_description
         * The attribute message_id is obtained from the column diagnoses.message_id
         * The attribute user_id is obtained from the column diagnoses.user_id

        The body should be a JSON document that matches the schema for new diagnoses

        RESPONSE STATUS CODE:
         * Returns 201 if the diagnosis has been added correctly.
           The Location header contains the path of the new diagnosis
         * Returns 400 if the diagnosis is not well formed or the entity body is
           empty.
         * Returns 415 if the format of the response is not json
         * Returns 500 if the diagnosis could not be added to database.

        """

        # Extract the request body. In general would be request.data
        # Since the request is JSON I use request.get_json
        # get_json returns a python dictionary after serializing the request body
        # get_json returns None if the body of the request is not formatted
        # using JSON. We use force=True since the input media type is not
        # application/json.

        if hyper_const.JSON != request.headers.get("Content-Type", ""):
            return create_error_response(
                415, "UnsupportedMediaType", "Use a JSON compatible format")
        request_body = request.get_json(force=True)

        try:
            disease = request_body["disease"]
            diagnosis_description = request_body["diagnosis_description"]
            message_id = request_body.get("message_id")
            user_id = request_body.get("user_id")

        except KeyError:
            # This is launched if either title or body does not exist or if
            # the template.data array does not exist.
            return create_error_response(
                400, "Wrong request format", "Be sure you include diagnosis and disease")

        # Create the new diagnosis and build the response code"
        user_id = int(user_id)
        message_id = 'msg-' + message_id

        diagnosis = {'user_id': user_id,
                     'message_id': message_id,
                     'disease': disease, 'diagnosis_description': diagnosis_description}

        try:
            new_diagnosis_id = g.con.create_diagnosis(diagnosis)
        except ValueError:
            return create_error_response(
                400, "Request by non-doctor user", "Only doctors can add a diagnosis")

        if not new_diagnosis_id:
            return create_error_response(
                500, "Problem with the database", "Cannot access the database")

        # Create the Location header with the id of the diagnosis created
        url = API.url_for(Diagnosis, diagnosis_id=new_diagnosis_id)

        # RENDER
        # Return the response
        return Response(status=201, headers={"Location": url})


class Diagnosis(Resource):
    """
    Resource that represents a single diagnosis in the API.
    """

    def get(self, diagnosis_id):
        """
        Get the disease, the diagnosis and the id of a specific diagnosis and its message id.

        Returns status code 404 if the diagnosis_id does not exist in the database.

        INPUT PARAMETER
       : param str diagnosis_id: The id of the diagnosis to be retrieved from the
            system

        RESPONSE ENTITY BODY:
         * Media type: application/vnd.mason+json:
             https://github.com/JornWildt/Mason
         * Profile: Forum_Diagnosis
           /profiles/diagnosis-profile

            Link relations used: self, collection, user_id,
            # NOTE, and reply?

            Semantic descriptors used: diagnosis, disease
            return None.

        RESPONSE STATUS CODE
         * Return status code 200 if everything OK.
         * Return status code 404 if the diagnosis was not found in the database.

        NOTE:
         * The attribute disease is obtained from the column diagnoses.disease
         * The attribute diagnosis is obtained from the column diagnoses.diagnosis_description
         * The attribute message_id is obtained from the column diagnoses.message_id
         * The attribute user_id is obtained from the column diagnoses.user_id
        """

        # PEFORM OPERATIONS INITIAL CHECKS
        # Get the diagnosis from db
        diagnosis_db = g.con.get_diagnosis(diagnosis_id)
        if not diagnosis_db:
            abort(404, diagnosis="There is no a diagnosis with id %s" % diagnosis_id,
                  resource_type="Diagnosis",
                  resource_url=request.path,
                  resource_id=diagnosis_id)

        user_id = diagnosis_db.get("user_id")
        message_id = diagnosis_db.get("message_id")
        # parent = diagnosis_db.get("reply_to", None)

        # FILTER AND GENERATE RESPONSE
        # Create the envelope:
        envelope = forum_obj.ForumObject(
            disease=diagnosis_db["disease"],
            diagnosis_description=diagnosis_db["diagnosis_description"],
            user_id=user_id,
            message_id=message_id
        )

        envelope.add_namespace("medical_forum", hyper_const.LINK_RELATIONS_URL)
        envelope.add_namespace("atom-thread", hyper_const.ATOM_THREAD_PROFILE)

        envelope.add_control_reply_to(diagnosis_id)
        envelope.add_control(
            "profile", href=hyper_const.FORUM_DIAGNOSIS_PROFILE)
        envelope.add_control("collection", href=API.url_for(Diagnoses))
        envelope.add_control("self", href=API.url_for(
            Diagnosis, diagnosis_id=diagnosis_id))
        envelope.add_control(
            "user_id", href=API.url_for(user_res.User, username=user_id))

        # if parent:
        #     envelope.add_control("atom-thread:in-reply-to",
        #                           href=api.url_for(Diagnosis, diagnosis_id=parent))
        # else:
        #     envelope.add_control("atom-thread:in-reply-to", href=None)
        envelope.add_control("atom-thread:in-reply-to", href=None)
        # RENDER
        return Response(json.dumps(envelope), 200, mimetype=hyper_const.MASON + ";" +
                        hyper_const.FORUM_DIAGNOSIS_PROFILE)

    def post(self, diagnosis_id):
        """
        Adds a response to a diagnosis with id <diagnosis_id>.

        INPUT PARAMETERS:
       : param str diagnosis_id: The id of the diagnosis to be posted

        REQUEST ENTITY BODY:
        * Media type: JSON
         * Profile: Forum_Diagnosis
          /profiles/diagnosis-profile

        The body should be a JSON document that matches the schema for new diagnoses

        RESPONSE HEADERS:
         * Location: Contains the URL of the new diagnosis

        RESPONSE STATUS CODE:
         * Returns 201 if the diagnosis has been added correctly.
           The Location header contains the path of the new diagnosis
         * Returns 400 if the diagnosis is not well formed or empty diagnosis
         * Returns 404 if there is no diagnosis with diagnosis_id
         * Returns 415 if the format of the response is not json
         * Returns 500 if the diagnosis could not be added to database.

        NOTE:
         * The attribute disease is obtained from the column diagnoses.disease
         * The attribute diagnosis is obtained from the column diagnoses.diagnosis_description
         * The attribute message_id is obtained from the column diagnoses.message_id
         * The attribute user_id is obtained from the column diagnoses.user_id
        """

        # CHECK THAT MESSAGE EXISTS
        # If the diagnosis with diagnosis_id does not exist return status code 404
        if not g.con.contains_diagnosis(diagnosis_id):
            return create_error_response(
                404, "Diagnosis not found", "There is no a diagnosis with id %s" % diagnosis_id)

        if hyper_const.JSON != request.headers.get("Content-Type", ""):
            return create_error_response(
                415, "UnsupportedMediaType", "Use a JSON compatible format")
        request_body = request.get_json(force=True)
        # It throws a BadRequest exception, and hence a 400 code if the JSON is
        # not well-formed
        try:
            disease = request_body["disease"]
            diagnosis = request_body["diagnosis_description"]
            user_id = request_body.get("user_id")
            message_id = request_body.get("message_id")

        except KeyError:
            # This is launched if either title or body does not exist or if
            # the template.data array does not exist.
            return create_error_response(
                400, "Wrong request format", "Be sure you include diagnosis title and body")

        # Create the new diagnosis and build the response code"
        new_diagnosis_id = g.con.append_answer(
            user_id, message_id, disease, diagnosis)
        if not new_diagnosis_id:
            abort(500)

        # Create the Location header with the id of the diagnosis created
        url = API.url_for(Diagnosis, diagnosis_id=new_diagnosis_id)

        # RENDER
        # Return the response
        return Response(status=201, headers={"Location": url})
