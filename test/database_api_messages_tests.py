"""
Created on 24.02.2018

Database API testing unit for messages related methods from medical_forum/database.py.

@author: Issam
"""

# Importing required modules
import unittest
# import helper different methods
from .utils import *

# Import the database of medical_forum
from medical_forum import database

# Database file path to be used for testing only and create database instance
DB_PATH = 'db/medical_forum_test.db'
ENGINE = database.Engine(DB_PATH)

# Defining testing constants for messages objects
INITIAL_MESSAGES_COUNT = 23

MESSAGE_1_ID = 'msg-1'
MESSAGE_1 = {
    'message_id': 'msg-1',
    'reply_to': None,  # this means it's a new message or medical case
    'title': 'Soreness in the throat',
<<<<<<< HEAD
    'body': "Hi, I have this soreness in my throat. It started just yesterday and its \
            getting worse by every hour. What should I do, and what is the cause of this. ",
=======
    'body': "Hi, I have this soreness in my throat. It started just yesterday and its getting worse by every hour. \
             What should I do, and what is the cause of this. ",
>>>>>>> e77a545ad5581d35febfe78f0a6e32975bbf63eb
    'sender': 'PoorGuy',
    'timestamp': 1519474612
}

MESSAGE_2_ID = 'msg-8'
MESSAGE_DUMMY_USERNAME = 'Dizzy'
MESSAGE_2 = {
    'message_id': 'msg-8',
    'reply_to': 'msg-1',  # message reply to MESSAGE_1
    'title': 'Dizziness when running',
<<<<<<< HEAD
    'body': "Dizziness when running','Hi, I need help with this issue real quick. I get very dizzy when I run for few minutes. \
            This is being happening for like 2 weeks now. I really need help with this ! ",
    'sender': 'Dizzy',
=======
    'body': "Hi, I need help with this issue real quick. I get very dizzy when I run for few minutes. \
            This is being happening for like 2 weeks now. I really need help with this ! ",
    'sender': MESSAGE_DUMMY_USERNAME,
>>>>>>> e77a545ad5581d35febfe78f0a6e32975bbf63eb
    'timestamp': 1519441355
}

MESSAGE_1_MODIFIED = {'message_id': MESSAGE_1_ID,
                      'reply_to': None,
                      'title': 'new title',
                      'body': 'new body',
                      'sender': 'poorGuy',
                      'timestamp': 1362017481}

# bad and non-existing message_id
NON_EXIST_MESSAGE_ID = 'msg-256'
BAD_MESSAGE_ID = '1'

FOREIGN_KEYS_ON = 'PRAGMA foreign_keys = ON'
MESSAGES_TABLE_NAME = 'messages'


