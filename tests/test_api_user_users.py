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
ATOM_THREAD_PROFILE = "https://tools.ietf.org/html/rfc4685"

# Tell Flask that I am running it in testing mode.
resources.app.config["TESTING"] = True
# Necessary for correct translation in url_for
resources.app.config["SERVER_NAME"] = "localhost:5000"

# Database Engine utilized in our testing
resources.app.config.update({"Engine": ENGINE})

# Other database parameters.
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


class UsersTestCase(ResourcesAPITestCase):
    PATIENT_USERNAME = 'PoorGuy'
    PATIENT_ID = 1
    DOCTOR_USERNAME = 'Clarissa'
    DOCTOR_ID = 4
    NEW_PATIENT_USERNAME = 'sully'

    user_1_request = {
        'reg_date': 1785505926,
        'username': NEW_PATIENT_USERNAME,
        'speciality': '',
        'user_type': 0,
        'firstname': 'PoorGuy',
        'lastname': 'Jackie',
        'work_address': '85 South White Oak Way',
        'gender': 'female',
        'picture': '192.219/dab/image.png',
        'age': 36,
        'email': 'vpid7@-zbe--.net'
    }

    # With just mandatory parameters
    user_2_request = {
        'reg_date': 1785505926,
        'username': 'anotheruser',
        'speciality': '',
        'user_type': 0,
        'firstname': 'PoorGuy',
        'lastname': 'Tell',
        'work_address': '54 Middle White Park',
        # 'gender': 'female',
        'picture': '192.219/dab/image45.png',
        # 'age': 36,
        # 'email': 'modified@email.net'
    }

    # Existing username
    user_wrong_1_request = {
        'reg_date': 1785505926,
        'username': PATIENT_USERNAME,
        'speciality': '',
        'user_type': 0,
        'firstname': 'PoorGuy',
        'lastname': 'Jackie',
        'work_address': '85 South White Oak Way',
        'gender': 'female',
        'picture': '192.219/dab/image.png',
        'age': 36,
        'email': 'vpid7@-zbe--.net'
    }

    # Missing username
    user_wrong_2_request = {
        'reg_date': 715581063,
        # 'username': DOCTOR_USERNAME,
        'speciality': 'head',
        'user_type': 1,
        'firstname': 'Clarissa',
        'lastname': 'Guadalupe',
        'work_address': '47 West Rocky Hague Road',
        'gender': 'female',
        'picture': '192.219/dab/image.png',
        'age': 27,
        'email': 'pbxim@f-hq--.com'
    }

    # Missing mandatory.
    user_wrong_3_request = {
        'reg_date': 1785505926,
        'username': PATIENT_USERNAME,
        'speciality': '',
        'user_type': 0,
        'firstname': 'PoorGuy',
        # 'lastname': 'Tell',
        'work_address': '54 Middle White Park',
        'gender': 'female',
        'picture': '192.219/dab/image45.png',
        'age': 36,
        'email': 'modified@email.net'
    }

    def setUp(self):
        super(UsersTestCase, self).setUp()
        self.url = resources.api.url_for(resources.Users,
                                         _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        # NOTE: self.shortDescription() should work.
        _url = "/medical_forum/api/users/"
        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__, end=' ')
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.Users)

    def test_get_users(self):
        """
        Checks that GET users return correct status code and data format
        """
        print
        "(" + self.test_get_users.__name__ + ")", self.test_get_users.__doc__
        # Check that I receive status code 200
        resp = self.client.get(flask.url_for("users"))
        self.assertEquals(resp.status_code, 200)

        # Check that I receive a collection and adequate href
        data = json.loads(resp.data)

        controls = data["@controls"]
        self.assertIn("self", controls)
        # ToDo self.assertIn("medical_forum:add-user", controls)
        self.assertIn("medical_forum:messages-all", controls)

        self.assertIn("href", controls["self"])
        self.assertEquals(controls["self"]["href"], self.url)

        msgs_ctrl = controls["medical_forum:messages-all"]
        self.assertIn("href", msgs_ctrl)
        self.assertEquals(msgs_ctrl["href"], "/medical_forum/api/messages/")
        self.assertIn("title", msgs_ctrl)

        # ToDo add_ctrl = controls["medical_forum:add-user"]
        # add_ctrl = controls["medical_forum:add-user"]
        # self.assertIn("href", add_ctrl)
        # self.assertEquals(add_ctrl["href"], "/medical_forum/api/users/")
        # self.assertIn("encoding", add_ctrl)
        # self.assertEquals(add_ctrl["encoding"], "json")
        # self.assertIn("method", add_ctrl)
        # self.assertEquals(add_ctrl["method"], "POST")
        # self.assertIn("title", add_ctrl)
        # self.assertIn("schemaUrl", add_ctrl)
        # self.assertEquals(add_ctrl["schemaUrl"], "/medical_forum/schema/user/")

        items = data["items"]
        self.assertEquals(len(items), initial_users)
        for item in items:
            self.assertIn("username", item)
            self.assertIn("reg_date", item)
            self.assertIn("@controls", item)
            self.assertIn("self", item["@controls"])
            self.assertIn("href", item["@controls"]["self"])
            self.assertEquals(item["@controls"]["self"]["href"],
                              resources.api.url_for(resources.User, username=item["username"], _external=False))
            self.assertIn("profile", item["@controls"])
            self.assertEquals(item["@controls"]["profile"]["href"], FORUM_USER_PROFILE)

    def test_get_users_mimetype(self):
        """
        Checks that GET Messages return correct status code and data format
        """
        print("(" + self.test_get_users_mimetype.__name__ + ")", self.test_get_users_mimetype.__doc__)

        # Check that I receive status code 200
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type", None),
                         "{};{}".format(MASONJSON, FORUM_USER_PROFILE))

    def test_add_user(self):
        """
        Checks that the user is added correctly

        """
        print("(" + self.test_add_user.__name__ + ")", self.test_add_user.__doc__)

        # With a complete request
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.user_1_request)
                                )
        self.assertEqual(resp.status_code, 201)
        self.assertIn("Location", resp.headers)
        url = resp.headers["Location"]
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 200)

        # ToDo With just mandatory parameters
        # resp = self.client.post(resources.api.url_for(resources.Users),
        #                         headers={"Content-Type": JSON},
        #                         data=json.dumps(self.user_2_request)
        #                         )
        # self.assertEqual(resp.status_code, 201)
        # self.assertIn("Location", resp.headers)
        # url = resp.headers["Location"]
        # resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 200)

    def test_add_user_missing_mandatory(self):
        """
        Test that it returns error when is missing a mandatory data
        """
        print("(" + self.test_add_user_missing_mandatory.__name__ + ")", self.test_add_user_missing_mandatory.__doc__)

        # Removing username
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.user_wrong_2_request)
                                )
        self.assertEqual(resp.status_code, 400)

        # ToDo Removing lastname
        # resp = self.client.post(resources.api.url_for(resources.Users),
        #                         headers={"Content-Type": JSON},
        #                         data=json.dumps(self.user_wrong_3_request)
        #                         )
        # self.assertEqual(resp.status_code, 400)

    def test_add_existing_user(self):
        """
        Testign that trying to add an existing user will fail

        """
        print("(" + self.test_add_existing_user.__name__ + ")", self.test_add_existing_user.__doc__)
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.user_wrong_1_request)
                                )
        self.assertEqual(resp.status_code, 409)

    def test_wrong_type(self):
        """
        Test that return adequate error if sent incorrect mime type
        """
        print("(" + self.test_wrong_type.__name__ + ")", self.test_wrong_type.__doc__)
        resp = self.client.post(resources.api.url_for(resources.Users),
                                headers={"Content-Type": "text/html"},
                                data=json.dumps(self.user_1_request)
                                )
        self.assertEqual(resp.status_code, 415)


class UserTestCase(ResourcesAPITestCase):

    def setUp(self):
        super(UserTestCase, self).setUp()
        user1_username = "AxelW"
        user2_usernmae = "Jacobino"
        self.url1 = resources.api.url_for(resources.User,
                                          username=user1_username,
                                          _external=False)
        self.url_wrong = resources.api.url_for(resources.User,
                                               username=user2_usernmae,
                                               _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """

        print("(" + self.test_url.__name__ + ")", self.test_url.__doc__)
        url = "/medical_forum/api/users/AxelW/"
        with resources.app.test_request_context(url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEqual(view_point, resources.User)

    # TODO Implement delete


if __name__ == "__main__":
    print("Start running tests")
    unittest.main()
