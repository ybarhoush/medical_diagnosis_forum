"""
ForumObject class
"""

from .resources import API
from .mason_object import MasonObject
from . import hypermedia_formats as hyper_const
from . import user_resources as user_res
from . import profile_resources as profile_res
from . import message_resources as message_res
from . import diagnosis_resources as diagnosis_res


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
            "href": API.url_for(message_res.Messages),
            "title": "All messages"
        }

    # Copied from add_control_users_all
    def add_control_users_all(self):
        """
        This adds the users-all link to an object. Intended for the document object.
        """

        self["@controls"]["medical_forum:users-all"] = {
            "href": API.url_for(user_res.Users),
            "title": "List users"
        }

    def add_control_diagnoses_all(self):
        """
        Adds the diagnosis-all link to an object. Intended for the document object.
        """

        self["@controls"]["medical_forum:diagnoses-all"] = {
            "href": API.url_for(diagnosis_res.Diagnoses),
            "title": "All diagnoses"
        }

    def add_control_add_message(self):
        """
        This adds the add-message control to an object. Intended for the
        document object. Here you can see that adding the control is a bunch of
        lines where all we're basically doing is nested dictionaries to
        achieve the correctly formed JSON document representation.
        """

        self["@controls"]["medical_forum:add-message"] = {
            "href": API.url_for(message_res.Messages),
            "title": "Create message",
            "encoding": "json",
            "method": "POST",
            "schema": self._msg_schema()
        }

    # copied from def add_control_add_user(self)
    def add_control_add_user(self):
        """
        This adds the add-user control to an object. Intended for the
        document object. Instead of adding a schema dictionary we are pointing
        to a schema url instead for two reasons: 1) to demonstrate both options;
        2) the user schema is relatively large.
        """

        self["@controls"]["medical_forum:add-user"] = {
            "href": API.url_for(user_res.Users),
            "title": "Create user",
            "encoding": "json",
            "method": "POST",
            "schemaUrl": hyper_const.USER_SCHEMA_URL
        }

    def add_control_add_diagnosis(self):
        """
        This adds the add-diagnosis control to an object. Intended for the
        document object. Here you can see that adding the control is a bunch of
        lines where all we're basically doing is nested dictionaries to
        achieve the correctly formed JSON document representation.
        """

        self["@controls"]["medical_forum:add-diagnosis"] = {
            "href": API.url_for(diagnosis_res.Diagnoses),
            "title": "Create diagnosis",
            "encoding": "json",
            "method": "POST",
            "schema": self._dgs_schema()
        }

    def add_control_delete_message(self, msgid):
        """
        Adds the delete control to an object. This is intended for any
        object that represents a message.

        : param str msgid: message id in the msg-N form
        """

        self["@controls"]["medical_forum:delete"] = {
            "href": API.url_for(message_res.Message, message_id=msgid),
            "title": "Delete this message",
            "method": "DELETE"
        }

    # copied from def add_control_delete_user(self, username):
    def add_control_delete_user(self, username):
        """
        Adds the delete control to an object. This is intended for any
        object that represents a user.

        : param str username: The username of the user to remove
        """

        self["@controls"]["forum:delete"] = {
            "href": API.url_for(user_res.User, username=username),
            "title": "Delete this user",
            "method": "DELETE"
        }

    def add_control_edit_message(self, msg_id):
        """
        Adds a the edit control to a message object. For the schema we need
        the one that's intended for editing

        : param str msgid: message id in the msg-N form
        """

        self["@controls"]["edit"] = {
            "href": API.url_for(message_res.Message, message_id=msg_id),
            "title": "Edit this message",
            "encoding": "json",
            "method": "PUT",
            "schema": self._msg_schema(edit=True)
        }

    # copied from def add_control_edit_public_profile(self, username):
    def add_control_edit_public_profile(self, username):
        """
        Adds the edit control to a public profile object. Editing a public
        profile uses a limited version of the full user schema.

        : param str username: username of the user whose profile is edited
        """

        self["@controls"]["edit"] = {
            "href": API.url_for(profile_res.UserPublic, username=username),
            "title": "Edit this public profile",
            "encoding": "json",
            "method": "PUT",
            "schema": self._public_profile_schema()
        }

    # copied from def add_control_edit_private_profile(self, username)
    def add_control_edit_private_profile(self, username):
        """
        Adds the edit control to a private profile object. Editing a private
        profile uses large subset of the user schema, so we're just going to
        use a URL this time.

        : param str username: username of the user whose profile is edited
        """

        self["@controls"]["edit"] = {
            "href": API.url_for(profile_res.UserRestricted, username=username),
            "title": "Edit this private profile",
            "encoding": "json",
            "method": "PUT",
            "schemaUrl": hyper_const.PRIVATE_PROFILE_SCHEMA_URL
        }

    def add_control_reply_to(self, msgid):
        """
        Adds a reply-to control to a message.

        : param str msgid: message id in the msg-N form
        """

        self["@controls"]["medical_forum:reply"] = {
            "href": API.url_for(message_res.Message, message_id=msgid),
            "title": "Reply to this message",
            "encoding": "json",
            "method": "POST",
            "schema": self._msg_schema()
        }

    # TODO def add_control_reply_to_diagnosis(self) --Not Used
    def add_control_reply_to_diagnosis(self, dgsid):
        """
        Adds a reply-to control to a diagnosis.

        : param str dgsid: diagnosis id in the dgs-N form
        """

        self["@controls"]["medical_forum:reply"] = {
            "href": API.url_for(diagnosis_res.Diagnosis, diagnosis_id=dgsid),
            "title": "Reply to this diagnosis",
            "encoding": "json",
            "method": "POST",
            "schema": self._dgs_schema()
        }

    # Schema
    def _msg_schema(self, edit=False):
        """
        Creates a schema dictionary for messages.

        This schema can also be accessed from the urls /medical_forum/schema/edit-msg/ and
        /medical_forum/schema/add-msg/.

        : param bool edit: is this schema for an edit form
        : rtype:: dict
        """

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

    def _dgs_schema(self, edit=False):
        """
        Creates a schema dictionary for diagnoses.

        This schema can also be accessed from the urls /medical_forum/schema/edit-dgs/ and
        /medical_forum/schema/add-dgs/.

        : param bool edit: is this schema for an edit form
        : rtype:: dict
        """

        user_id = "user_id"

        schema = {
            "type": "object",
            "properties": {},
            "required": ["disease", "diagnosis_description"]
        }

        props = schema["properties"]

        props["disease"] = {
            "title": "disease",
            "description": "diagnosis disease",
            "type": "string"
        }
        props["diagnosis_description"] = {
            "title": "diagnosis description",
            "description": "diagnosis description",
            "type": "string"
        }

        props[user_id] = {
            "title": user_id,
            "description": "user_ide {}".format(user_id),
            "type": "Integer"
        }
        return schema

    def _public_profile_schema(self):
        """
        Creates a schema dictionary for editing public profiles of users.

        :rtype:: dict
        """

        schema = {
            "type": "object",
            "properties": {},
            "required": ["lastname", "picture"]
        }

        props = schema["properties"]
        props["signature"] = {
            "description": "User's signature",
            "title": "Signature",
            "type": "string"
        }

        props["picture"] = {
            "description": "image file location",
            "title": "picture",
            "type": "string"
        }

        return schema
