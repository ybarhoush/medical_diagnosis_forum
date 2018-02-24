"""
Created on 24.02.2018

Database API testing unit for tables creation, and whether all created successfully or not.

@author: Issam
"""

# Importing required modules
import sqlite3
import unittest

# Import the database of medical_forum
from medical_forum import database

# Database file path to be used for testing only and create database instance
DB_PATH = 'db/medical_forum_data_test.db'
ENGINE = database.Engine(DB_PATH)

# Tables content initial sizes
INITIAL_MESSAGES_COUNT = 0
INITIAL_USERS_COUNT = 0
INITIAL_USERS_PROFILE_COUNT = 0
INITIAL_DIAGNOSIS_COUNT = 0

# Tables names
USERS_TABLE = 'users'
USERS_PROFILE_TABLE = 'users_profile'
MESSAGES_TABLE = 'messages'
DIAGNOSIS_TABLE = 'diagnosis'

# Tables names, types and foreign keys constants
# User table
USERS_TABLE_NAMES = ['user_id', 'username', 'pass_hash', 'reg_date', 'last_login', 'msg_count']
USERS_TABLE_TYPES = ['INTEGER', 'TEXT', 'TEXT', 'INTEGER', 'INTEGER', 'INTEGER']
USERS_TABLE_FK = [()]

# Profile table
USERS_PROFILE_TABLE_NAMES = ['user_id', 'user_type', 'firstname', 'lastname', 'work_address', 'gender',
                             'age', 'email', 'picture', 'phone', 'diagnosis_id', 'height', 'weight', 'speciality']
USERS_PROFILE_TABLE_TYPES = ['INTEGER', 'INTEGER', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT',
                             'INTEGER', 'INTEGER', 'INTEGER', 'INTEGER', 'TEXT']
USERS_PROFILE_TABLE_FK = [('users', 'user_id', 'user_id'), ('diagnosis', 'diagnosis_id', 'diagnosis_id')]

# Messages table
MESSAGES_TABLE_NAMES = ['message_id', 'user_id', 'username', 'reply_to', 'title', 'body', 'views', 'timestamp']
MESSAGES_TABLE_TYPES = ['INTEGER', 'INTEGER', 'TEXT', 'INTEGER', 'TEXT', 'TEXT', 'INTEGER', 'INTEGER']
MESSAGES_TABLE_FK = [('users', 'user_id', 'user_id'), ('users', 'username', 'username'),
                     ('messages', 'reply_to', 'message_id')]

# Diagnosis table
DIAGNOSIS_TABLE_NAMES = ['diagnosis_id', 'user_id', 'message_id', 'disease', 'diagnosis_description']
DIAGNOSIS_TABLE_TYPES = ['INTEGER', 'INTEGER', 'INTEGER', 'TEXT', 'TEXT']
DIAGNOSIS_TABLE_FK = [('messages', 'message_id', 'message_id'), ('users', 'user_id', 'user_id')]

FOREIGN_KEYS_ON = 'PRAGMA foreign_keys = ON'


