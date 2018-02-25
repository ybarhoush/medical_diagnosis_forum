"""
Created on 25.02.2018

Database API testing unit for users related methods from medical_forum/database.py.

@author: Issam
"""

# Importing required modules
import unittest
# import helper different methods
from .utils import *

class DatabaseDiagnosisTestCase(unittest.TestCase):
    """
    Test cases for different database diagnosis table methods
    """

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

    def test_create_user_list_object(self):
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


if __name__ == '__main__':
    print('Start running users tests')
    unittest.main()