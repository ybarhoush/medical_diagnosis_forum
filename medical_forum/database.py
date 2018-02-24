"""
Created on 13.02.2013

Modified on 25.02.2018

Provides the database API to access the forum persistent data.

@author: ivan
@author: mika
@author: yazan
"""

from datetime import datetime
import time, sqlite3, re, os
#Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/medical_forum_data.db'
DEFAULT_SCHEMA = "db/medical_forum_data_schema.sql"
DEFAULT_DATA_DUMP = "db/medical_forum_data_dump.sql"

# Copied Class from Exercise 1
# Unless it is stated in the comment before the method, the method is copied
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
            #THIS REMOVES THE DATABASE STRUCTURE
            os.remove(self.db_path)

    def clear(self):
        """
        Purge the database removing all records from the tables. However,
        it keeps the database schema (meaning the table structure)

        """
        keys_on = 'PRAGMA foreign_keys = ON'
        #THIS KEEPS THE SCHEMA AND REMOVE VALUES
        con = sqlite3.connect(self.db_path)
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        with con:
            cur = con.cursor()
            cur.execute("DELETE FROM messages")
            cur.execute("DELETE FROM users")
            #NOTE since we have ON DELETE CASCADE BOTH IN users_profile AND
            #friends, WE DO NOT HAVE TO WORRY TO CLEAR THOSE TABLES.

    #METHODS TO CREATE AND POPULATE A DATABASE USING DIFFERENT SCRIPTS
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
            with open(schema, encoding="utf-8") as f:
                sql = f.read()
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
        #Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        #Populate database from dump
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        try:
            with open (dump, encoding="utf-8") as f:
                sql = f.read()
                cur = con.cursor()
                cur.executescript(sql)
        finally:
            con.close()

    #METHODS TO CREATE THE TABLES PROGRAMMATICALLY WITHOUT USING SQL SCRIPT

    #Modified from create_messages_table
    def create_messages_table(self):
        """
        Create the table ``messages`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        """
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE messages(message_id INTEGER PRIMARY KEY, \
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
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error as excp:
                print("Error %s:" % excp.args[0])
                return False
        return True

    #Modified from create_users_table
    def create_users_table(self):
        """
        Create the table ``users`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        """
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE users(user_id INTEGER PRIMARY KEY,\
                                    username TEXT UNIQUE, \
                                    pass_hash INTEGER,\
                                    reg_date INTEGER,\
                                    last_login INTEGER, \
                                    msg_count INTEGER,\
                                    UNIQUE(user_id, username))'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error as excp:
                print("Error %s:" % excp.args[0])
                return False
        return True

    #Modified from create_users_profile_table
    def create_users_profile_table(self):
        """
        Create the table ``users_profile`` programmatically, without using
        .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        """
        keys_on = 'PRAGMA foreign_keys = ON'

        stmnt = 'CREATE TABLE users_profile(user_type INTEGER PRIMARY KEY, \
                    user_id INTEGER, \
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
                    FOREIGN KEY(user_type) \
                    REFERENCES users(user_type) ON DELETE CASCADE) \
                    FOREIGN KEY(diagnosis_id) \
                    REFERENCES users(diagnosis_id) ON DELETE CASCADE)'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error as excp:
                print("Error %s:" % excp.args[0])
                return False
        return True

    #Modified from create_users_profile_table
    def create_diagnosis_table(self):
        """
        Create the table ``diagnosis`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        """
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE users_profile(diagnosis_id INTEGER PRIMARY KEY, \
                    user_id INTEGER, \
                    message_id INTEGER, \
                    disease TEXT, \
                    diagnosis_description TEXT, \
                    FOREIGN KEY(user_id) \
                    REFERENCES users(user_id) ON DELETE CASCADE) \
                    FOREIGN KEY(message_id) \
                    REFERENCES users(message_id) ON DELETE CASCADE)'
        #Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                #execute the statement
                cur.execute(stmnt)
            except sqlite3.Error as excp:
                print("Error %s:" % excp.args[0])
                return False
        return True