class TablesCreationTestCase(unittest.TestCase):
    """
    Test case for different tables creation
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
            print(ENGINE.connect())
            self.connection = ENGINE.connect()

        # In case of error/exception in populating tables, clear all tables data
        except Exception as e:
            print(e)
            ENGINE.clear()

    def tearDown(self):
        """ Terminate active database connection and clear tables records (keep structure) """
        self.connection.close()
        ENGINE.clear()

    def test_users_table_schema(self):
        """
        Checks that the users table has the right schema.
        """
        print('(' + self.test_messages_table_schema.__name__ + ')', self.test_messages_table_schema.__doc__)
        test_table_schema(self, USERS_TABLE, USERS_TABLE_NAMES, USERS_TABLE_TYPES, USERS_TABLE_FK, False)

    def test_users_profile_table_schema(self):
        """
        Checks that the users profile table has the right schema.
        """
        print('(' + self.test_messages_table_schema.__name__ + ')', self.test_messages_table_schema.__doc__)
        test_table_schema(self, USERS_PROFILE_TABLE, USERS_PROFILE_TABLE_NAMES, USERS_PROFILE_TABLE_TYPES,
                          USERS_PROFILE_TABLE_FK, True)

    def test_messages_table_schema(self):
        """
        Checks that the messages table has the right schema.
        """
        print('(' + self.test_messages_table_schema.__name__ + ')', self.test_messages_table_schema.__doc__)
        test_table_schema(self, MESSAGES_TABLE, MESSAGES_TABLE_NAMES, MESSAGES_TABLE_TYPES, MESSAGES_TABLE_FK, True)

    def test_diagnosis_table_schema(self):
        """
        Checks that the diagnosis table has the right schema.
        """
        print('(' + self.test_messages_table_schema.__name__ + ')', self.test_messages_table_schema.__doc__)
        test_table_schema(self, DIAGNOSIS_TABLE, DIAGNOSIS_TABLE_NAMES, DIAGNOSIS_TABLE_TYPES, DIAGNOSIS_TABLE_FK, True)

    def test_users_table_populated(self):
        """
        Check that the users table has been populated with default data successfully.
         """
        print('(' + self.test_users_table_populated.__name__ + ')', self.test_users_table_populated.__doc__)
        test_table_populated(self, USERS_TABLE, INITIAL_USERS_COUNT)

    def test_users_profile_table_populated(self):
        """
        Check that the users profile table has been populated with default data successfully.
         """
        print('(' + self.test_users_table_populated.__name__ + ')', self.test_users_table_populated.__doc__)
        test_table_populated(self, USERS_TABLE, INITIAL_USERS_COUNT)

    def test_messages_table_populated(self):
        """
        Check that the messages table has been populated with default data successfully.
         """
        print('(' + self.test_users_table_populated.__name__ + ')', self.test_users_table_populated.__doc__)
        test_table_populated(self, USERS_TABLE, INITIAL_USERS_COUNT)

    def test_diagnosis_table_populated(self):
        """
        Check that the diagnosis table has been populated with default data successfully.
         """
        print('(' + self.test_users_table_populated.__name__ + ')', self.test_users_table_populated.__doc__)
        test_table_populated(self, USERS_TABLE, INITIAL_USERS_COUNT)


def test_table_populated(self, table_name, element_count):
    """
    Check that the messages table has been populated with default data successfully.
    Calling sqlite directly (as stated in Exercise 1 docs)
    Exercise 1 has been used as a reference
     """
    # print('(' + self.test_messages_table_populated.__name__ + ')', self.test_messages_table_populated.__doc__)
    # query to get list of messages table elements
    query = 'SELECT * FROM {}'.format(table_name)
    # Get the sqlite3 con from the Connection instance
    con = self.connection.con
    with con:
        # Cursor and row from sqlite3 class
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        # Support for foreign keys and execute query
        cur.execute(FOREIGN_KEYS_ON)
        cur.execute(query)
        items = cur.fetchall()
        # Assert if count of messages doesn't equal the known initial value
        self.assertEqual(len(items), element_count)


def test_table_schema(self, table_name, columns_names, columns_types, table_fk, fk_on):
    """
    General method to checks that the provided table has the right schema.
    Calling sqlite directly (as stated in Exercise 1 docs)
    Exercise 1 is used as reference and https://docs.python.org/3/library/unittest.html#re-using-old-test-code

    @:param table_name the name of the table to check
    @:param columns_names a tuple with the real/default column names
    @:param columns_types a tuple with the real/default column types
    @:param table_fk a tuple with the table's foreign keys
    @:param fk_on whether the table has any foreign keys or not (True/False)
    """
    # print('(' + self.test_users_table_schema.__name__ + ')', self.test_users_table_schema.__doc__)
    # connection instance
    con = self.connection.con
    with con:
        c = con.cursor()
        # collect column information in the query result
        # Every column will be represented by a tuple with the following attributes:
        # (id, name, type, not null, default_value, primary_key)
        c.execute('PRAGMA TABLE_INFO({})'.format(table_name))
        ti_result = c.fetchall()
        names = [tup[1] for tup in ti_result]
        types = [tup[2] for tup in ti_result]

        # Check and assert the names and their types with default ones
        self.assertEqual(names, columns_names)
        self.assertEqual(types, columns_types)

        if fk_on:
            # get the foreign key data using the the query below
            # the returned tuple has the following attributes
            # (id, seq, table, from, to, on_update, on_delete, match)
            # so we take elements (2, 3, 4) -> (table, from, to)
            # reference: https://stackoverflow.com/questions/44424476/output-of-the-sqlites-foreign-key-list-pragma
            c.execute('PRAGMA FOREIGN_KEY_LIST({})'.format(table_name))
            fk_result = c.fetchall()
            # Check and assert that foreign keys are correctly set
            result_filtered = [(tup[2], tup[3], tup[4]) for tup in fk_result]
            for tup in result_filtered:
                # Test that each tup is included in the list of all default foreign keys
                self.assertIn(tup, table_fk)


if __name__ == '__main__':
    print('Start running tables tests')
    print(ENGINE)
    unittest.main()

