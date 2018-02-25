"""
Created on 25.02.2018

Database API testing unit for users related methods from medical_forum/database.py.

@author: Issam
"""

# Importing required modules
import unittest
# import helper different methods
from .utils import *

# declare constants
DIAGNOSIS_1_ID = 'diagnosis-1'
DIAGNOSIS_1 = {'user_id': 1,
               'message_id': 'msg-7',
               'disease': 'blood',
               'diagnosis_description': 'Anne bought new car. Tony bought new car. Anne has free time. '
                                        'John has free time. Tony bought new car. '}
DIAGNOSIS_2_ID = 'diagnosis-12'
DIAGNOSIS_2 = {'user_id': 9,
               'message_id': 'msg-3',
               'disease': 'eyes',
               'diagnosis_description': 'Tony has free time. Anne is shopping. Tony bought new car. '
                                        'John bought new car. John bought new car. '}

DOCTOR_ID = 4
NOT_DOCTOR_ID = 1
NEW_DIAGNOSIS = {'user_id': DOCTOR_ID,
                 'message_id': 'msg-3',
                 'disease': 'flu',
                 'diagnosis_description': 'You need to stay and calm and not panic.'}

BAD_DIAGNOSIS_ID = '100'
NON_EXIST_DIAGNOSIS_ID = 'diagnosis-100'


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

    def test_diagnosis_table_populated(self):
        """
        Check that the diagnosis table has been populated with default data successfully.
         """
        print('(' + self.test_diagnosis_table_populated.__name__ + ')', self.test_diagnosis_table_populated.__doc__)
        test_table_populated(self, DIAGNOSIS_TABLE, INITIAL_DIAGNOSIS_COUNT)

    def test_create_diagnosis_object(self):
        """
        Check that the method create_diagnosis_object works return proper values for diagnosis id 1
        """
        print('(' + self.test_create_diagnosis_object.__name__+')', self.test_create_diagnosis_object.__doc__)
        # Query to get users and users_profile for the patient
        query = 'SELECT * FROM diagnosis WHERE diagnosis_id = 1'
        # assert if result doesn't contain patient
        self.assertDictContainsSubset(self.connection._create_diagnosis_object(execute_query(self, query, 'one')),
                                      DIAGNOSIS_1)

    def test_get_diagnosis(self):
        """
        Test get_diagnosis with diagnosis_id
        """
        print('(' + self.test_get_diagnosis.__name__+')', self.test_get_diagnosis.__doc__)
        # test for patient
        self.assertDictContainsSubset(self.connection.get_diagnosis(DIAGNOSIS_1_ID), DIAGNOSIS_1)

    def test_get_bad_diagnosis(self):
        """
        Test get_diagnosis with  diagnosis-100 (no-existing)
        """
        print('(' + self.test_get_bad_diagnosis.__name__+')', self.test_get_bad_diagnosis.__doc__)
        with self.assertRaises(ValueError):
            self.connection.get_diagnosis(BAD_DIAGNOSIS_ID)

    def test_get_non_exist_diagnosis(self):
        """
        Test get_diagnosis with  diagnosis-100 (no-existing)
        """
        print('(' + self.test_get_non_exist_diagnosis.__name__+')', self.test_get_non_exist_diagnosis.__doc__)
        self.assertIsNone(self.connection.get_diagnosis(NON_EXIST_DIAGNOSIS_ID))

    def test_append_diagnosis(self):
        """
        Test that a new diagnosis can be added and check its data after adding
        """
        print('(' + self.test_append_diagnosis.__name__+')', self.test_append_diagnosis.__doc__)
        new_diagnosis_id = self.connection.create_diagnosis(NEW_DIAGNOSIS)
        # test appended ok
        self.assertIsNotNone(new_diagnosis_id)
        # check the added user in db has the same data
        get_new_diagnosis = self.connection.get_diagnosis(new_diagnosis_id)
        self.assertDictContainsSubset(NEW_DIAGNOSIS, get_new_diagnosis)

    def test_append_diagnosis_by_non_doctor(self):
        """
        Test that a new diagnosis cannot be added by a non-doctor user
        """
        print('(' + self.test_append_diagnosis_by_non_doctor.__name__+')',
              self.test_append_diagnosis_by_non_doctor.__doc__)
        no_doctor_diagnosis = NEW_DIAGNOSIS
        no_doctor_diagnosis['user_id'] = NOT_DOCTOR_ID
        with self.assertRaises(ValueError):
            self.connection.create_diagnosis(no_doctor_diagnosis)


if __name__ == '__main__':
    print('Start running users tests')
    unittest.main()
