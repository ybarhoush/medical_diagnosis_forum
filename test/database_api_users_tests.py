"""
Created on 24.02.2018

Database API testing unit for users related methods from medical_forum/database.py.

@author: Issam
"""

# Importing required modules
import unittest
# import helper different methods
from .utils import *

# Users constants
PATIENT_USERNAME = 'PoorGuy'
PATIENT_ID = 1
PATIENT = {'public_profile': {'reg_date': 1785505926,
                              'username': PATIENT_USERNAME,
                              'speciality': '',
                              'user_type': 0},
           'restricted_profile': {'firstname': 'PoorGuy',
                                  'lastname': 'Jackie',
                                  'work_address': '85 South White Oak Way',
                                  'gender': 'female',
                                  'picture': '192.219/dab/image.png',
                                  'age': 36}
           }

MODIFIED_PATIENT = {'public_profile': {'reg_date': 1785505926,
                                       'username': PATIENT_USERNAME,
                                       'speciality': '',
                                       'user_type': 0},
                    'restricted_profile': {'firstname': 'PoorGuy',
                                           'lastname': 'Tell',
                                           'work_address': '54 Middle White Park',
                                           'gender': 'female',
                                           'picture': '192.219/dab/image45.png',
                                           'age': 36}
                    }

DOCTOR_USERNAME = 'Clarissa'
DOCTOR_ID = 4
DOCTOR = {'public_profile': {'reg_date': 715581063,
                             'username': DOCTOR_USERNAME,
                             'speciality': 'head',
                             'user_type': 1},
          'restricted_profile': {'firstname': 'Clarissa',
                                 'lastname': 'Guadalupe',
                                 'work_address': '47 West Rocky Hague Road',
                                 'gender': 'female',
                                 'picture': '192.219/dab/image.png',
                                 'age': 27}
          }

NEW_PATIENT_USERNAME = 'sully'
NEW_PATIENT = {'public_profile': {'reg_date': 1362012548,
                                  'username': NEW_PATIENT_USERNAME,
                                  'speciality': '',
                                  'user_type': 0},
               'restricted_profile': {'firstname': 'sully',
                                      'lastname': 'stolen',
                                      'work_address': '89 North White Oak Way',
                                      'gender': 'male',
                                      'picture': '',
                                      'age': 40},
               'pass_hash': 'testPass'  # TODO we will add hashing creation logic later
               }

NON_EXIST_PATIENT_USERNAME = 'SuperBoy'
NON_EXIST_DOCTOR_USERNAME = 'VirusKiller'


