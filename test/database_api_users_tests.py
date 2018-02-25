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
PATIENT = {'public_profile': {'reg_date': 1362015937,
                              'username': PATIENT_USERNAME,
                              'speciality': '',
                              'user_type': 0},
           'restricted_profile': {'firstname': 'PoorGuy',
                                  'lastname': 'Jackie',
                                  'work_address': '85 South White Oak Way',
                                  'gender': 'female',
                                  'picture': '192.219/dab/image.png',
                                  'age': '36'}
           }

MODIFIED_PATIENT = {'public_profile': {'reg_date': 1362015937,
                                       'username': PATIENT_USERNAME,
                                       'speciality': '',
                                       'user_type': 0},
                    'restricted_profile': {'firstname': 'PoorGuy',
                                           'lastname': 'Tell',
                                           'work_address': '54 Middle White Park',
                                           'picture': '192.219/dab/image45.png',
                                           'age': '36'}
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
                                 'picture': '192.219/dab/image.png',
                                 'age': '27'}
          }

NEW_PATIENT_USERNAME = 'sully'
NEW_PATIENT = {'public_profile': {'reg_date': 1362012548,
                                  'username': NEW_PATIENT_USERNAME,
                                  'speciality': '',
                                  'user_type': 0},
               'restricted_profile': {'firstname': 'sully',
                                      'lastname': 'stolen',
                                      'work_address': '89 North White Oak Way',
                                      'picture': '',
                                      'age': '40'}
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


if __name__ == '__main__':
    print('Start running users tests')
    unittest.main()
