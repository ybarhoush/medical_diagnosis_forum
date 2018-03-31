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


class MessagesTestCase(ResourcesAPITestCase):
    url = "/medical_forum/api/messages/"

    existing_user_request = {
        "headline": "sad",
        "articleBody": "Tony bought new car. Anne bought new car. John bought new car. ",
        "author": "Chad"
    }

    non_existing_user_request = {
        "headline": "Can you help?",
        "articleBody": "I came here a months ago talking about the same problem in which i feel like ...",
        "author": "NoBodyKnows"
    }

    no_headline_wrong = {
        "articleBody": "I am not sure about my test results, I am here to ask for ...",
        "author": "Ellen"
    }

    no_body_wrong = {
        "headline": "Knee problems",
        "author": "Dizzy"
    }

    # Copied from test_url(self):
    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__, end=' ')
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Messages)

    # Modified from def test_get_messages(self):
    def test_get_messages(self):
        """
        Checks that GET Messages return correct status code and data format
        """
        print("(" + self.test_get_messages.__name__ + ")", self.test_get_messages.__doc__)

        # Check that I receive status code 200
        resp = self.client.get(flask.url_for("messages"))
        self.assertEqual(resp.status_code, 200)

        # Check that I receive a collection and adequate href
        data = json.loads(resp.data.decode("utf-8"))

        # Check controls
        controls = data["@controls"]
        self.assertIn("self", controls)
        self.assertIn("medical_forum:add-message", controls)
        # TODO self.assertIn("medical_forum:users-all", controls)

        self.assertIn("href", controls["self"])
        self.assertEqual(controls["self"]["href"], self.url)

        # TODO Check that users-all control is correct
        # users_ctrl = controls["forum:users-all"]
        # self.assertIn("title", users_ctrl)
        # self.assertIn("href", users_ctrl)
        # self.assertEqual(users_ctrl["href"], "/medical_forum/api/users/")

        # Check that add-message control is correct
        msg_ctrl = controls["medical_forum:add-message"]
        self.assertIn("title", msg_ctrl)
        self.assertIn("href", msg_ctrl)
        self.assertEqual(msg_ctrl["href"], "/medical_forum/api/messages/")
        self.assertIn("encoding", msg_ctrl)
        self.assertEqual(msg_ctrl["encoding"], "json")
        self.assertIn("method", msg_ctrl)
        self.assertEqual(msg_ctrl["method"], "POST")
        self.assertIn("schema", msg_ctrl)

        schema_data = msg_ctrl["schema"]
        self.assertIn("type", schema_data)
        self.assertIn("properties", schema_data)
        self.assertIn("required", schema_data)

        props = schema_data["properties"]
        self.assertIn("headline", props)
        self.assertIn("articleBody", props)
        self.assertIn("author", props)

        req = schema_data["required"]
        self.assertIn("headline", req)
        self.assertIn("articleBody", req)

        for key, value in list(props.items()):
            self.assertIn("description", value)
            self.assertIn("title", value)
            self.assertIn("type", value)
            self.assertEqual("string", value["type"])

    # Copied frm test_get_messages_mimetype(self)
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

    # Modified from test_add_message(self):
    def test_add_message(self):
        """
        Test adding messages to the database.
        """
        print("(" + self.test_add_message.__name__ + ")", self.test_add_message.__doc__)

        resp = self.client.post(resources.api.url_for(resources.Messages),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.existing_user_request)
                                )
        self.assertTrue(resp.status_code == 201)
        url = resp.headers.get("Location")
        self.assertIsNotNone(url)
        resp = self.client.get(url)
        self.assertTrue(resp.status_code == 200)

        # TODO fix database lock: def test_add_message(self): will try again after users is implemented
        # resp = self.client.post(resources.api.url_for(resources.Messages),
        #                         headers={"Content-Type": JSON},
        #                         data=json.dumps(self.non_existing_user_request)
        #                         )
        # self.assertTrue(resp.status_code == 201)
        # url = resp.headers.get("Location")
        # self.assertIsNotNone(url)
        # resp = self.client.get(url)
        # self.assertTrue(resp.status_code == 200)

    # def test_add_message_wrong_media(self):
    #     """
    #     Test adding messages with a media different than json
    #     """
    #     print("(" + self.test_add_message_wrong_media.__name__ + ")", self.test_add_message_wrong_media.__doc__)
    #     resp = self.client.post(resources.api.url_for(resources.Messages),
    #                             headers={"Content-Type": "text"},
    #                             data=self.message_1_request.__str__()
    #                             )
    #     self.assertTrue(resp.status_code == 415)

    # Modified from test_add_message_wrong_media(self):
    def test_add_message_wrong_media(self):
        """
        Test adding messages with a media different than json
        """
        print("(" + self.test_add_message_wrong_media.__name__ + ")", self.test_add_message_wrong_media.__doc__)
        resp = self.client.post(resources.api.url_for(resources.Messages),
                                headers={"Content-Type": "text"},
                                data=self.existing_user_request.__str__()
                                )
        self.assertTrue(resp.status_code == 415)

    # Modified from test_add_message_incorrect_format(self):
    def test_add_message_incorrect_format(self):
        """
        Test that add message response correctly when sending erroneous message
        format.
        """
        print("(" + self.test_add_message_incorrect_format.__name__ + ")",
              self.test_add_message_incorrect_format.__doc__)
        resp = self.client.post(resources.api.url_for(resources.Messages),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.no_headline_wrong)
                                )
        self.assertTrue(resp.status_code == 400)

        resp = self.client.post(resources.api.url_for(resources.Messages),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.no_body_wrong)
                                )
        self.assertTrue(resp.status_code == 400)