class DatabaseUsersTestCase(unittest.TestCase):
    """
    Test cases for different database users and users profile methods
    """

    # following resources were used for setUpClass and tearDownClass, setUpDB and tearDownDB
    # Exercise 1 and https://docs.python.org/3/library/unittest.html#setupclass-and-teardownclass
    # Setup method
    @classmethod
    def setUpClass(cls):
        """ Remove the database structure from previous sessions and create tables again """
        print("Testing started for: ", cls.__name__)
        ENGINE.remove_database()
        # Create all DB tables
        ENGINE.create_tables()

    # TeaDown method
    @classmethod
    def tearDownClass(cls):
        """ Remove the testing database """
        print("Testing has ENDED for: ", cls.__name__)
        ENGINE.remove_database()

    def setUp(self):
        """ Populates the database tables with data """
        try:
            # Get default data from medical_forum_data_dump.sql, populate tables and connect to DB
            ENGINE.populate_tables()
            self.connection = ENGINE.connect()

        # In case of error/exception in populating tables, clear all tables data
        except Exception as e:
            print(e)
            ENGINE.clear()

    def tearDown(self):
        """ Terminate active database connection and clear tables records (keep structure) """
        self.connection.close()
        ENGINE.clear()

    def test_users_table_populated(self):
        """
        Check that the users table has been populated with default data successfully.
         """
        print('(' + self.test_users_table_populated.__name__ + ')', self.test_users_table_populated.__doc__)
        test_table_populated(self, USERS_TABLE, INITIAL_USERS_COUNT)

    def test_users_profile_table_populated(self):
        """
        Check that the users_profile table has been populated with default data successfully.
         """
        print('(' + self.test_users_profile_table_populated.__name__ + ')',
              self.test_users_profile_table_populated.__doc__)
        test_table_populated(self, USERS_PROFILE_TABLE, INITIAL_USERS_PROFILE_COUNT)

    def test_create_user_object(self):
        """
        Check that the method create_user_object works return proper values.
        """
        print('(' + self.test_create_user_object.__name__+')', self.test_create_user_object.__doc__)
        # Query to get users and users_profile for the patient
        query = 'SELECT users.*, users_profile.* FROM users, users_profile \
                 WHERE users.user_id = users_profile.user_id'
        # assert if result doesn't contain patient
        self.assertDictContainsSubset(self.connection._create_user_object(execute_query(self, query, 'one')), PATIENT)

    def test_get_user(self):
        """
        Test get_user for patient with username PoorGuy and doctor with username Clarissa
        """
        print('(' + self.test_get_user.__name__+')', self.test_get_user.__doc__)
        # test for patient
        self.assertDictContainsSubset(self.connection.get_user(PATIENT_USERNAME), PATIENT)
        # test for doctor
        self.assertDictContainsSubset(self.connection.get_user(DOCTOR_USERNAME), DOCTOR)

    def test_get_user_non_exist_id(self):
        """
        Test get_user with  msg-200 (no-existing)
        """
        print('(' + self.test_get_user_non_exist_id.__name__+')', self.test_get_user_non_exist_id.__doc__)
        self.assertIsNone(self.connection.get_user(NON_EXIST_PATIENT_USERNAME))

    def test_get_users(self):
        """
        Test that get_users work correctly and extract required user info
        """
        print('(' + self.test_get_users.__name__+')', self.test_get_users.__doc__)
        users = self.connection.get_users()
        # Check we get right size of users table
        self.assertEqual(len(users), INITIAL_USERS_COUNT)
        # check PATIENT and DOCTOR data with users object we got
        for user in users:
            if user['username'] == PATIENT_USERNAME:
                self.assertDictContainsSubset(user, PATIENT['public_profile'])
            elif user['username'] == DOCTOR_USERNAME:
                self.assertDictContainsSubset(user, DOCTOR['public_profile'])

    # TODO not working
    def test_delete_user(self):
        """
        Test that the user PoorGuy is deleted
        """
        print('(' + self.test_delete_user.__name__+')', self.test_delete_user.__doc__)
        # check delete user is successful
        self.assertTrue(self.connection.delete_user(PATIENT_USERNAME))
        # ask to get user and check if it was really deleted
        self.assertIsNone(self.connection.get_user(PATIENT_USERNAME))
        # Check that the user does not have associated any message
        self.assertEqual(len(self.connection.get_messages(PATIENT_USERNAME)), 0)

    def test_delete_user_non_exist_username(self):
        """
        Test delete_user with  SuperBoy (no-existing patient)
        """
        print('(' + self.test_delete_user_non_exist_username.__name__+')',
              self.test_delete_user_non_exist_username.__doc__)
        self.assertFalse(self.connection.delete_user(NON_EXIST_PATIENT_USERNAME))

    def test_modify_user(self):
        """
        Test that the user PoorGuy is modified
        """
        print('(' + self.test_modify_user.__name__+')', self.test_modify_user.__doc__)
        # modify the user with provided user dict
        modify_resp = self.connection.modify_user(PATIENT_USERNAME, MODIFIED_PATIENT['public_profile'],
                                                  MODIFIED_PATIENT['restricted_profile'])
        self.assertEqual(modify_resp, PATIENT_USERNAME)
        # check each value in the profile with the modified one, see if modification successful
        # get the get_user response
        get_resp = self.connection.get_user(PATIENT_USERNAME)
        resp_r_profile = get_resp['restricted_profile']
        r_profile = MODIFIED_PATIENT['restricted_profile']
        self.assertEqual(r_profile['firstname'], resp_r_profile['firstname'])
        self.assertEqual(r_profile['lastname'], resp_r_profile['lastname'])
        self.assertEqual(r_profile['work_address'], resp_r_profile['work_address'])
        self.assertEqual(r_profile['gender'], resp_r_profile['gender'])
        self.assertEqual(r_profile['picture'], resp_r_profile['picture'])
        self.assertEqual(r_profile['age'], resp_r_profile['age'])
        self.assertDictContainsSubset(get_resp, MODIFIED_PATIENT)

    def test_modify_user_non_exist_username(self):
        """
        Test modify_user with  user SuperBoy (no-existing)
        """
        print('(' + self.test_modify_user_non_exist_username.__name__+')', self.test_modify_user_non_exist_username.__doc__)
        self.assertIsNone(self.connection.modify_user(NON_EXIST_PATIENT_USERNAME, PATIENT['public_profile'],
                                                      PATIENT['restricted_profile']))

    # TODO not working
    def test_append_user(self):
        """
        Test that a new patient/doctor can be added and check its data after adding
        """
        print('(' + self.test_append_user.__name__+')', self.test_append_user.__doc__)
        new_username = self.connection.append_user(NEW_PATIENT_USERNAME, NEW_PATIENT)
        # test appended ok
        self.assertIsNotNone(new_username)
        # check appended the same user data
        self.assertEqual(new_username, NEW_PATIENT_USERNAME)
        # check the added user in db has the same data
        get_new_patient = self.connection.get_user(new_username)
        self.assertDictContainsSubset(NEW_PATIENT['restricted_profile'], get_new_patient['restricted_profile'])
        self.assertDictContainsSubset(NEW_PATIENT['public_profile'], get_new_patient['public_profile'])

    def test_append_existing_user(self):
        """
        Test that I cannot add two users with the same name
        """
        print('(' + self.test_append_existing_user.__name__+')', self.test_append_existing_user.__doc__)
        self.assertIsNone(self.connection.append_user(PATIENT_USERNAME, NEW_PATIENT))

    def test_get_user_id(self):
        """
        Test that get_user_id returns the right value given a username
        """
        print('(' + self.test_get_user_id.__name__+')', self.test_get_user_id.__doc__)
        # for patient
        self.assertEqual(PATIENT_ID, self.connection.get_user_id(PATIENT_USERNAME))
        # for doctor
        self.assertEqual(DOCTOR_ID, self.connection.get_user_id(DOCTOR_USERNAME))

    def test_get_user_id_unknown_user(self):
        """
        Test that get_user_id returns None when the username does not exist
        """
        print('(' + self.test_get_user_id.__name__+')', self.test_get_user_id.__doc__)
        self.assertIsNone(self.connection.get_user_id(NON_EXIST_PATIENT_USERNAME))

    def test_not_contains_user(self):
        """
        Check if the database does not contain users with username SuperBoy
        """
        print('(' + self.test_not_contains_user.__name__+')', self.test_not_contains_user.__doc__)
        # non existing doctor, it could be patient as well
        self.assertFalse(self.connection.contains_user(NON_EXIST_DOCTOR_USERNAME))

    def test_contains_user(self):
        """
        Check if the database contains users with username PoorGuy (patient) and Clarissa (doctor)
        """
        print('(' + self.test_contains_user.__name__+')', self.test_contains_user.__doc__)
        self.assertTrue(self.connection.contains_user(PATIENT_USERNAME))
        self.assertTrue(self.connection.contains_user(DOCTOR_USERNAME))


if __name__ == '__main__':
    print('Start running users tests')
    unittest.main()
