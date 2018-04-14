"""
Created on 13.02.2013

Modified on 25.02.2018

Provides the database API to access the forum persistent data.

@author: ivan
@author: mika
@author: yazan
@author: Issam
"""

import sqlite3
import os
from .database_connection import Connection

DEFAULT_DB_PATH = 'db/medical_forum_data.db'
DEFAULT_SCHEMA = "db/medical_forum_data_schema.sql"
DEFAULT_DATA_DUMP = "db/medical_forum_data_dump.sql"

# Copied Class from Exercise 1
# We state if a method is copied, modified or written from scratch before it


class Engine(object):
    """
    Abstraction of the database.

    It includes tools to create, configure,
    populate and connect to the sqlite file. You can access the Connection
    instance, and hence, to the database interface itself using the method
    :py:meth:`connection`.

    :Example:

    >>> engine = Engine()
    >>> con = engine.connect()

    :param db_path: The path of the database file (always with respect to the
        calling script. If not specified, the Engine will use the file located
        at *db/forum.db*

    """

    def __init__(self, db_path=None):
        """
        """

        super(Engine, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH

    def connect(self):
        """
        Creates a connection to the database.

        :return: A Connection instance
        :rtype: Connection

        """
        return Connection(self.db_path)

    def remove_database(self):
        """
        Removes the database file from the filesystem.
        """
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def clear(self):
        """
        Purge the database removing all records from the tables. However,
        it keeps the database schema (meaning the table structure)

        """
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        cursor = con.cursor()
        cursor.execute(keys_on)
        with con:
            cursor = con.cursor()
            # cursor.execute("DELETE FROM diagnoses")
            cursor.execute("DELETE FROM messages")
            cursor.execute("DELETE FROM users_profile")
            cursor.execute("DELETE FROM users")

    def create_tables(self, schema=None):
        """
        Create programmatically the tables from a schema file.

        :param schema: path to the .sql schema file. If this parmeter is
            None, then *db/forum_schema_dump.sql* is utilized.
        """
        con = sqlite3.connect(self.db_path)
        if schema is None:
            schema = DEFAULT_SCHEMA
        try:
            with open(schema, encoding="utf-8") as schema_file:
                sql = schema_file.read()
                cur = con.cursor()
                cur.executescript(sql)
        finally:
            con.close()

    def populate_tables(self, dump=None):
        """
        Populate programmatically the tables from a dump file.

        :param dump:  path to the .sql dump file. If this parmeter is
            None, then *db/forum_data_dump.sql* is utilized.
        """
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        cursor = con.cursor()
        cursor.execute(keys_on)
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        try:
            with open(dump, encoding="utf-8") as schema_file:
                sql = schema_file.read()
                cursor = con.cursor()
                cursor.executescript(sql)
        finally:
            con.close()

    # Modified from create_messages_table
    def create_messages_table(self):
        """
        Create the table ``messages`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        """
        create_messages_table_query = 'CREATE TABLE messages(message_id INTEGER PRIMARY KEY, \
                    user_id INTEGER, \
                    username TEXT, \
                    reply_to INTEGER, \
                    title TEXT, \
                    body TEXT, \
                    views INTEGER, \
                    timestamp INTEGER, \
                    FOREIGN KEY(reply_to) \
                    REFERENCES messages(message_id) ON DELETE CASCADE, \
                    FOREIGN KEY(user_id,username) \
                    REFERENCES users(user_id, username) ON DELETE SET NULL)'
        return self.__execute_query(create_messages_table_query)

    # Modified from create_users_table
    def create_users_table(self):
        """
        Create the table ``users`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        """
        create_users_table_query = 'CREATE TABLE users(user_id INTEGER PRIMARY KEY,\
                                    username TEXT UNIQUE, \
                                    pass_hash INTEGER,\
                                    reg_date INTEGER,\
                                    last_login INTEGER, \
                                    msg_count INTEGER,\
                                    UNIQUE(user_id, username))'
        return self.__execute_query(create_users_table_query)

    # Modified from create_users_profile_table
    def create_users_profile_table(self):
        """
        Create the table ``users_profile`` programmatically, without using
        .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        """
        create_usersprofile_table_query = 'CREATE TABLE users_profile(\
                    user_id INTEGER PRIMARY KEY, \
                    user_type INTEGER, \
                    firstname TEXT, \
                    lastname TEXT, \
                    work_address TEXT, \
                    gender TEXT, \
                    age TEXT, \
                    email TEXT, \
                    picture TEXT, \
                    phone TEXT, \
                    diagnosis_id INTEGER, \
                    height INTEGER, \
                    weight INTEGER, \
                    speciality TEXT, \
                    FOREIGN KEY(diagnosis_id) \
                    REFERENCES users(diagnosis_id) ON DELETE CASCADE)'
        return self.__execute_query(create_usersprofile_table_query)

    # Modified from create_users_profile_table
    def create_diagnoses_table(self):
        """
        Create the table ``diagnoses`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        """
        create_diags_table_query = 'CREATE TABLE diagnosis(diagnosis_id INTEGER PRIMARY KEY, \
                    user_id INTEGER, \
                    message_id INTEGER, \
                    disease TEXT, \
                    diagnosis_description TEXT, \
                    FOREIGN KEY(user_id) \
                    REFERENCES users(user_id) ON DELETE CASCADE) \
                    FOREIGN KEY(message_id) \
                    REFERENCES users(message_id) ON DELETE CASCADE)'

        return self.__execute_query(create_diags_table_query)

    def __execute_query(self, query):
        """Execute the given SQL query"""
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        with con:
            cursor = con.cursor()
            try:
                cursor.execute(keys_on)
                cursor.execute(query)
            except sqlite3.Error as excp:
                print("Error %s:" % excp.args[0])
                return False
        return True