class Connection(object):
    """
    API to access the Forum database.

    The sqlite3 connection instance is accessible to all the methods of this
    class through the :py:attr:`self.con` attribute.

    An instance of this class should not be instantiated directly using the
    constructor. Instead use the :py:meth:`Engine.connect`.

    Use the method :py:meth:`close` in order to close a connection.
    A :py:class:`Connection` **MUST** always be closed once when it is not going to be
    utilized anymore in order to release internal locks.

    :param db_path: Location of the database file.
    :type dbpath: str

    """
    def __init__(self, db_path):
        super(Connection, self).__init__()
        self.con = sqlite3.connect(db_path)
        self._isclosed = False

    def isclosed(self):
        """
        :return: ``True`` if connection has already being closed.  
        """
        return self._isclosed

    def close(self):
        """
        Closes the database connection, commiting all changes.

        """
        if self.con and not self._isclosed:
            self.con.commit()
            self.con.close()
            self._isclosed = True

    #FOREIGN KEY STATUS
    def check_foreign_keys_status(self):
        """
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.

        """
        try:
            #Create a cursor to receive the database values
            cur = self.con.cursor()
            #Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            #We know we retrieve just one record: use fetchone()
            data = cur.fetchone()
            is_activated = data == (1,)
            print("Foreign Keys status: %s" % 'ON' if is_activated else 'OFF')
        except sqlite3.Error as excp:
            print("Error %s:" % excp.args[0])
            self.close()
            raise excp
        return is_activated

    def set_foreign_keys_support(self):
        """
        Activate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        """
        keys_on = 'PRAGMA foreign_keys = ON'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, ON
            cur.execute(keys_on)
            return True
        except sqlite3.Error as excp:
            print("Error %s:" % excp.args[0])
            return False

    def unset_foreign_keys_support(self):
        """
        Deactivate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        """
        keys_on = 'PRAGMA foreign_keys = OFF'
        try:
            #Get the cursor object.
            #It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            #execute the pragma command, OFF
            cur.execute(keys_on)
            return True
        except sqlite3.Error as excp:
            print("Error %s:" % excp.args[0])
            return False
    
    #HELPERS
    #Here the helpers that transform database rows into dictionary. They work
    #similarly to ORM

    #Helpers for messages
    #Modified from _create_message_object
    def _create_message_object(self, row):
        """
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``message_id``: id of the message (int)
            * ``title``: message's title
            * ``body``: message's text
            * ``timestamp``: UNIX timestamp (long integer) that specifies when
              the message was created.
            * ``replyto``: The id of the parent message. String with the format
              msg-{id}. Its value can be None.
            * ``sender``: The username of the message's creator.

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        """
        message_id = 'msg-' + str(row['message_id'])
        message_replyto = 'msg-' + str(row['reply_to']) \
            if row['reply_to'] is not None else None
        message_sender = row['username']
        message_title = row['title']
        message_body = row['body']
        message_timestamp = row['timestamp']
        message = {'message_id': message_id, 'title': message_title,
                   'timestamp': message_timestamp, 'replyto': message_replyto,
                   'body': message_body, 'sender': message_sender}
        return message

    #Modified from _create_message_list_object
    def _create_message_list_object(self, row):
        """
        Same as :py:meth:`_create_message_object`. However, the resulting
        dictionary is targeted to build messages in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``message_id``, ``title``,
            ``timestamp`` and ``sender``.

        """
        message_id = 'msg-' + str(row['message_id'])
        message_sender = row['username']
        message_title = row['title']
        message_timestamp = row['timestamp']
        message = {'message_id': message_id, 'title': message_title,
                   'timestamp': message_timestamp, 'sender': message_sender}
        return message

    #Helpers for users
    #Modified from _create_user_object
    def _create_user_object(self, row):
        """
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following format:

            .. code-block:: javascript

                {'public_profile':{'reg_date':,'username':'',
                                   'speciality':'','age':''},
                'restricted_profile':{'firstname':'','lastname':'',
                                      'work_address':'','gender':'',
                                      'picture':''}
                }

            where:

            * ``reg_date``: UNIX timestamp when the user registered in
                                 the system (long integer)
            * ``username``: username of the user
            * ``speciality``: text chosen by the user for speciality
            * ``age``: name of the image file used as age
            * ``firstanme``: given name of the user
            * ``lastname``: family name of the user
            * ``phone``: string showing the user's phone number. Can be None.
            * ``work_address``: complete user's home address.
            * ``picture``: file which contains an image of the user.
            * ``gender``: User's gender ('male' or 'female').

            Note that all values are string if they are not otherwise indicated.

        """
        reg_date = row['reg_date']
        return {'public_profile': {'reg_date': reg_date,
                                   'username': row['username'],
                                   'speciality': row['speciality'],
                                   'age': row['age']},
                'restricted_profile': {'firstname': row['firstname'],
                                       'lastname': row['lastname'],
                                       'phone': row['phone'],
                                       'work_address': row['work_address'],
                                       'gender': row['gender'],
                                       'picture': row['picture']}
                }
    #Modified from _create_user_list_object
    def _create_user_list_object(self, row):
        """
        Same as :py:meth:`_create_message_object`. However, the resulting
        dictionary is targeted to build messages in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``reg_date`` and
            ``username``

        """
        return {'reg_date': row['reg_date'], 'username': row['username']}
