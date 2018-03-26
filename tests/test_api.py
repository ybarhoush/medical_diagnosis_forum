"""
Created on 26.01.2013
Modified on 26.03.2017
@author: ivan sanchez
@author: mika oja
@author: yazan barhoush
"""
import unittest, copy
import json

import flask

import medical_forum.resources as resources
import medical_forum.database as database

# Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/medical_forum_data_test.db'
DEFAULT_SCHEMA = "db/medical_forum_data_schema.sql"
DEFAULT_DATA_DUMP = "db/medical_forum_data_dump.sql"

ENGINE = database.Engine(DEFAULT_DB_PATH)

MASONJSON = "application/vnd.mason+json"
JSON = "application/json"
HAL = "application/hal+json"
FORUM_USER_PROFILE = "/profiles/user-profile/"
FORUM_MESSAGE_PROFILE = "/profiles/message-profile/"
ATOM_THREAD_PROFILE = "https://tools.ietf.org/html/rfc4685"

# Tell Flask that I am running it in testing mode.
resources.app.config["TESTING"] = True
# Necessary for correct translation in url_for
resources.app.config["SERVER_NAME"] = "localhost:5000"

# Database Engine utilized in our testing
resources.app.config.update({"Engine": ENGINE})

# Other database parameters.
initial_messages = 19
initial_users = 25


# Copied Class ResourcesAPITestCase from Ex. 4
class ResourcesAPITestCase(unittest.TestCase):
    # INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        """ Creates the database structure. Removes first any preexisting
            database file
        """
        print("Testing ", cls.__name__)
        ENGINE.remove_database()
        ENGINE.create_tables()

    @classmethod
    def tearDownClass(cls):
        """Remove the testing database"""
        print("Testing ENDED for ", cls.__name__)
        ENGINE.remove_database()

    def setUp(self):
        """
        Populates the database
        """
        # This method load the initial values from forum_data_dump.sql
        ENGINE.populate_tables()
        # Activate app_context for using url_for
        self.app_context = resources.app.app_context()
        self.app_context.push()
        # Create a test client
        self.client = resources.app.test_client()

    def tearDown(self):
        """
        Remove all records from database
        """
        ENGINE.clear()
        self.app_context.pop()


# TODO class MessagesTestCase (ResourcesAPITestCase):
class MessagesTestCase(ResourcesAPITestCase):
    url = "/medical_forum/api/messages/"

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__, end=' ')
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Messages)

    # TODO def test_get_messages(self):

    def test_get_messages_mimetype(self):
        """
        Checks that GET Messages return correct status code and data format
        """
        print("(" + self.test_get_messages_mimetype.__name__ + ")", self.test_get_messages_mimetype.__doc__)

        # Check that I receive status code 200
        resp = self.client.get(flask.url_for("messages"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type", None),
                         "{};{}".format(MASONJSON, FORUM_MESSAGE_PROFILE))

    # TODO def test_add_message(self):
    # TODO def test_add_message_wrong_media(self):


# TODO class MessageTestCase(ResourcesAPITestCase):
# TODO class MessageTestCase (ResourcesAPITestCase):
# TODO class UsersTestCase (ResourcesAPITestCase):
# TODO class UserTestCase (ResourcesAPITestCase):
# TODO class DiagnosesTestCase (ResourcesAPITestCase):
# TODO class DiagnosisTestCase (ResourcesAPITestCase):


if __name__ == "__main__":
    print("Start running tests")
    unittest.main()
