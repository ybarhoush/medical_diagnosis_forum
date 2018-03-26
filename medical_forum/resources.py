# coding= utf-8
'''
Created on 26.01.2013
Modified on 26.03.2018
@author: mika oja
@author: ivan
@author: yazan
'''

import json

from urllib.parse import unquote

from flask import Flask, request, Response, g, _request_ctx_stack, redirect, send_from_directory
from flask_restful import Resource, Api, abort
from werkzeug.exceptions import NotFound, UnsupportedMediaType
from medical_forum.utils import RegexConverter
from medical_forum import database

# Constants for hypermedia formats and profiles
MASON = "application/vnd.mason+json"
JSON = "application/json"

FORUM_USER_PROFILE = "/profiles/user-profile/"
FORUM_MESSAGE_PROFILE = "/profiles/message-profile/"
FORUM_DIAGNOSIS_PROFILE = "/profiles/diagnosis-profile/"
ERROR_PROFILE = "/profiles/error-profile"

ATOM_THREAD_PROFILE = "https://tools.ietf.org/html/rfc4685"

STUDENT_APIARY_PROJECT = "https://pwpforumompletedversion.docs.apiary.io"
APIARY_PROFILES_URL = STUDENT_APIARY_PROJECT + "/#reference/profiles/"
APIARY_RELS_URL = STUDENT_APIARY_PROJECT + "/#reference/link-relations/"

USER_SCHEMA_URL = "/medical_forum/schema/user/"
PRIVATE_PROFILE_SCHEMA_URL = "/medical_forum/schema/private-profile/"
LINK_RELATIONS_URL = "/medical_forum/link-relations/"

# Define the application and the api
app = Flask(__name__, static_folder="static", static_url_path="/.")
app.debug = True
# Set the database Engine. In order to modify the database file (e.g. for
# testing) provide the database path   app.config to modify the
# database to be used (for instance for testing)
app.config.update({"Engine": database.Engine()})
# Start the REST-ful API.
api = Api(app)


