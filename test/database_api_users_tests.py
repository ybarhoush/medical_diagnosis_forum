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
                                      'picture': '',
                                      'age': 40}
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
        '''
        Check that the method create_user_object works return proper values.
        '''
        print('('+self.test_create_user_object.__name__+')', self.test_create_user_object.__doc__)
        # Query to get users and users_profile for the patient
        query = 'SELECT users.*, users_profile.* FROM users, users_profile \
                 WHERE users.user_id = users_profile.user_id'
        # assert if result doesn't contain patient
        self.assertDictContainsSubset(self.connection._create_user_object(execute_query(self, query, 'one')), PATIENT)

    def test_get_user(self):
        '''
        Test get_user for patient with username PoorGuy and doctor with username Clarissa
        '''
        print('('+self.test_get_user.__name__+')', self.test_get_user.__doc__)
        # test for patient
        self.assertDictContainsSubset(self.connection.get_user(PATIENT_ID), PATIENT)
        # test for doctor
        self.assertDictContainsSubset(self.connection.get_user(DOCTOR_ID), DOCTOR)
    #
    # def test_get_user_noexistingid(self):
    #     '''
    #     Test get_user with  msg-200 (no-existing)
    #     '''
    #     print('('+self.test_get_user_noexistingid.__name__+')', \
    #           self.test_get_user_noexistingid.__doc__)
    #
    #     #Test with an existing user
    #     user = self.connection.get_user(USER_WRONG_NICKNAME)
    #     self.assertIsNone(user)
    #
    # def test_get_users(self):
    #     '''
    #     Test that get_users work correctly and extract required user info
    #     '''
    #     print('('+self.test_get_users.__name__+')', \
    #           self.test_get_users.__doc__)
    #     users = self.connection.get_users()
    #     #Check that the size is correct
    #     self.assertEqual(len(users), INITIAL_SIZE)
    #     #Iterate throug users and check if the users with USER1_ID and
    #     #USER2_ID are correct:
    #     for user in users:
    #         if user['nickname'] == USER1_NICKNAME:
    #             self.assertDictContainsSubset(user, USER1['public_profile'])
    #         elif user['nickname'] == USER2_NICKNAME:
    #             self.assertDictContainsSubset(user, USER2['public_profile'])
    #
    # def test_delete_user(self):
    #     '''
    #     Test that the user Mystery is deleted
    #     '''
    #     print('('+self.test_delete_user.__name__+')', \
    #           self.test_delete_user.__doc__)
    #     resp = self.connection.delete_user(USER1_NICKNAME)
    #     self.assertTrue(resp)
    #     #Check that the users has been really deleted throug a get
    #     resp2 = self.connection.get_user(USER1_NICKNAME)
    #     self.assertIsNone(resp2)
    #     #Check that the user does not have associated any message
    #     resp3 = self.connection.get_messages(nickname=USER1_NICKNAME)
    #     self.assertEqual(len(resp3), 0)
    #
    # def test_delete_user_noexistingnickname(self):
    #     '''
    #     Test delete_user with  Batty (no-existing)
    #     '''
    #     print('('+self.test_delete_user_noexistingnickname.__name__+')', \
    #           self.test_delete_user_noexistingnickname.__doc__)
    #     #Test with an existing user
    #     resp = self.connection.delete_user(USER_WRONG_NICKNAME)
    #     self.assertFalse(resp)
    #
    # def test_modify_user(self):
    #     '''
    #     Test that the user Mystery is modifed
    #     '''
    #     print('('+self.test_modify_user.__name__+')', \
    #           self.test_modify_user.__doc__)
    #     #Get the modified user
    #     resp = self.connection.modify_user(USER1_NICKNAME, MODIFIED_USER1)
    #     self.assertEqual(resp, USER1_NICKNAME)
    #     #Check that the users has been really modified through a get
    #     resp2 = self.connection.get_user(USER1_NICKNAME)
    #     resp_p_profile = resp2['public_profile']
    #     resp_r_profile = resp2['restricted_profile']
    #     #Check the expected values
    #     p_profile = MODIFIED_USER1['public_profile']
    #     r_profile = MODIFIED_USER1['restricted_profile']
    #     self.assertEqual(p_profile['signature'],
    #                       resp_p_profile['signature'])
    #     self.assertEqual(p_profile['avatar'], resp_p_profile['avatar'])
    #     self.assertEqual(r_profile['age'], resp_r_profile['age'])
    #     self.assertEqual(r_profile['email'], resp_r_profile['email'])
    #     self.assertEqual(r_profile['website'], resp_r_profile['website'])
    #     self.assertEqual(r_profile['residence'], resp_r_profile['residence'])
    #     self.assertEqual(r_profile['mobile'], resp_r_profile['mobile'])
    #     self.assertEqual(r_profile['skype'], resp_r_profile['skype'])
    #     self.assertEqual(r_profile['picture'], resp_r_profile['picture'])
    #     self.assertDictContainsSubset(resp2, MODIFIED_USER1)
    #
    # def test_modify_user_noexistingnickname(self):
    #     '''
    #     Test modify_user with  user Batty (no-existing)
    #     '''
    #     print('('+self.test_modify_user_noexistingnickname.__name__+')', \
    #           self.test_modify_user_noexistingnickname.__doc__)
    #     #Test with an existing user
    #     resp = self.connection.modify_user(USER_WRONG_NICKNAME, USER1)
    #     self.assertIsNone(resp)
    #
    # def test_append_user(self):
    #     '''
    #     Test that I can add new users
    #     '''
    #     print('('+self.test_append_user.__name__+')', \
    #           self.test_append_user.__doc__)
    #     nickname = self.connection.append_user(NEW_USER_NICKNAME, NEW_USER)
    #     self.assertIsNotNone(nickname)
    #     self.assertEqual(nickname, NEW_USER_NICKNAME)
    #     #Check that the messages has been really modified through a get
    #     resp2 = self.connection.get_user(nickname)
    #     self.assertDictContainsSubset(NEW_USER['restricted_profile'],
    #                                   resp2['restricted_profile'])
    #     self.assertDictContainsSubset(NEW_USER['public_profile'],
    #                                   resp2['public_profile'])
    #
    # def test_append_existing_user(self):
    #     '''
    #     Test that I cannot add two users with the same name
    #     '''
    #     print('('+self.test_append_existing_user.__name__+')', \
    #           self.test_append_existing_user.__doc__)
    #     nickname = self.connection.append_user(USER1_NICKNAME, NEW_USER)
    #     self.assertIsNone(nickname)
    #
    # def test_get_user_id(self):
    #     '''
    #     Test that get_user_id returns the right value given a nickname
    #     '''
    #     print('('+self.test_get_user_id.__name__+')', \
    #           self.test_get_user_id.__doc__)
    #     id = self.connection.get_user_id(USER1_NICKNAME)
    #     self.assertEqual(USER1_ID, id)
    #     id = self.connection.get_user_id(USER2_NICKNAME)
    #     self.assertEqual(USER2_ID, id)
    #
    # def test_get_user_id_unknown_user(self):
    #     '''
    #     Test that get_user_id returns None when the nickname does not exist
    #     '''
    #     print('('+self.test_get_user_id.__name__+')', \
    #           self.test_get_user_id.__doc__)
    #     id = self.connection.get_user_id(USER_WRONG_NICKNAME)
    #     self.assertIsNone(id)
    #
    # def test_not_contains_user(self):
    #     '''
    #     Check if the database does not contain users with id Batty
    #     '''
    #     print('('+self.test_contains_user.__name__+')', \
    #           self.test_contains_user.__doc__)
    #     self.assertFalse(self.connection.contains_user(USER_WRONG_NICKNAME))
    #
    # def test_contains_user(self):
    #     '''
    #     Check if the database contains users with nickname Mystery and HockeyFan
    #     '''
    #     print('('+self.test_contains_user.__name__+')', \
    #           self.test_contains_user.__doc__)
    #     self.assertTrue(self.connection.contains_user(USER1_NICKNAME))
    #     self.assertTrue(self.connection.contains_user(USER2_NICKNAME))


if __name__ == '__main__':
    print('Start running users tests')
    unittest.main()
