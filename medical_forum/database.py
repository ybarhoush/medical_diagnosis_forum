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

        stmnt = 'CREATE TABLE users_profile(user_id INTEGER PRIMARY KEY, \
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

    # Helpers for diagnosis
    # Written from scratch
    def _create_diagnosis_object(self, row):
        '''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``diagnosis_id``: id of the message (int)
            * ``user_id``: id of the user (int)
            * ``message_id``: id of the message (int)
            * ``disease``: disease's text
            * ``diagnosis_description``: diagnosis description's text

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        '''
        diagnosis_id = 'diagnosis-' + str(row['diagnosis_id'])
        user_id = row['user_id']
        message_id = row['message_id']
        disease = row['disease']
        diagnosis_description = row['diagnosis_description']

        diagnosis = {'diagnosis_id': diagnosis_id, 'user_id': user_id,
                     'message_id': message_id,
                     'disease': disease, 'diagnosis_description': diagnosis_description}
        return diagnosis

    # Written from scratch
    def _create_diagnosis_list_object(self, row):
        '''
        Same as :py:meth:`_create_diagnosis_object`. However, the resulting
        dictionary is targeted to build messages in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``diagnosis_id``, ``user_id``,
            ``message_id``, ``disease`` and ``diagnosis_description``.
        '''
        diagnosis_id = 'diagnosis-' + str(row['diagnosis_id'])
        user_id = row['user_id']
        message_id = row['message_id']
        disease = row['disease']
        diagnosis_description = row['diagnosis_description']

        return {'diagnosis_id': diagnosis_id, 'user_id': user_id,
                'message_id': message_id,
                'disease': disease, 'diagnosis_description': diagnosis_description}

    #API ITSELF
    # Diagnosis Table API.
    def get_diagnosis(self, diagnosisid):
        '''
        Extracts a diagnosis from the database.

        :param diagnosisid: The id of the diagnosis. Note that diagnosisid is a
            string with format ``diagnosis-\d{1,3}``.
        :return: A dictionary with the format provided in
            :py:meth:`_create_diagnosis_object` or None if the diagnosis with target
            id does not exist.
        :raises ValueError: when ``diagnosisid`` is not well formed

        '''
        # Extracts the int which is the id for a diagnosis in the database
        match = re.match(r'diagnosis-(\d{1,3})', diagnosisid)
        if match is None:
            raise ValueError("The diagnosis is malformed")
        diagnosisid = int(match.group(1))
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Create the SQL Query
        query = 'SELECT * FROM diagnosis WHERE diagnosis_id = ?'
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement
        pvalue = (diagnosisid,)
        cur.execute(query, pvalue)
        # Process the response.
        # Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        # Build the return object
        return self._create_diagnosis_object(row)

    # TODO imlement create_diagnosis

    #Message Table API.
    def get_message(self, messageid):
        '''
        Extracts a message from the database.

        :param messageid: The id of the message. Note that messageid is a
            string with format ``msg-\d{1,3}``.
        :return: A dictionary with the format provided in
            :py:meth:`_create_message_object` or None if the message with target
            id does not exist.
        :raises ValueError: when ``messageid`` is not well formed

        '''
        #Extracts the int which is the id for a message in the database
        match = re.match(r'msg-(\d{1,3})', messageid)
        if match is None:
            raise ValueError("The messageid is malformed")
        messageid = int(match.group(1))
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the SQL Query
        query = 'SELECT * FROM messages WHERE message_id = ?'
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = (messageid,)
        cur.execute(query, pvalue)
        #Process the response.
        #Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        #Build the return object
        return self._create_message_object(row)

    def delete_message(self, messageid):
        '''
        Delete the message with id given as parameter.

        :param str messageid: id of the message to remove.Note that messageid
            is a string with format ``msg-\d{1,3}``
        :return: True if the message has been deleted, False otherwise
        :raises ValueError: if the messageId has a wrong format.

        '''
        #Extracts the int which is the id for a message in the database
        match = re.match(r'msg-(\d{1,3})', messageid)
        if match is None:
            raise ValueError("The messageid is malformed")
        messageid = int(match.group(1))

        #Create the SQL statment
        stmnt = 'DELETE FROM messages WHERE message_id = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (messageid,)
        try:
            cur.execute(stmnt, pvalue)
            #Commit the message
            self.con.commit()
        except sqlite3.Error as e:
            print("Error %s:" % (e.args[0]))
        return bool(cur.rowcount)
    #Modified from modify_message
    def modify_message(self, messageid, title, body, editor="Anonymous"):
        '''
        Modify the title, the body and the editor of the message with id
        ``messageid``

        :param str messageid: The id of the message to remove. Note that
            messageid is a string with format msg-\d{1,3}
        :param str title: the message's title
        :param str body: the message's content
        :param str editor: default 'Anonymous'. The username of the person
            who is editing this message. If it is not provided "Anonymous"
            will be stored in db.
        :return: the id of the edited message or None if the message was
              not found. The id of the message has the format ``msg-\d{1,3}``,
              where \d{1,3} is the id of the message in the database.
        :raises ValueError: if the messageid has a wrong format.

        '''
        #Extracts the int which is the id for a message in the database
        match = re.match(r'msg-(\d{1,3})', messageid)
        if match is None:
            raise ValueError("The messageid is malformed")
        messageid = int(match.group(1))
        #Create the SQL statment
        stmnt = 'UPDATE messages SET title=:title , body=:body, editor_nickname=:editor\
                 WHERE message_id =:msg_id'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        pvalue = {"msg_id": messageid,
                  "title": title,
                  "body": body,
                  "editor": editor}
        try:
            cur.execute(stmnt, pvalue)
            self.con.commit()
        except sqlite3.Error as e:
            print ("Error %s:" % (e.args[0]))
        else: 
            if cur.rowcount < 1:
                return None
        return 'msg-%s' % messageid

    def create_message(self, title, body, sender="Anonymous", replyto=None):
        '''
        Create a new message with the data provided as arguments.

        :param str title: the message's title
        :param str body: the message's content
        :param str sender: the username of the person who is editing this
            message. If it is not provided "Anonymous" will be stored in db.
        :param str replyto: Only provided if this message is an answer to a
            previous message (parent). Otherwise, Null will be stored in the
            database. The id of the message has the format msg-\d{1,3}

        :return: the id of the created message or None if the message was not
            found. Note that the returned value is a string with the format msg-\d{1,3}.

        :raises ForumDatabaseError: if the database could not be modified.
        :raises ValueError: if the replyto has a wrong format.

        '''
        #Extracts the int which is the id for a message in the database
        if replyto is not None:
            match = re.match('msg-(\d{1,3})', replyto)
            if match is None:
                raise ValueError("The replyto is malformed")
            replyto = int(match.group(1))

        #Create the SQL statment
          #SQL to test that the message which I am answering does exist
        query1 = 'SELECT * from messages WHERE message_id = ?'
          #SQL Statement for getting the user id given a username
        query2 = 'SELECT user_id from users WHERE username = ?'
          #SQL Statement for inserting the data
        stmnt = 'INSERT INTO messages (title,body,timestamp, \
                 timesviewed,reply_to,username,user_id) \
                 VALUES(?,?,?,?,?,?,?,?)'
          #Variables for the statement.
          #user_id is obtained from first statement.
        user_id = None
        timestamp = time.mktime(datetime.now().timetuple())
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #If exists the replyto argument, check that the message exists in
        #the database table
        if replyto is not None:
            pvalue = (replyto,)
            cur.execute(query1, pvalue)
            messages = cur.fetchall()
            if len(messages) < 1:
                return None
        #Execute SQL Statement to get userid given username
        pvalue = (sender,)
        cur.execute(query2, pvalue)
        #Extract user id
        row = cur.fetchone()
        if row is not None:
            user_id = row["user_id"]
        #Generate the values for SQL statement
        pvalue = (title, body, timestamp, 0, replyto, sender,
                  user_id)
        #Execute the statement
        cur.execute(stmnt, pvalue)
        self.con.commit()
        #Extract the id of the added message
        lid = cur.lastrowid
        #Return the id in
        return 'msg-' + str(lid) if lid is not None else None
   
    #Modified from append_answer
    def append_answer(self, replyto, title, body, sender="Anonymous"):
        '''
        Same as :py:meth:`create_message`. The ``replyto`` parameter is not
        a keyword argument, though.

        :param str replyto: Only provided if this message is an answer to a
            previous message (parent). Otherwise, Null will be stored in the
            database. The id of the message has the format msg-\d{1,3}
        :param str title: the message's title
        :param str body: the message's content
        :param str sender: the nickname of the person who is editing this
            message. If it is not provided "Anonymous" will be stored in db.

        :return: the id of the created message or None if the message was not
            found. Note that 
            the returned value is a string with the format msg-\d{1,3}.

        :raises ForumDatabaseError: if the database could not be modified.
        :raises ValueError: if the replyto has a wrong format.

        '''
        return self.create_message(title, body, sender, replyto)

    #MESSAGE UTILS

    def contains_message(self, messageid):
        '''
        Checks if a message is in the database.

        :param str messageid: Id of the message to search. Note that messageid
            is a string with the format msg-\d{1,3}.
        :return: True if the message is in the database. False otherwise.

        '''
        return self.get_message(messageid) is not None

    #ACCESSING THE USER and USER_PROFILE tables
    def get_users(self):
        '''
        Extracts all users in the database.

        :return: list of Users of the database. Each user is a dictionary
            that contains two keys: ``username``(str) and ``reg_date``
            (long representing UNIX timestamp). None is returned if the database
            has no users.

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the users
        query = 'SELECT users.*, users_profile.* FROM users, users_profile \
                 WHERE users.user_id = users_profile.user_id'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Create the cursor
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute main SQL Statement
        cur.execute(query)
        #Process the results
        rows = cur.fetchall()
        if rows is None:
            return None
        #Process the response.
        users = []
        for row in rows:
            users.append(self._create_user_list_object(row))
        return users

    def get_user(self, username):
        '''
        Extracts all the information of a user.

        :param str nickname: The nickname of the user to search for.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_user_object`

        '''
        #Create the SQL Statements
          #SQL Statement for retrieving the user given a nickname
        query1 = 'SELECT user_id from users WHERE nickname = ?'
          #SQL Statement for retrieving the user information
        query2 = 'SELECT users.*, users_profile.* FROM users, users_profile \
                  WHERE users.user_id = ? \
                  AND users_profile.user_id = users.user_id'
          #Variable to be used in the second query.
        user_id = None
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute SQL Statement to retrieve the id given a nickname
        pvalue = (username,)
        cur.execute(query1, pvalue)
        #Extract the user id
        row = cur.fetchone()
        if row is None:
            return None
        user_id = row["user_id"]
        # Execute the SQL Statement to retrieve the user invformation.
        # Create first the valuse
        pvalue = (user_id, )
        #execute the statement
        cur.execute(query2, pvalue)
        #Process the response. Only one posible row is expected.
        row = cur.fetchone()
        return self._create_user_object(row)

    def delete_user(self, username):
        '''
        Remove all user information of the user with the nickname passed in as
        argument.

        :param str nickname: The nickname of the user to remove.

        :return: True if the user is deleted, False otherwise.

        '''
        #Create the SQL Statements
          #SQL Statement for deleting the user information
        query = 'DELETE FROM users WHERE nickname = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the statement to delete
        pvalue = (username,)
        cur.execute(query, pvalue)
        self.con.commit()
        #Check that it has been deleted
        if cur.rowcount < 1:
            return False
        return True

    # TODO def modify_user(self, nickname, user)
    # TODO def def append_user(self, nickname, user)


    # UTILS
    def get_user_id(self, username):
        '''
        Get the key of the database row which contains the user with the given
        username.

        :param str username: The username of the user to search.
        :return: the database attribute user_id or None if ``username`` does
            not exit.
        :rtype: str

        '''

        query = 'SELECT user_id FROM users WHERE username = ?'
        #Activate foreign key support
        self.set_foreign_keys_support()
        #Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        #Execute the  main SQL statement
        pvalue = (username,)
        cur.execute(query, pvalue)
        #Process the response.
        #Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        #Build the return object
        else:
            return row[0]

    def contains_user(self, username):
        '''
        :return: True if the user is in the database. False otherwise
        '''
        return self.get_user_id(username) is not None