# These two classes below are how we make producing the resource representation
# JSON documents manageable and resilient to errors. As noted, our mediatype is
# Mason. Similar solutions can easily be implemented for other mediatypes.
class MasonObject(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs


class ForumObject(MasonObject):
    """
    A convenience subclass of MasonObject that defines a bunch of shorthand
    methods for inserting application specific objects into the document. This
    class is particularly useful for adding control objects that are largely
    context independent, and defining them in the resource methods would add a
    lot of noise to our code - not to mention making inconsistencies much more
    likely!

    In the medical_forum code this object should always be used for root document as
    well as any items in a collection type resource.
    """

    def __init__(self, **kwargs):
        """
        Calls dictionary init method with any received keyword arguments. Adds
        the controls key afterwards because hypermedia without controls is not
        hypermedia.
        """

        super(ForumObject, self).__init__(**kwargs)
        self["@controls"] = {}

    def add_control_messages_all(self):
        """
        Adds the message-all link to an object. Intended for the document object.
        """

        self["@controls"]["medical_forum:messages-all"] = {
            "href": api.url_for(Messages),
            "title": "All messages"
        }

    # TODO def add_control_users_all(self):

    # TODO def add_control_diagnoses_all(self):

    def add_control_add_message(self):
        """
        This adds the add-message control to an object. Intended for the
        document object. Here you can see that adding the control is a bunch of
        lines where all we're basically doing is nested dictionaries to
        achieve the correctly formed JSON document representation.
        """

        self["@controls"]["medical_forum:add-message"] = {
            "href": api.url_for(Messages),
            "title": "Create message",
            "encoding": "json",
            "method": "POST",
            "schema": self._msg_schema()
        }

    # TODO def add_control_add_user(self):

    # TODO def add_control_add_diagnosis(self):

    def add_control_delete_message(self, msgid):
        """
        Adds the delete control to an object. This is intended for any
        object that represents a message.

        : param str msgid: message id in the msg-N form
        """

        self["@controls"]["medical_forum:delete"] = {
            "href": api.url_for(Message, message_id=msgid),
            "title": "Delete this message",
            "method": "DELETE"
        }

    # TODO def add_control_delete_user(self, username):

    # TODO def add_control_delete_diagnosis(self):

    def add_control_edit_message(self, msgid):
        """
        Adds a the edit control to a message object. For the schema we need
        the one that's intended for editing (it has editor instead of author).

        : param str msgid: message id in the msg-N form
        """

        self["@controls"]["edit"] = {
            "href": api.url_for(Message, message_id=msgid),
            "title": "Edit this message",
            "encoding": "json",
            "method": "PUT",
            "schema": self._msg_schema(edit=True)
        }

    # TODO def add_control_edit_public_profile(self, username):

    # TODO def add_control_edit_private_profile(self, username):

    # TODO def add_control_edit_diagnosis(self):

    def add_control_reply_to(self, msgid):
        """
        Adds a reply-to control to a message.

        : param str msgid: message id in the msg-N form
        """

        self["@controls"]["medical_forum:reply"] = {
            "href": api.url_for(Message, message_id=msgid),
            "title": "Reply to this message",
            "encoding": "json",
            "method": "POST",
            "schema": self._msg_schema()
        }

    # TODO def add_control_reply_to_diagnosis(self):

    # Schema

    def _msg_schema(self, edit=False):
        """
        Creates a schema dictionary for messages. If we're editing a message
        the editor field should be set. If the message is new, the author field
        should be set instead. This is controlled by the edit flag.

        This schema can also be accessed from the urls /forum/schema/edit-msg/ and
        /forum/schema/add-msg/.

        : param bool edit: is this schema for an edit form
        : rtype:: dict
        """

        if edit:
            user_field = "editor"
        else:
            user_field = "author"

        schema = {
            "type": "object",
            "properties": {},
            "required": ["headline", "articleBody"]
        }

        props = schema["properties"]
        props["headline"] = {
            "title": "Headline",
            "description": "Message headline",
            "type": "string"
        }
        props["articleBody"] = {
            "title": "Contents",
            "description": "Message contents",
            "type": "string"
        }
        props[user_field] = {
            "title": user_field.capitalize(),
            "description": "Name of the message {}".format(user_field),
            "type": "string"
        }
        return schema


# TODO def _public_profile_schema(self):
# TODO def _dgs_schema(self): -- we need to modify database.py; replace msg with dgs for diagnosis

# ERROR HANDLERS


def create_error_response(status_code, title, message=None):
    """
    Creates a: py: class:`flask.Response` instance when sending back an
    HTTP error response

    : param integer status_code: The HTTP status code of the response
    : param str title: A short description of the problem
    : param message: A long description of the problem
    : rtype:: py: class:`flask.Response`
    """

    resource_url = None
    # We need to access the context in order to access the request.path
    ctx = _request_ctx_stack.top
    if ctx is not None:
        resource_url = request.path
    envelope = MasonObject(resource_url=resource_url)
    envelope.add_error(title, message)

    return Response(json.dumps(envelope), status_code, mimetype=MASON + ";" + ERROR_PROFILE)


def create_error_response(status_code, title, message=None):
    """
    Creates a: py: class:`flask.Response` instance when sending back an
    HTTP error response

    : param integer status_code: The HTTP status code of the response
    : param str title: A short description of the problem
    : param message: A long description of the problem
    : rtype:: py: class:`flask.Response`
    """

    resource_url = None
    # We need to access the context in order to access the request.path
    ctx = _request_ctx_stack.top
    if ctx is not None:
        resource_url = request.path
    envelope = MasonObject(resource_url=resource_url)
    envelope.add_error(title, message)

    return Response(json.dumps(envelope), status_code, mimetype=MASON + ";" + ERROR_PROFILE)


@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, "Resource not found",
                                 "This resource url does not exit")


@app.errorhandler(400)
def resource_not_found(error):
    return create_error_response(400, "Malformed input format",
                                 "The format of the input is incorrect")


@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, "Error",
                                 "The system has failed. Please, contact the administrator")


@app.before_request
def connect_db():
    """
    Creates a database connection before the request is proccessed.

    The connection is stored in the application context variable flask.g .
    Hence it is accessible from the request object.
    """

    g.con = app.config["Engine"].connect()


# HOOKS
@app.teardown_request
def close_connection(exc):
    """
    Closes the database connection
    Check if the connection is created. It migth be exception appear before
    the connection is created.
    """

    if hasattr(g, "con"):
        g.con.close()