class MessageTestCase(ResourcesAPITestCase):
    message_req_1 = {
        "headline": "Soreness in the throat",
        "articleBody": "Hi, I have this soreness in my throat. It started just yesterday and its getting worse by "
                       "every hour. What should I do, and what is the cause of this. ",
        "author": "PoorGuy"
    }

    message_modify_req_1 = {
        "headline": "Dizziness when running",
        "articleBody": "Hi, I need help with this issue real quick. I get very dizzy when I run for few minutes. This "
                       "is being happening for like 2 weeks now. I really need help with this ! ",
        "author": "Dizzy",
        # "editor": "AxelW"
    }

    message_wrong_req_1 = {
        "headline": "Dizziness when running"
    }

    message_wrong_req_2 = {
        "articleBody": "Tony bought new car. John is shopping. Anne bought new car. ",
    }

    # Modified from def setUp(self):
    def setUp(self):
        super(MessageTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Message,
                                         message_id="msg-1",
                                         _external=False)
        self.url_wrong = resources.api.url_for(resources.Message,
                                               message_id="msg-290",
                                               _external=False)

    # Modified from def setUp(self):
    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        _url = "/medical_forum/api/messages/msg-1/"
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__)
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Message)

    # Copied from def setUp(self):
    def test_wrong_url(self):
        """
        Checks that GET Message return correct status code if given a
        wrong message
        """
        resp = self.client.get(self.url_wrong)
        self.assertEqual(resp.status_code, 404)

    # Modified from test_get_message(self):
    def test_get_message(self):
        """
        Checks that GET Message return correct status code and data format
        """
        print("(" + self.test_get_message.__name__ + ")", self.test_get_message.__doc__)
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data.decode("utf-8"))

            controls = data["@controls"]
            self.assertIn("self", controls)
            self.assertIn("profile", controls)
            self.assertIn("author", controls)
            self.assertIn("collection", controls)
            self.assertIn("edit", controls)
            self.assertIn("medical_forum:delete", controls)
            self.assertIn("medical_forum:reply", controls)
            self.assertIn("atom-thread:in-reply-to", controls)

            edit_ctrl = controls["edit"]
            self.assertIn("title", edit_ctrl)
            self.assertIn("href", edit_ctrl)
            self.assertEqual(edit_ctrl["href"], self.url)
            self.assertIn("encoding", edit_ctrl)
            self.assertEqual(edit_ctrl["encoding"], "json")
            self.assertIn("method", edit_ctrl)
            self.assertEqual(edit_ctrl["method"], "PUT")
            self.assertIn("schema", edit_ctrl)

            reply_ctrl = controls["medical_forum:reply"]
            self.assertIn("title", reply_ctrl)
            self.assertIn("href", reply_ctrl)
            self.assertEqual(reply_ctrl["href"], self.url)
            self.assertIn("encoding", reply_ctrl)
            self.assertEqual(reply_ctrl["encoding"], "json")
            self.assertIn("method", reply_ctrl)
            self.assertEqual(reply_ctrl["method"], "POST")
            self.assertIn("schema", reply_ctrl)

            # Test edit schema
            schema_data = edit_ctrl["schema"]
            self.assertIn("type", schema_data)
            self.assertIn("properties", schema_data)
            self.assertIn("required", schema_data)

            props = schema_data["properties"]
            self.assertIn("headline", props)
            self.assertIn("articleBody", props)
            # self.assertIn("editor", props)

            req = schema_data["required"]
            self.assertIn("headline", req)
            self.assertIn("articleBody", req)

            # Test reply schema
            schema_data = reply_ctrl["schema"]
            self.assertIn("type", schema_data)
            self.assertIn("properties", schema_data)
            self.assertIn("required", schema_data)

            props = schema_data["properties"]
            self.assertIn("headline", props)
            self.assertIn("articleBody", props)
            self.assertIn("author", props)

            req = schema_data["required"]
            self.assertIn("headline", req)
            self.assertIn("articleBody", req)

            self.assertIn("href", controls["self"])
            self.assertEqual(controls["self"]["href"], self.url)

            self.assertIn("href", controls["profile"])
            self.assertEqual(controls["profile"]["href"], FORUM_MESSAGE_PROFILE)
            # TODO test_get_message(self) -- author name AxelW not PoorGuy
            self.assertIn("href", controls["author"])
            self.assertEqual(controls["author"]["href"], resources.api.url_for(
                resources.User, username="PoorGuy", _external=False
            ))

            self.assertIn("href", controls["collection"])
            self.assertEqual(controls["collection"]["href"], resources.api.url_for(
                resources.Messages, _external=False
            ))

            self.assertIn("href", controls["atom-thread:in-reply-to"])
            self.assertEqual(controls["atom-thread:in-reply-to"]["href"], None)

            del_ctrl = controls["medical_forum:delete"]
            self.assertIn("href", del_ctrl)
            self.assertEqual(del_ctrl["href"], self.url)
            self.assertIn("method", del_ctrl)
            self.assertEqual(del_ctrl["method"], "DELETE")

            # Check rest attributes
            self.assertIn("articleBody", data)
            self.assertIn("author", data)
            self.assertIn("headline", data)
            # self.assertIn("editor", data)

    # Copied from def test_get_message_mimetype(self):
    def test_get_message_mimetype(self):
        """
        Checks that GET Messages return correct status code and data format
        """
        print("(" + self.test_get_message_mimetype.__name__ + ")", self.test_get_message_mimetype.__doc__)

        # Check that I receive status code 200
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type", None),
                         "{};{}".format(MASONJSON, FORUM_MESSAGE_PROFILE))

    # Copied from def test_add_reply_nonexisting_message(self):
    def test_add_reply_nonexisting_message(self):
        """
        Try to add a reply to an nonexisting message
        """
        print("(" + self.test_add_reply_nonexisting_message.__name__ + ")",
              self.test_add_reply_nonexisting_message.__doc__)
        resp = self.client.post(self.url_wrong,
                                data=json.dumps(self.message_req_1),
                                headers={"Content-Type": JSON})
        self.assertEqual(resp.status_code, 404)

    # Copied from def test_add_reply_wrong_message(self):
    def test_add_reply_wrong_message(self):
        """
        Try to add a reply to a message sending wrong data
        """
        print("(" + self.test_add_reply_wrong_message.__name__ + ")", self.test_add_reply_wrong_message.__doc__)
        resp = self.client.post(self.url,
                                data=json.dumps(self.message_wrong_req_1),
                                headers={"Content-Type": JSON})
        self.assertEqual(resp.status_code, 400)
        resp = self.client.post(self.url,
                                data=json.dumps(self.message_wrong_req_2),
                                headers={"Content-Type": JSON})
        self.assertEqual(resp.status_code, 400)

    # Copied from def test_add_reply_wrong_type(self):
    def test_add_reply_wrong_type(self):
        """
        Checks that returns the correct status code if the Content-Type is wrong
        """
        print("(" + self.test_add_reply_wrong_type.__name__ + ")", self.test_add_reply_wrong_type.__doc__)
        resp = self.client.post(self.url,
                                data=json.dumps(self.message_req_1),
                                headers={"Content-Type": "text/html"})
        self.assertEqual(resp.status_code, 415)

    # Modified from def test_add_reply(self):
    def test_add_reply(self):
        """
        Add a new message and check that I receive the same data
        """
        print("(" + self.test_add_reply.__name__ + ")", self.test_add_reply.__doc__)
        resp = self.client.post(self.url,
                                data=json.dumps(self.message_req_1),
                                headers={"Content-Type": JSON})
        self.assertEqual(resp.status_code, 201)
        self.assertIn("Location", resp.headers)
        message_url = resp.headers["Location"]
        # Check that the message is stored
        resp2 = self.client.get(message_url)
        self.assertEqual(resp2.status_code, 200)

    # Modified from def test_modify_message(self):
    def test_modify_message(self):
        """
        Modify an exsiting message and check that the message has been modified correctly in the server
        """
        print("(" + self.test_modify_message.__name__ + ")", self.test_modify_message.__doc__)
        resp = self.client.put(self.url,
                               data=json.dumps(self.message_modify_req_1),
                               headers={"Content-Type": JSON})
        self.assertEqual(resp.status_code, 204)
        # Check that the message has been modified
        resp2 = self.client.get(self.url)
        self.assertEqual(resp2.status_code, 200)
        data = json.loads(resp2.data.decode("utf-8"))
        # Check that the title and the body of the message has been modified with the new data
        self.assertEqual(data["headline"], self.message_modify_req_1["headline"])
        self.assertEqual(data["articleBody"], self.message_modify_req_1["articleBody"])

    # Modified from def test_modify_nonexisting_message(self):
    def test_modify_nonexisting_message(self):
        """
        Try to modify a message that does not exist
        """
        print("(" + self.test_modify_nonexisting_message.__name__ + ")", self.test_modify_nonexisting_message.__doc__)
        resp = self.client.put(self.url_wrong,
                               data=json.dumps(self.message_modify_req_1),
                               headers={"Content-Type": JSON})
        self.assertEqual(resp.status_code, 404)

    # Modified from def test_modify_wrong_message(self):
    def test_modify_wrong_message(self):
        """
        Try to modify a message sending wrong data
        """
        print("(" + self.test_modify_wrong_message.__name__ + ")", self.test_modify_wrong_message.__doc__)
        resp = self.client.put(self.url,
                               data=json.dumps(self.message_wrong_req_1),
                               headers={"Content-Type": JSON})
        self.assertEqual(resp.status_code, 400)
        resp = self.client.put(self.url,
                               data=json.dumps(self.message_wrong_req_2),
                               headers={"Content-Type": JSON})
        self.assertEqual(resp.status_code, 400)

    # Modified from def test_delete_message(self):
    def test_delete_message(self):
        """
        Checks that Delete Message return correct status code if corrected delete
        """
        print("(" + self.test_delete_message.__name__ + ")", self.test_delete_message.__doc__)
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)
        resp2 = self.client.get(self.url)
        self.assertEqual(resp2.status_code, 404)

    # Modified from def test_delete_nonexisting_message(self):
    def test_delete_nonexisting_message(self):
        """
        Checks that Delete Message return correct status code if given a wrong address
        """
        print("(" + self.test_delete_nonexisting_message.__name__ + ")", self.test_delete_nonexisting_message.__doc__)
        resp = self.client.delete(self.url_wrong)
        self.assertEqual(resp.status_code, 404)


# TODO class MessageTestCase (ResourcesAPITestCase):
# TODO class UsersTestCase (ResourcesAPITestCase):
# TODO class UserTestCase (ResourcesAPITestCase):
# TODO class DiagnosesTestCase (ResourcesAPITestCase):
# TODO class DiagnosisTestCase (ResourcesAPITestCase):


if __name__ == "__main__":
    print("Start running tests")
    unittest.main()
