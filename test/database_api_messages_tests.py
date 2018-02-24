"""
Created on 24.02.2018

Database API testing unit for messages related methods from medical_forum/database.py.

@author: Issam
"""

# Importing required modules
import sqlite3
import unittest

# Import the database of medical_forum
from medical_forum import database

# Database file path to be used for testing only and create database instance
DB_PATH = 'db/medical_forum_test.db'
ENGINE = database.Engine(DB_PATH)

# Defining testing constants for messages objects
INITIAL_MESSAGES_COUNT = 23

MESSAGE_1 = {
    'message_id': 'msg-1',
    'reply_to': None,  # this means it's a new message or medical case
    'title': 'Soreness in the throat',
    'body': "Hi, I have this soreness in my throat. It started just yesterday and it's \
            getting worse by every hour. What should I do, and what is the cause of this.",
    'sender': 'PoorGuy',
    'created_time': 1519474612
}

MESSAGE_2 = {
    'message_id': 'msg-8',
    'reply_to': 'msg-1',  # message reply to MESSAGE_1
    'title': 'Dizziness when running',
    'body': "Hi, I need help with this issue real quick. I get very dizzy when I run for few minutes. \
            This is being happening for like 2 weeks now. I really need help with this !",
    'sender': 'Dizzy',
    'created_time': 1519441355
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

    def setUpDB(self):
        """ Populates the database tables with data """
        try:
            # Get default data from medical_forum_data_dump.sql, populate tables and connect to DB
            ENGINE.populate_tables()
            self.connection = ENGINE.connect()

        # In case of error/exception in populating tables, clear all tables data
        except Exception as e:
            print(e)
            ENGINE.clear()

    def tearDownDB(self):
        """ Terminate active database connection and clear tables records (keep structure) """
        self.connection.close()
        ENGINE.clear()

    def test_messages_table_exist(self):
        """
        Check that the messages table has been created successfully.
        Calling sqlite directly (as stated in Exercise 1 docs) and
        reference with changes: https://dev.mysql.com/doc/refman/5.7/en/information-schema.html
         """
        print('(' + self.test_messages_table_exist.__name__ + ')', self.test_messages_table_exist.__doc__)
        # SQL query to get schema information
        query = 'SELECT COUNT(*) FROM information_schema.tables WHERE table_name = {}'.format(MESSAGES_TABLE_NAME)
        # Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            # Cursor and row from sqlite3 class
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Support for foreign keys and execute query
            cur.execute(FOREIGN_KEYS_ON)
            cur.execute(query)
            # Assert if table does not exist from result of previous query
            self.assertEqual(cur.fetchone()[0], 1)

    def test_messages_table_populated(self):
        """
        Check that the messages table has been populated with default data successfully.
        Calling sqlite directly (as stated in Exercise 1 docs)
        Exercise 1 has been used as a reference
         """
        print('(' + self.test_messages_table_populated.__name__ + ')', self.test_messages_table_populated.__doc__)
        # query to get list of messages table elements
        query = 'SELECT * FROM {}'.format(MESSAGES_TABLE_NAME)
        # Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            # Cursor and row from sqlite3 class
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            # Support for foreign keys and execute query
            cur.execute(FOREIGN_KEYS_ON)
            cur.execute(query)
            messages_items = cur.fetchall()
            # Assert if count of messages doesn't equal the known initial value
            self.assertEqual(len(messages_items), INITIAL_MESSAGES_COUNT)

    def test_create_message_object(self):
        """
        Check that the messages table has been populated with default data successfully.
        Calling sqlite directly (as stated in Exercise 1 docs)
         """
        print('(' + self.test_create_message_object.__name__ + ')', self.test_create_message_object.__doc__)


if __name__ == '__main__':
    print('Running database messages tests')
    unittest.main()
