"""
Messages and Message resource API implementation
"""

import json
from flask import request, Response, g
from flask_restful import Resource, abort

from .resources import API, hyper_const
from .error_handlers import create_error_response

from . import forum_object as forum_obj
from . import user_resources as user_res
from . import diagnosis_resources as diagnosis_res


class Messages(Resource):
    """
    Resource Messages implementation
    """

    def get(self):
        """
        Get all messages.

        INPUT parameters:
          None

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Forum_Message
          /profiles/message_profile

        NOTE:
         * The attribute articleBody is obtained from the column messages.body
         * The attribute headline is obtained from the column messages.title
         * The attribute author is obtained from the column messages.sender
        """

        # Extract messages from database
        messages_db = g.con.get_messages()

        envelope = forum_obj.ForumObject()
        envelope.add_namespace("medical_forum", hyper_const.LINK_RELATIONS_URL)

        envelope.add_control("self", href=API.url_for(Messages))
        envelope.add_control_users_all()
        envelope.add_control_add_message()

        items = envelope["items"] = []

        for msg in messages_db:
            item = forum_obj.ForumObject(
                id=msg["message_id"], headline=msg["title"])
            item.add_control("self", href=API.url_for(
                Message, message_id=msg["message_id"]))
            item.add_control("profile", href=hyper_const.FORUM_MESSAGE_PROFILE)
            items.append(item)

        return Response(json.dumps(envelope), 200, mimetype=hyper_const.MASON + ";" +
                        hyper_const.FORUM_MESSAGE_PROFILE)

    def post(self):
        """
        Adds a a new message.

        REQUEST ENTITY BODY:
         * Media type: JSON:
         * Profile: Forum_Message
          /profiles/message_profile

        NOTE:
         * The attribute articleBody is obtained from the column messages.body
         * The attribute headline is obtained from the column messages.title
         * The attribute author is obtained from the column messages.sender

        The body should be a JSON document that matches the schema for new messages

        RESPONSE STATUS CODE:
         * Returns 201 if the message has been added correctly.
           The Location header contains the path of the new message
         * Returns 400 if the message is not well formed or the entity body is
           empty.
         * Returns 415 if the format of the response is not json
         * Returns 500 if the message could not be added to database.

        """

        # Extract the request body. In general would be request.data
        # Since the request is JSON I use request.get_json
        # get_json returns a python dictionary after serializing the request body
        # get_json returns None if the body of the request is not formatted
        # using JSON. We use force=True since the input media type is not
        # application/json.

        if hyper_const.JSON != request.headers.get("Content-Type", ""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")
        request_body = request.get_json(force=True)
        # It throws a BadRequest exception, and hence a 400 code if the JSON is
        # not well-formed
        try:
            title = request_body["headline"]
            body = request_body["articleBody"]
            sender = request_body.get("author")

        except KeyError:
            # This is launched if either title or body does not exist or if
            # the template.data array does not exist.
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include message title and body")
        try:
            # Create the new message and build the response code"
            new_message_id = g.con.create_message(title, body, sender)

            if not new_message_id:
                return create_error_response(500, "Problem with the database",
                                             "Cannot access the database")
        except KeyError:
            return create_error_response(400, "Wrong request format",
                                         "Be sure to have the right request values or user_id")

        # Create the Location header with the id of the message created
        url = API.url_for(Message, message_id=new_message_id)

        # RENDER
        # Return the response
        return Response(status=201, headers={"Location": url})


class Message(Resource):
    """
    Resource that represents a single message in the API.
    """

    def get(self, message_id):
        """
        Get the body, the title and the id of a specific message.

        Returns status code 404 if the message_id does not exist in the database.

        INPUT PARAMETER
       : param str message_id: The id of the message to be retrieved from the
            system

        RESPONSE ENTITY BODY:
         * Media type: application/vnd.mason+json:
             https://github.com/JornWildt/Mason
         * Profile: Forum_Message
           /profiles/message-profile

            Link relations used: self, collection, author, replies and
            in-reply-to

            Semantic descriptors used: articleBody, headline
            return None.

        RESPONSE STATUS CODE
         * Return status code 200 if everything OK.
         * Return status code 404 if the message was not found in the database.

        NOTE:
         * The attribute articleBody is obtained from the column messages.body
         * The attribute headline is obtained from the column messages.title
         * The attribute author is obtained from the column messages.sender
        """

        # PEFORM OPERATIONS INITIAL CHECKS
        # Get the message from db
        message_db = g.con.get_message(message_id)
        if not message_db:
            abort(404, message="There is no a message with id %s" % message_id,
                  resource_type="Message",
                  resource_url=request.path,
                  resource_id=message_id)

        sender = message_db.get("sender")
        parent = message_db.get("reply_to", None)

        # FILTER AND GENERATE RESPONSE
        # Create the envelope:
        envelope = forum_obj.ForumObject(
            headline=message_db["title"],
            articleBody=message_db["body"],
            author=sender,
            reply_to=message_db["reply_to"],
            message_id=message_db["message_id"]
        )

        envelope.add_namespace("medical_forum", hyper_const.LINK_RELATIONS_URL)
        envelope.add_namespace("atom-thread", hyper_const.ATOM_THREAD_PROFILE)

        envelope.add_control_delete_message(message_id)
        envelope.add_control_edit_message(message_id)
        envelope.add_control_reply_to(message_id)
        envelope.add_control_add_diagnosis_with_user(
            user_id=message_db['user_id'])
        envelope.add_control("medical_forum:diagnoses-history-message",
                             href=API.url_for(diagnosis_res.DiagnosesHistoryMessage,
                                              message_id=message_id))

        envelope.add_control_delete_message(message_id=message_id)
        envelope.add_control("profile", href=hyper_const.FORUM_MESSAGE_PROFILE)
        envelope.add_control("collection", href=API.url_for(Messages))
        envelope.add_control("self", href=API.url_for(
            Message, message_id=message_id))
        envelope.add_control("author", href=API.url_for(
            user_res.User, username=sender))

        if parent:
            envelope.add_control("atom-thread:in-reply-to",
                                 href=API.url_for(Message, message_id=parent))
        else:
            envelope.add_control("atom-thread:in-reply-to", href=None)

        # RENDER
        return Response(json.dumps(envelope), 200, mimetype=hyper_const.MASON + ";" +
                        hyper_const.FORUM_MESSAGE_PROFILE)

    def delete(self, message_id):
        """
        Deletes a message from the medical_forum API.

        INPUT PARAMETERS:
       : param str message_id: The id of the message to be deleted

        RESPONSE STATUS CODE
         * Returns 204 if the message was deleted
         * Returns 404 if the message_id is not associated to any message.
        """

        # PERFORM DELETE OPERATIONS
        if g.con.delete_message(message_id):
            return "", 204
        else:
            # Send error message
            return create_error_response(404, "Unknown message",
                                         "There is no a message with id %s" % message_id)

    def put(self, message_id):
        """
        Modifies the title and body properties of this message.

        INPUT PARAMETERS:
       : param str message_id: The id of the message to be deleted

        REQUEST ENTITY BODY:
        * Media type: JSON

        * Profile: Forum_Message
          /profiles/message-profile

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
        * Profile: Forum_Message
          /profiles/message-profile

        The body should be a JSON document that matches the schema for editing messages

        OUTPUT:
         * Returns 204 if the message is modified correctly
         * Returns 400 if the body of the request is not well formed or it is
           empty.
         * Returns 404 if there is no message with message_id
         * Returns 415 if the input is not JSON.
         * Returns 500 if the database cannot be modified

        NOTE:
         * The attribute articleBody is obtained from the column messages.body
         * The attribute headline is obtained from the column messages.title
         * The attribute author is obtained from the column messages.sender
        """

        # CHECK THAT MESSAGE EXISTS
        if not g.con.contains_message(message_id):
            return create_error_response(404, "Message not found",
                                         "There is no a message with id %s" % message_id)

        if hyper_const.JSON != request.headers.get("Content-Type", ""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")
        request_body = request.get_json(force=True)
        # It throws a BadRequest exception, and hence a 400 code if the JSON is
        # not wellformed
        try:
            title = request_body["headline"]
            body = request_body["articleBody"]

        except KeyError:
            # This is launched if either title or body does not exist or if
            # the template.data array does not exist.
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include message title and body")
        else:
            # Modify the message in the database
            if not g.con.modify_message(message_id, title, body):
                return create_error_response(
                    500, "Internal error", "Message information for %s cannot be updated"
                    % message_id)
            return "", 204

    def post(self, message_id):
        """
        Adds a response to a message with id <message_id>.

        INPUT PARAMETERS:
       : param str message_id: The id of the message to be deleted

        REQUEST ENTITY BODY:
        * Media type: JSON
         * Profile: Forum_Message
          /profiles/message-profile

        The body should be a JSON document that matches the schema for new messages

        RESPONSE HEADERS:
         * Location: Contains the URL of the new message

        RESPONSE STATUS CODE:
         * Returns 201 if the message has been added correctly.
           The Location header contains the path of the new message
         * Returns 400 if the message is not well formed or the entity body is
           empty.
         * Returns 404 if there is no message with message_id
         * Returns 415 if the format of the response is not json
         * Returns 500 if the message could not be added to database.

         NOTE:
         * The attribute articleBody is obtained from the column messages.body
         * The attribute headline is obtained from the column messages.title
         * The attribute author is obtained from the column messages.sender
        """

        # CHECK THAT MESSAGE EXISTS
        # If the message with message_id does not exist return status code 404
        if not g.con.contains_message(message_id):
            return create_error_response(404, "Message not found",
                                         "There is no a message with id %s" % message_id)

        if hyper_const.JSON != request.headers.get("Content-Type", ""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")
        request_body = request.get_json(force=True)
        # It throws a BadRequest exception, and hence a 400 code if the JSON is
        # not well-formed
        try:
            title = request_body["headline"]
            body = request_body["articleBody"]
            sender = request_body.get("author")

        except KeyError:
            # This is launched if either title or body does not exist or if
            # the template.data array does not exist.
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include message title and body")

        # Create the new message and build the response code"
        new_message_id = g.con.append_answer(message_id, title, body, sender)
        if not new_message_id:
            abort(500)

        # Create the Location header with the id of the message created
        url = API.url_for(Message, message_id=new_message_id)

        # RENDER
        # Return the response
        return Response(status=201, headers={"Location": url})


class History(Resource):
    """
    Resource for messages history of a specific user
    """

    def get(self, username):
        """
            This method returns a list of messages that has been sent by an user
            and meet certain restrictions (result of an algorithm).
            The restrictions are given in the URL as query parameters.

            INPUT:
            The query parameters are:
             * length: the number of messages to return
             * after: the messages returned must have been modified after
                      the time provided in this parameter.
                      Time is UNIX timestamp
             * before: the messages returned must have been modified before the
                       time provided in this parameter. Time is UNIX timestamp

            RESPONSE STATUS CODE:
             * Returns 200 if the list can be generated and it is not empty
             * Returns 404 if no message meets the requirement

            RESPONSE ENTITY BODY:
            * Media type recommended: application/vnd.mason+json
            * Profile recommended: Forum_Message
                /profiles/message-profile

            Link relations used in items: None

            Semantic descriptions used in items: headline

            Link relations used in links: messages-all, author

            Semantic descriptors used in queries: after, before, length
        """

        parameters = request.args
        length = int(parameters.get('length', -1))
        before = int(parameters.get('before', -1))
        after = int(parameters.get('after', -1))

        messages_db = g.con.get_messages(username, length, before, after)
        if messages_db is None or not messages_db:
            return create_error_response(404, "Empty list",
                                         "Cannot find any message with the"
                                         " provided restrictions")
        envelope = forum_obj.ForumObject()
        envelope.add_namespace("forum", hyper_const.LINK_RELATIONS_URL)
        envelope.add_control("self", href=API.url_for(
            History, username=username))
        envelope.add_control(
            "author", href=API.url_for(user_res.User, username=username))
        envelope.add_control_messages_all()
        envelope.add_control_users_all()

        items = envelope["items"] = []

        for msg in messages_db:
            item = forum_obj.ForumObject(
                id=msg["message_id"], headline=msg["title"])
            item.add_control("self", href=API.url_for(
                Message, message_id=msg["message_id"]))
            item.add_control("profile", href=hyper_const.FORUM_MESSAGE_PROFILE)
            items.append(item)

        return Response(json.dumps(envelope), 200, mimetype=hyper_const.MASON+";" +
                        hyper_const.FORUM_MESSAGE_PROFILE)