class DatabaseMessagesTestCase(unittest.TestCase):
    """
    Test cases for different database messages methods
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

    def test_messages_table_populated(self):
        """
        Check that the messages table has been populated with default data successfully.
         """
        print('(' + self.test_messages_table_populated.__name__ + ')', self.test_messages_table_populated.__doc__)
        test_table_populated(self, MESSAGES_TABLE_NAME, INITIAL_MESSAGES_COUNT)

    def test_create_message_object(self):
        """
        Check that the method _create_message_object works return adequate
        values for the first database row. NOTE: Do not use Connection instace
        to extract data from database but call directly SQL.
         """
        print('(' + self.test_create_message_object.__name__ + ')', self.test_create_message_object.__doc__)
        # Query string
        query = 'SELECT * FROM messages WHERE message_id = 1'
        # Test the method
        message = self.connection._create_message_object(execute_query(self, query, 'one'))
        self.assertDictContainsSubset(message, MESSAGE_1)

    def test_get_message(self):
        """
        Test get_message with id msg-1 and msg-8 (declared above)
        """
        print('(' + self.test_get_message.__name__+')', self.test_get_message.__doc__)
        self.assertDictContainsSubset(self.connection.get_message(MESSAGE_1_ID), MESSAGE_1)
        self.assertDictContainsSubset(self.connection.get_message(MESSAGE_2_ID), MESSAGE_2)

    def test_get_message_bad_id(self):
        """
        Test get_message with id 1 (malformed) and not 'msg-1'
        """
        print('(' + self.test_get_message_bad_id.__name__+')', self.test_get_message_bad_id.__doc__)
        # Test with an existing message
        with self.assertRaises(ValueError):
            self.connection.get_message(BAD_MESSAGE_ID)

    def test_get_message_non_exist_id(self):
        """
        Test get_message with msg-200 (no-existing)
        """
        print('(' + self.test_get_message_non_exist_id.__name__+')', self.test_get_message_non_exist_id.__doc__)
        # Test with an message id for a non-existing message
        self.assertIsNone(self.connection.get_message(NON_EXIST_MESSAGE_ID))

    # TODO: this is not implemented yet
    def test_get_messages(self):
        """
        Test that get_messages (a list of all messages) work correctly
        """
        print('(' + self.test_get_messages.__name__+')', self.test_get_messages.__doc__)
        messages = self.connection.get_messages()
        # Check that the size is correct
        self.assertEqual(len(messages), INITIAL_MESSAGES_COUNT)
        # check all message for the MESSAGE_1 and 2 if all values are correct
        for message in messages:
            if message['message_id'] == MESSAGE_1_ID:
                self.assertEqual(len(message), 4)
                self.assertDictContainsSubset(message, MESSAGE_1)
            elif message['message_id'] == MESSAGE_2_ID:
                self.assertEqual(len(message), 4)
                self.assertDictContainsSubset(message, MESSAGE_2)

    # TODO: this is not implemented yet
    def test_get_messages_specific_user(self):
        """
        Get all messages from user Mystery. Check that their ids are 13 and 14.
        """
        # Messages sent from Mystery are 13 and 14
        print('(' + self.test_get_messages_specific_user.__name__+')', self.test_get_messages_specific_user.__doc__)
        messages = self.connection.get_messages(nickname="Mystery")
        self.assertEqual(len(messages), 2)
        # Messages id are 13 and 14
        for message in messages:
            self.assertIn(message['message_id'], ('msg-13', 'msg-14'))
            self.assertNotIn(message['message_id'], ('msg-1', 'msg-2',
                                                    'msg-3', 'msg-4'))

    # TODO: this is not implemented yet
    def test_get_messages_length(self):
        """
        Check that the number_of_messages  is working in get_messages
        """
        # Messages sent from Mystery are 2
        print('(' + self.test_get_messages_length.__name__+')', self.test_get_messages_length.__doc__)
        messages = self.connection.get_messages(nickname="Mystery",
                                                number_of_messages=2)
        self.assertEqual(len(messages), 2)
        #Number of messages is 20
        messages = self.connection.get_messages(number_of_messages=1)
        self.assertEqual(len(messages), 1)

    def test_delete_message(self):
        """
        Test deleting a message (msg-1) and whether it was successful or not
        """
        print('(' + self.test_delete_message.__name__+')', self.test_delete_message.__doc__)
        self.assertTrue(self.connection.delete_message(MESSAGE_1_ID))
        # get the same message to see if was successfully deleted
        self.assertIsNone(self.connection.get_message(MESSAGE_1_ID))

    def test_delete_message_bad_id(self):
        """
        Test deleting a message with bad format (1) where the message exists but right
        format is (msg-1) not (1)
        """
        print('(' + self.test_delete_message_bad_id.__name__+')', self.test_delete_message_bad_id.__doc__)
        with self.assertRaises(ValueError):
            self.connection.delete_message(BAD_MESSAGE_ID)

    def test_delete_message_non_exist_id(self):
        """
        Test delete_message with a message that doesn't exist (msg-256)
        """
        print('(' + self.test_delete_message_non_exist_id.__name__+')', self.test_delete_message_non_exist_id.__doc__)
        self.assertFalse(self.connection.delete_message(NON_EXIST_MESSAGE_ID))

    # TODO: this is not implemented fully yet
    def test_modify_message(self):
        """
        Test that the message msg-1 has been modified
        """
        print('(' + self.test_modify_message.__name__+')', self.test_modify_message.__doc__)
        resp = self.connection.modify_message(MESSAGE_1_ID, "new title", "new body", "new editor")
        self.assertEqual(resp, MESSAGE_1_ID)
        # check whether modification was successful
        self.assertDictContainsSubset(self.connection.get_message(MESSAGE_1_ID), MESSAGE_1_MODIFIED)

    def test_modify_message_bad_id(self):
        """
        Test that trying to modify message with id (1) and not (msg-1) which actually exist
        """
        print('(' + self.test_modify_message_bad_id.__name__+')', self.test_modify_message_bad_id.__doc__)
        with self.assertRaises(ValueError):
            self.connection.modify_message(BAD_MESSAGE_ID, "new title", "new body", "editor")

    def test_modify_message_non_exist_id(self):
        """
        Test that trying to modify message with id (msg-256) which does not exist
        """
        print('(' + self.test_modify_message_non_exist_id.__name__+')', self.test_modify_message_non_exist_id.__doc__)
        resp = self.connection.modify_message(NON_EXIST_MESSAGE_ID, "new title", "new body", "editor")
        self.assertIsNone(resp)

    def test_create_message(self):
        """
        Test that a new message can be created with no error
        """
        print('(' + self.test_create_message.__name__+')', self.test_create_message.__doc__)
        message_id = self.connection.create_message("new title", "new body", MESSAGE_DUMMY_USERNAME)
        self.assertIsNotNone(message_id)
        # Get the expected modified message
        # for proper dictionary declaration: https://docs.python.org/3/tutorial/datastructures.html
        real_message = {'title': 'new title',
                        'body': 'new body',
                        'sender': MESSAGE_DUMMY_USERNAME}
        # Check that the message created with no error by matching it to the real one real_message
        self.assertDictContainsSubset(real_message, self.connection.get_message(message_id))

    def test_append_answer(self):
        """
        Test that a new message can be replied to
        """
        print('(' + self.test_append_answer.__name__+')', self.test_append_answer.__doc__)
        message_id = self.connection.append_answer(MESSAGE_1_ID, "new title", "new body", MESSAGE_DUMMY_USERNAME)
        self.assertIsNotNone(message_id)
        # The real message (how it should be)
        real_message = {'title': 'new title',
                        'body': 'new body',
                        'sender': MESSAGE_DUMMY_USERNAME,
                        'reply_to': MESSAGE_1_ID}
        # check created message with real one (accurate data)
        self.assertDictContainsSubset(real_message, self.connection.get_message(message_id))

    def test_append_answer_malformed_id(self):
        """
        Test that trying to reply message with bad id (1) raises an error
        """
        print('(' + self.test_append_answer_malformed_id.__name__+')', self.test_append_answer_malformed_id.__doc__)
        with self.assertRaises(ValueError):
            self.connection.append_answer(BAD_MESSAGE_ID, "new title", "new body", MESSAGE_DUMMY_USERNAME)

    def test_append_answer_non_exist_id(self):
        """
        Test append_answer with  id (msg-256) (no-existing)
        """
        print('(' + self.test_append_answer_non_exist_id.__name__+')', self.test_append_answer_non_exist_id.__doc__)
        self.assertIsNone(self.connection.append_answer(NON_EXIST_MESSAGE_ID, "new title", "new body",
                                                        MESSAGE_DUMMY_USERNAME))

    def test_contains_valid_message(self):
        """
        Check if the database contains messages with id msg-1 and msg-8
        """
        print('(' + self.test_contains_valid_message.__name__+')', self.test_contains_valid_message.__doc__)
        self.assertTrue(self.connection.contains_message(MESSAGE_1_ID))
        self.assertTrue(self.connection.contains_message(MESSAGE_2_ID))

    def test_not_contains_message(self):
        """
        Check if the database does not contain messages with id msg-256
        """
        print('(' + self.test_not_contains_message.__name__+')', self.test_not_contains_message.__doc__)
        # the right response should be false otherwise assert error
        self.assertFalse(self.connection.contains_message(NON_EXIST_MESSAGE_ID))


if __name__ == '__main__':
    print('Running database messages tests')
    unittest.main()