# Define the resources
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

        envelope = ForumObject()
        envelope.add_namespace("medical_forum", LINK_RELATIONS_URL)

        envelope.add_control("self", href=api.url_for(Messages))
        # TODO envelope.add_control_users_all()
        envelope.add_control_add_message()

        items = envelope["items"] = []

        for msg in messages_db:
            item = ForumObject(id=msg["message_id"], headline=msg["title"])
            item.add_control("self", href=api.url_for(Message, message_id=msg["message_id"]))
            item.add_control("profile", href=FORUM_MESSAGE_PROFILE)
            items.append(item)

        # RENDER
        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + FORUM_MESSAGE_PROFILE)

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

        if JSON != request.headers.get("Content-Type", ""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")
        request_body = request.get_json(force=True)
        # It throws a BadRequest exception, and hence a 400 code if the JSON is
        # not wellformed
        try:
            title = request_body["headline"]
            body = request_body["articleBody"]
            sender = request_body.get("author")
            ipaddress = request.remote_addr

        except KeyError:
            # This is launched if either title or body does not exist or if
            # the template.data array does not exist.
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include message title and body")
        # Create the new message and build the response code"
        newmessageid = g.con.create_message(title, body, sender, ipaddress)
        if not newmessageid:
            return create_error_response(500, "Problem with the database",
                                         "Cannot access the database")

        # Create the Location header with the id of the message created
        url = api.url_for(Message, message_id=newmessageid)

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

            Semantic descriptors used: articleBody, headline, editor and author
            NOTE: editor should not be included in the output if the database
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
        parent = message_db.get("replyto", None)

        # FILTER AND GENERATE RESPONSE
        # Create the envelope:
        envelope = ForumObject(
            headline=message_db["title"],
            articleBody=message_db["body"],
            author=sender,
            editor=message_db["editor"]
        )

        envelope.add_namespace("medical_forum", LINK_RELATIONS_URL)
        envelope.add_namespace("atom-thread", ATOM_THREAD_PROFILE)

        envelope.add_control_delete_message(message_id)
        envelope.add_control_edit_message(message_id)
        envelope.add_control_reply_to(message_id)
        envelope.add_control("profile", href=FORUM_MESSAGE_PROFILE)
        envelope.add_control("collection", href=api.url_for(Messages))
        envelope.add_control("self", href=api.url_for(Message, message_id=message_id))
        # TODO envelope.add_control("author", href=api.url_for(User, username=sender))

        if parent:
            envelope.add_control("atom-thread:in-reply-to", href=api.url_for(Message, message_id=parent))
        else:
            envelope.add_control("atom-thread:in-reply-to", href=None)

        # RENDER
        return Response(json.dumps(envelope), 200, mimetype=MASON + ";" + FORUM_MESSAGE_PROFILE)

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
                                         "There is no a message with id %s" % message_id
                                         )

    def put(self, message_id):
        """
        Modifies the title, body and editor properties of this message.

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
                                         "There is no a message with id %s" % message_id
                                         )

        if JSON != request.headers.get("Content-Type", ""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")
        request_body = request.get_json(force=True)
        # It throws a BadRequest exception, and hence a 400 code if the JSON is
        # not wellformed
        try:
            title = request_body["headline"]
            body = request_body["articleBody"]
            editor = request_body.get("editor")
            ipaddress = request.remote_addr

        except KeyError:
            # This is launched if either title or body does not exist or if
            # the template.data array does not exist.
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include message title and body")
        else:
            # Modify the message in the database
            if not g.con.modify_message(message_id, title, body, editor):
                return create_error_response(500, "Internal error",
                                             "Message information for %s cannot be updated" % message_id
                                             )
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
                                         "There is no a message with id %s" % message_id
                                         )

        if JSON != request.headers.get("Content-Type", ""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")
        request_body = request.get_json(force=True)
        # It throws a BadRequest exception, and hence a 400 code if the JSON is
        # not wellformed
        try:
            title = request_body["headline"]
            body = request_body["articleBody"]
            sender = request_body.get("author")
            ipaddress = request.remote_addr

        except KeyError:
            # This is launched if either title or body does not exist or if
            # the template.data array does not exist.
            return create_error_response(400, "Wrong request format",
                                         "Be sure you include message title and body")

        # Create the new message and build the response code"
        newmessageid = g.con.append_answer(message_id, title, body,
                                           sender, ipaddress)
        if not newmessageid:
            abort(500)

        # Create the Location header with the id of the message created
        url = api.url_for(Message, message_id=newmessageid)

        # RENDER
        # Return the response
        return Response(status=201, headers={"Location": url})

    # TODO class Users(Resource):
    # TODO class User(Resource):
    # TODO class User_public(Resource):
    # TODO class User_restricted(Resource):


# Add the Regex Converter so we can use regex expressions when we define the
# routes
app.url_map.converters["regex"] = RegexConverter

# Define the routes

api.add_resource(Messages, "/medical_forum/api/messages/",
                 endpoint="messages")
api.add_resource(Message, "/medical_forum/api/messages/<regex('msg-\d+'):message_id>/",
                 endpoint="message")


# TODO api.add_resource for User_public
# TODO api.add_resource for User_restricted
# TODO api.add_resource for Users
# TODO api.add_resource for User
# TODO api.add_resource for Diagnoses
# TODO api.add_resource for Diagnosis

# TODO Define the routes for diagnosis/diagnoses

# Redirect profile
@app.route("/profiles/<profile_name>/")
def redirect_to_profile(profile_name):
    return redirect(APIARY_PROFILES_URL + profile_name)


@app.route("/medical_forum/link-relations/<rel_name>/")
def redirect_to_rels(rel_name):
    return redirect(APIARY_RELS_URL + rel_name)


# Send our schema file(s)
@app.route("/medical_forum/schema/<schema_name>/")
def send_json_schema(schema_name):
    # return send_from_directory("static/schema", "{}.json".format(schema_name))
    return send_from_directory(app.static_folder, "schema/{}.json".format(schema_name))


# Start the application
# DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == '__main__':
    # Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
