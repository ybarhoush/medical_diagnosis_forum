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
    'body': "Hi, I have this soreness in my throat. It started just yesterday and it's \
            getting worse by every hour. What should I do, and what is the cause of this.",
    'sender': 'PoorGuy',
    'timestamp': 1519474612
}

MESSAGE_2_ID = 'msg-8'
MESSAGE_2 = {
    'message_id': 'msg-8',
    'reply_to': 'msg-1',  # message reply to MESSAGE_1
    'title': 'Dizziness when running',
    'body': "Hi, I need help with this issue real quick. I get very dizzy when I run for few minutes. \
            This is being happening for like 2 weeks now. I really need help with this !",
    'sender': 'Dizzy',
    'timestamp': 1519441355
}

# bad non-existing message_id
BAD_MESSAGE_ID = 'msg-256'

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
            self.connection.get_message('1')

    def test_get_message_non_exist_id(self):
        """
        Test get_message with msg-200 (no-existing)
        """
        print('(' + self.test_get_message_non_exist_id.__name__+')', self.test_get_message_non_exist_id.__doc__)
        # Test with an message id for a non-existing message
        self.assertIsNone(self.connection.get_message(BAD_MESSAGE_ID))

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


if __name__ == '__main__':
    print('Running database messages tests')
    unittest.main()
