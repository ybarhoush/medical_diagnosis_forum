"""
Created on 13.02.2013

Modified on 14.04.2018

Provides the database API to access the forum persistent data.

@author: ivan
@author: mika
@author: yazan
@author: Issam
"""

from datetime import datetime
import time
import sqlite3
import re
from .utils import execute_query

DEFAULT_DB_PATH = 'db/medical_forum_data.db'
DEFAULT_SCHEMA = "db/medical_forum_data_schema.sql"
DEFAULT_DATA_DUMP = "db/medical_forum_data_dump.sql"
DOCTOR = 1
PATIENT = 0

# Copied Class from Exercise 1
# We state if a method is copied, modified or written from scratch before it


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

    def check_foreign_keys_status(self):
        """
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.
        """
        try:
            cursor = self.con.cursor()
            cursor.execute('PRAGMA foreign_keys')
            data = cursor.fetchone()
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
            cursor = self.con.cursor()
            cursor.execute(keys_on)
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
            cursor = self.con.cursor()
            cursor.execute(keys_on)
            return True
        except sqlite3.Error as excp:
            print("Error %s:" % excp.args[0])
            return False

    # Helpers for messages
    # Modified from _create_message_object
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
            * ``reply_to``: The id of the parent message. String with the format
              msg-{id}. Its value can be None.
            * ``sender``: The username of the message's creator.

            Note that all values in the returned dictionary are string unless
            otherwise stated.
        """
        message_id = 'msg-' + str(row['message_id'])
        message_reply_to = 'msg-' + str(row['reply_to']) \
            if row['reply_to'] is not None else None
        message_sender = row['username']
        message_title = row['title']
        message_body = row['body']
        message_timestamp = row['timestamp']
        message = {'message_id': message_id, 'title': message_title,
                   'timestamp': message_timestamp, 'reply_to': message_reply_to,
                   'body': message_body, 'sender': message_sender, 'user_id': row['user_id']}
        return message

    # Modified from _create_message_list_object
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

    def _create_diagnoses_list_object(self, row):
        """
        Same as :py:meth:`_create_message_object`. However, the resulting
        dictionary is targeted to build messages in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``message_id``, ``title``,
            ``timestamp`` and ``sender``.
        """
        diagnosis_id = 'dgs-' + str(row['diagnosis_id'])
        user_id = row['user_id']
        message_id = row['message_id']
        disease = row['disease']
        diagnosis_description = row['diagnosis_description']
        diagnoses = {'diagnosis_id': diagnosis_id, 'message_id': message_id,
                     'disease': disease, 'user_id': user_id,
                     'diagnosis_description': diagnosis_description}
        return diagnoses

    # Helpers for users
    # Modified from _create_user_object
    def _create_user_object(self, row):
        """
        It takes a database Row and transform it into a python dictionary.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the following format:

            .. code-block:: javascript

                {'public_profile':{'reg_date':,'username':'',
                                   'speciality':'','user_type':''},
                'restricted_profile':{'firstname':'','lastname':'',
                                      'work_address':'','gender':'',
                                      'picture':'', age':'', email':''}
                }

            where:

            * ``reg_date``: UNIX timestamp when the user registered in
                                 the system (long integer)
            * ``user_type``: either a patient or a doctor
            * ``username``: username of the user
            * ``speciality``: text chosen by the user for speciality
            * ``age``: name of the image file used as age
            * ``firstname``: given name of the user
            * ``lastname``: family name of the user
            * ``phone``: string showing the user's phone number. Can be None.
            * ``work_address``: complete user's work address.
            * ``picture``: file which contains an image of the user.
            * ``gender``: User's gender ('male' or 'female').
            * ``email``: User's email.

            Note that all values are string if they are not otherwise indicated.
        """
        reg_date = row['reg_date']
        return {'public_profile': {'reg_date': reg_date,
                                   'username': row['username'],
                                   'picture': row['picture'],
                                   'user_id': row['user_id'],
                                   'user_type': row['user_type'],
                                   'speciality': row['speciality']},
                'restricted_profile': {'user_id': row['user_id'], 'firstname': row['firstname'],
                                       'lastname': row['lastname'],
                                       'work_address': row['work_address'],
                                       'phone': row['phone'],
                                       'gender': row['gender'],
                                       'age': row['age'],
                                       'email': row['email'],
                                       'diagnosis_id': row['diagnosis_id'],
                                       'height': row['height'],
                                       'weight': row['weight']}}

    # Modified from _create_user_list_object
    def _create_user_list_object(self, row):
        """
        Same as :py:meth:`_create_user_object`. However, the resulting
        dictionary is targeted to build users in a list.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary with the keys ``reg_date`` and
            ``username``
        """
        return {'user_id': row['user_id'], 'reg_date': row['reg_date'], 'username': row['username'],
                'user_type': row['user_type'], 'speciality': row['speciality'],
                'picture': row['picture']}

    # Helpers for diagnosis
    # Written from scratch
    def _create_diagnosis_object(self, row):
        """
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
        """
        user_id = row['user_id']
        message_id = 'msg-' + str(row['message_id'])
        disease = row['disease']
        diagnosis_description = row['diagnosis_description']

        diagnosis = {'user_id': user_id,
                     'message_id': message_id,
                     'disease': disease, 'diagnosis_description': diagnosis_description}
        return diagnosis

    # API ITSELF
    # Diagnosis Table API.
    def get_diagnosis(self, diagnosis_id):
        """
        Extracts a diagnosis from the database.

        :param diagnosis_id: The id of the diagnosis. Note that diagnosis_id is a
            string with format ``dgs-\d{1,3}``.
        :return: A dictionary with the format provided in
            :py:meth:`_create_diagnosis_object` or None if the diagnosis with target
            id does not exist.
        :raises ValueError: when ``diagnosis_id`` is not well formed
        """
        diagnosis_id_int = re.match(r'dgs-(\d{1,3})', diagnosis_id)
        if diagnosis_id_int is None:
            raise ValueError("The diagnosis is malformed")
        diagnosis_id = int(diagnosis_id_int.group(1))
        self.set_foreign_keys_support()
        query = 'SELECT * FROM diagnosis WHERE diagnosis_id = ?'
        self.con.row_factory = sqlite3.Row
        cursor = self.con.cursor()
        pvalue = (diagnosis_id,)
        cursor.execute(query, pvalue)

        row = cursor.fetchone()
        if row is None:
            return None
        return self._create_diagnosis_object(row)

    # TODO get_diagnoses --Extra
    # Return a list of all the diagnoses in the database
    # Modified from get_messages
    def get_diagnoses(self, message_id=None, user_id=None, number_of_diagnoses=-1):
        """
        Return a list of all the messages in the database filtered by the
        conditions provided in the parameters.

        :param username: default None. Search messages of a user with the given
            username. If this parameter is None, it returns the messages of
            any user in the system.
        :type username: str
        :param number_of_messages: default -1. Sets the maximum number of
            messages returning in the list. If set to -1, there is no limit.
        :type number_of_messages: int
        :param before: All timestamps > ``before`` (UNIX timestamp) are removed.
            If set to -1, this condition is not applied.
        :type before: long
        :param after: All timestamps < ``after`` (UNIX timestamp) are removed.
            If set to -1, this condition is not applied.
        :type after: long

        :return: A list of messages. Each message is a dictionary containing
            the following keys:

            * ``user_id``: string with the format msg-\d{1,3}.Id of the
                message.
            * ``sender``: username of the message's author.
            * ``title``: string containing the title of the message.
            * ``timestamp``: UNIX timestamp (long int) that specifies when the
                message was created.

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        :raises ValueError: if ``before`` or ``after`` are not valid UNIX
            timestamps
        """
        select_all_dgs_query = 'SELECT * FROM diagnosis'
        if user_id is not None:
            select_all_dgs_query += " WHERE user_id = '%s'" % user_id
        if message_id is not None:
            message_id_int = re.match(r'msg-(\d{1,3})', message_id)
            if message_id_int is None:
                raise ValueError("The message id is malformed")
            message_id_n = int(message_id_int.group(1))
            select_all_dgs_query += " WHERE message_id = '%s'" % message_id_n

        select_all_dgs_query += ' ORDER BY diagnosis_id ASC'
        if number_of_diagnoses > -1:
            select_all_dgs_query += ' LIMIT ' + str(number_of_diagnoses)
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cursor = self.con.cursor()
        cursor.execute(select_all_dgs_query)

        rows = cursor.fetchall()
        if rows is None:
            return None

        diagnoses = []
        for row in rows:
            diagnosis = self._create_diagnoses_list_object(row)
            diagnoses.append(diagnosis)
        return diagnoses

    # Written from scratch
    def create_diagnosis(self, diagnosis):
        """
        Create a new diagnosis with the data provided as arguments.

        :param diagnosis : the diagnosis object

        :return: the id of the created message or None if the message was not
            found. Note that the returned value is a string with the format msg-\d{1,3}.

        :raises ForumDatabaseError: if the database could not be modified.
        """
        query_user = 'SELECT user_id, user_type from users_profile WHERE user_id = ?'
        query_msg = 'SELECT message_id from messages WHERE message_id = ?'
        insert_data_query = ('INSERT INTO diagnosis(disease, diagnosis_description, message_id, '
                             'user_id) VALUES(?,?,?,?)')

        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cursor = self.con.cursor()

        user_id = diagnosis['user_id']
        if user_id is None:
            raise ValueError("User is not valid")
        cursor.execute(query_user, (user_id,))

        row = cursor.fetchone()
        if row is None:
            return None
        if row['user_type'] != DOCTOR:
            raise ValueError("the user is not a doctor")

        message_id_int = re.match(r'msg-(\d{1,3})', diagnosis['message_id'])
        if message_id_int is None:
            raise ValueError("The message_id is malformed")
        message_id = int(message_id_int.group(1))
        cursor.execute(query_msg, (message_id,))
        row = cursor.fetchone()
        if row is None:
            return None

        disease = diagnosis['disease']
        diagnosis_description = diagnosis['diagnosis_description']
        pvalue = (disease, diagnosis_description, message_id, user_id)
        cursor.execute(insert_data_query, pvalue)
        self.con.commit()

        last_id = cursor.lastrowid
        return 'dgs-' + str(last_id) if last_id is not None else None

    # TODO def delete_diagnosis(self, diagnosis_id) --Extra

    def modify_diagnosis(self, diagnosis_id, disease, diagnosis_description):
        """"
        Modifies the disease and description of a diagnosis
        """
        # TODO def modify_diagnosis(self, diagnosis_id, disease,
        # diagnosis_description) --Extra

    # TODO def append_diagnosis(self, reply_to, disease, diagnosis_description, sender) --Needed?

    # Message Table API
    # Modified from get_message
    def get_message(self, message_id):
        """
        Extracts a message from the database.

        :param message_id: The id of the message. Note that message_id is a
            string with format ``msg-\d{1,3}``.
        :return: A dictionary with the format provided in
            :py:meth:`_create_message_object` or None if the message with target
            id does not exist.
        :raises ValueError: when ``message_id`` is not well formed
        """
        message_id_int = re.match(r'msg-(\d{1,3})', message_id)
        if message_id_int is None:
            raise ValueError("The message_id is malformed")
        message_id = int(message_id_int.group(1))
        self.set_foreign_keys_support()
        query = 'SELECT * FROM messages WHERE message_id = ?'
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        cur.execute(query, (message_id,))
        row = cur.fetchone()
        if row is None:
            return None

        return self._create_message_object(row)

    # Modified from get_messages
    def get_messages(self, username=None, number_of_messages=-1,
                     before=-1, after=-1):
        """
        Return a list of all the messages in the database filtered by the
        conditions provided in the parameters.

        :param username: default None. Search messages of a user with the given
            username. If this parameter is None, it returns the messages of
            any user in the system.
        :type username: str
        :param number_of_messages: default -1. Sets the maximum number of
            messages returning in the list. If set to -1, there is no limit.
        :type number_of_messages: int
        :param before: All timestamps > ``before`` (UNIX timestamp) are removed.
            If set to -1, this condition is not applied.
        :type before: long
        :param after: All timestamps < ``after`` (UNIX timestamp) are removed.
            If set to -1, this condition is not applied.
        :type after: long

        :return: A list of messages. Each message is a dictionary containing
            the following keys:

            * ``message_id``: string with the format msg-\d{1,3}.Id of the
                message.
            * ``sender``: username of the message's author.
            * ``title``: string containing the title of the message.
            * ``timestamp``: UNIX timestamp (long int) that specifies when the
                message was created.

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        :raises ValueError: if ``before`` or ``after`` are not valid UNIX
            timestamps
        """
        select_all_msg_query = 'SELECT * FROM messages'
        if username is not None or before != -1 or after != -1:
            select_all_msg_query += ' WHERE'
        if username is not None:
            select_all_msg_query += " username = '%s'" % username

        if before != -1:
            if username is not None:
                select_all_msg_query += ' AND'
            select_all_msg_query += " timestamp < %s" % str(before)

        if after != -1:
            if username is not None or before != -1:
                select_all_msg_query += ' AND'
            select_all_msg_query += " timestamp > %s" % str(after)

        select_all_msg_query += ' ORDER BY timestamp DESC'
        if number_of_messages > -1:
            select_all_msg_query += ' LIMIT ' + str(number_of_messages)
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cursor = self.con.cursor()
        cursor.execute(select_all_msg_query)

        rows = cursor.fetchall()
        if rows is None:
            return None

        messages = []
        for row in rows:
            message = self._create_message_list_object(row)
            messages.append(message)
        return messages

    # Modified from delete_message
    def delete_message(self, message_id):
        """
        Delete the message with id given as parameter.

        :param str message_id: id of the message to remove.Note that message_id
            is a string with format ``msg-\d{1,3}``
        :return: True if the message has been deleted, False otherwise
        :raises ValueError: if the message_id has a wrong format.
        """
        message_id_int = re.match(r'msg-(\d{1,3})', message_id)
        if message_id_int is None:
            raise ValueError("The message_id is malformed")
        message_id = int(message_id_int.group(1))

        delete_diagnosis_query = 'DELETE FROM diagnosis WHERE message_id = ?'
        delete_message_query = 'DELETE FROM messages WHERE message_id = ?'
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cursor = self.con.cursor()
        try:
            cursor.execute(delete_diagnosis_query, (message_id,))
            cursor.execute(delete_message_query, (message_id,))
            self.con.commit()
        except sqlite3.Error as exception:
            print("Error %s:" % (exception.args[0]))

        if cursor.rowcount >= 1:
            return True
        return False

    # Modified from modify_message
    def modify_message(self, message_id, title, body):
        """
        Modify the title, the body and the editor of the message with id
        ``message_id``

        :param str message_id: The id of the message to remove. Note that
            message_id is a string with format msg-\d{1,3}
        :param str title: the message's title
        :param str body: the message's content
        :return: the id of the edited message or None if the message was
              not found. The id of the message has the format ``msg-\d{1,3}``,
              where \d{1,3} is the id of the message in the database.
        :raises ValueError: if the message_id has a wrong format.
        """
        message_id_int = re.match(r'msg-(\d{1,3})', message_id)
        if message_id_int is None:
            raise ValueError("The message_id is malformed")
        message_id = int(message_id_int.group(1))

        update_message_query = ('UPDATE messages SET title=:title , '
                                'body=:body WHERE message_id =:msg_id')
        self.set_foreign_keys_support()
        self.con.row_factory = sqlite3.Row
        cursor = self.con.cursor()
        pvalue = {"msg_id": message_id,
                  "title": title,
                  "body": body}
        try:
            cursor.execute(update_message_query, pvalue)
            self.con.commit()
        except sqlite3.Error as exception:
            print("Error %s:" % (exception.args[0]))
        else:
            if cursor.rowcount < 1:
                return None
        return 'msg-%s' % message_id

    # Modified from create_message
    def create_message(self, title, body, sender, reply_to=None):
        """
        Create a new message with the data provided as arguments.

        :param str title: the message's title
        :param str body: the message's content
        :param str sender: the username of the person who is editing this message.
        :param str reply_to: Only provided if this message is an answer to a
            previous message (parent). Otherwise, Null will be stored in the
            database. The id of the message has the format msg-\d{1,3}

        :return: the id of the created message or None if the message was not
            found. Note that the returned value is a string with the format msg-\d{1,3}.

        :raises ForumDatabaseError: if the database could not be modified.
        :raises ValueError: if the reply_to has a wrong format.

        """
        # Extracts the int which is the id for a message in the database
        if reply_to is not None:
            match = re.match('msg-(\d{1,3})', reply_to)
            if match is None:
                raise ValueError("The reply_to is malformed")
            reply_to = int(match.group(1))

        # Create the SQL statement
        # SQL to test that the message which I am answering does exist
        query1 = 'SELECT * from messages WHERE message_id = ?'
        # SQL Statement for getting the user id given a username
        query2 = 'SELECT user_id from users WHERE username = ?'
        # SQL Statement for inserting the data
        stmnt = ('INSERT INTO messages(title, body, timestamp, views,'
                 'reply_to, username, user_id) VALUES(?,?,?,?,?,?,?)')
        # Variables for the statement.
        timestamp = time.mktime(datetime.now().timetuple())
        # If exists the reply_to argument, check that the message exists in
        # the database table
        if reply_to is not None:
            messages = execute_query(self.con, query1, (reply_to,))
            if len(messages) < 1:
                return None

        row = execute_query(self.con, query2, (sender, ), 'one')
        if row is not None:
            user_id = row["user_id"]
        else:
            raise KeyError("User is not valid")

        pvalue = (title, body, timestamp, 0, reply_to, sender, user_id)
        last_id = execute_query(self.con, stmnt, pvalue, 'lastid')
        return 'msg-' + str(last_id) if last_id is not None else None

    # Modified from append_answer
    def append_answer(self, reply_to, title, body, sender):
        """
        Same as :py:meth:`create_message`. The ``reply_to`` parameter is not
        a keyword argument, though.

        :param str reply_to: Only provided if this message is an answer to a
            previous message (parent). Otherwise, Null will be stored in the
            database. The id of the message has the format msg-\d{1,3}
        :param str title: the message's title
        :param str body: the message's content
        :param str sender: the username of the person who is editing this
            message.

        :return: the id of the created message or None if the message was not
            found. Note that
            the returned value is a string with the format msg-\d{1,3}.

        :raises ForumDatabaseError: if the database could not be modified.
        :raises ValueError: if the reply_to has a wrong format.

        """
        return self.create_message(title, body, sender, reply_to)

    # MESSAGE UTILS
    # Copied from contains_message
    def contains_message(self, message_id):
        """
        Checks if a message is in the database.

        :param str message_id: Id of the message to search. Note that message_id
            is a string with the format msg-\d{1,3}.
        :return: True if the message is in the database. False otherwise.

        """
        return self.get_message(message_id) is not None

    # ACCESSING THE USER and USER_PROFILE tables
    # Modified from get_users
    def get_users(self):
        '''
        Extracts all users in the database.

        :return: list of Users of the database. Each user is a dictionary
            that contains tswo keys: ``username``(str) and ``reg_date``
            (long representing UNIX timestamp). None is returned if the database
            has no users.

        '''
        # Create the SQL Statements
        # SQL Statement for retrieving the users
        query = 'SELECT users.*, users_profile.* FROM users, users_profile \
                 WHERE users.user_id = users_profile.user_id'
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Create the cursor
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement
        cur.execute(query)
        # Process the results
        rows = cur.fetchall()
        if rows is None:
            return None
        # Process the response.
        users = []
        for row in rows:
            users.append(self._create_user_list_object(row))
        return users

    # Modified from get_users
    def get_user(self, username):
        '''
        Extracts all the information of a user.

        :param str username: The username of the user to search for.
        :return: dictionary with the format provided in the method:
            :py:meth:`_create_user_object
        '''
        # Create the SQL Statements
        # SQL Statement for retrieving the user given a username
        query1 = 'SELECT user_id from users WHERE username = ?'
        # SQL Statement for retrieving the user information
        query2 = ('SELECT users.*, users_profile.* FROM users, users_profile '
                  'WHERE users.user_id = ? AND users_profile.user_id = users.user_id')
        # Variable to be used in the second query.
        user_id = None
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute SQL Statement to retrieve the id given a username
        pvalue = (username,)
        cur.execute(query1, pvalue)
        # Extract the user id
        row = cur.fetchone()
        if row is None:
            return None
        user_id = row["user_id"]
        # Execute the SQL Statement to retrieve the user invformation.
        # Create first the valuse
        pvalue = (user_id,)
        # execute the statement
        cur.execute(query2, pvalue)
        # Process the response. Only one posible row is expected.
        row = cur.fetchone()
        return self._create_user_object(row)

    # Modified from delete_user
    def delete_user(self, username):
        '''
        Remove all user information of the user with the username passed in as
        argument.

        :param str username: The username of the user to remove.

        :return: True if the user is deleted, False otherwise.

        '''
        # Create the SQL Statements
        # get the user_id for username
        query = 'SELECT user_id FROM users WHERE username = ?'
        # execute the statement
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        cur.execute(query, (username, ))
        # Process the response. Only one possible row is expected.
        row = cur.fetchone()
        if row is not None:
            user_id = row['user_id']
        else:
            raise ValueError("the username doesn't exist!")

        # SQL Statement for deleting the user information
        query_d = 'DELETE FROM diagnosis WHERE user_id = ?'
        query_m = 'DELETE FROM messages WHERE user_id = ?'
        query_p = 'DELETE FROM users_profile WHERE user_id = ?'
        query_u = 'DELETE FROM users WHERE username = ?'

        # Execute the statement to delete
        cur.execute(query_d, (user_id,))
        cur.execute(query_m, (user_id,))
        cur.execute(query_p, (user_id,))
        cur.execute(query_u, (username,))
        self.con.commit()
        # Check that it has been deleted
        if cur.rowcount < 1:
            return False
        return True

    # Modified from modify_user
    def modify_user(self, username, p_profile, r_profile):
        '''
        Modify the information of a user.

        :param str username: The username of the user to modify
        :param dict p_profile: a dictionary with the public information
                to be modified. The dictionary has the following structure:
        :param dict r_profile: a dictionary with the restricted inforamtion
                to be modified. The dictionary has the following structure:
                .. code-block:: javascript

                    {'public_profile':{'reg_date':,'username':'',
                                       'speciality':'', user_type':''},
                    'restricted_profile':{'firstname':'','lastname':'',
                                          'work_address':'','gender':'',
                                          'picture':'', 'age':'', 'email':''}
                    }

                where:

                * ``reg_date``: UNIX timestamp when the user registered in
                                     the system (long integer)
                * ``user_type``: can either be a doctor or patient
                * ``username``: username of the user
                * ``speciality``: text chosen by the user for speciality
                * ``age``: name of the image file used as age
                * ``firstanme``: given name of the user
                * ``lastname``: family name of the user
                * ``work_address``: complete user's work address.
                * ``picture``: file which contains an image of the user.
                * ``gender``: User's gender ('male' or 'female').
                * ``email``: User's email.

                Note that all values are string if they are not otherwise indicated.

        :return: the username of the modified user or None if the
            ``username`` passed as parameter is not  in the database.
        :raise ValueError: if the user argument is not well formed.
        '''
        # Create the SQL Statements
        # SQL Statement for extracting the userid given a username
        query1 = 'SELECT user_id from users WHERE username = ?'
        # SQL Statement to update the user_profile table
        query2 = 'UPDATE users_profile SET firstname = ?,lastname = ?, speciality = ?, \
                    picture = ?, work_address = ?, gender = ? , age = ?, email = ? \
                    WHERE user_id = ?'
        # temporal variables
        user_id = None
        _firstname = None if not r_profile else r_profile.get(
            'firstname', None)
        _lastname = None if not r_profile else r_profile.get('lastname', None)
        _speciality = None if not p_profile else p_profile.get(
            'speciality', None)
        _work_address = None if not r_profile else r_profile.get(
            'work_address', None)
        _gender = None if not r_profile else r_profile.get('gender', None)
        _age = None if not r_profile else r_profile.get('age', None)
        _picture = None if not r_profile else r_profile.get('picture', None)
        _email = None if not r_profile else r_profile.get('email', None)

        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute the statement to extract the id associated to a username
        pvalue = (username,)
        cur.execute(query1, pvalue)
        # Only one value expected
        row = cur.fetchone()
        # if does not exist, return
        if row is None:
            return None
        else:
            user_id = row["user_id"]
            # execute the main statement
            pvalue = (_firstname, _lastname, _speciality, _picture,
                      _work_address, _gender, _age, _email, user_id)
            cur.execute(query2, pvalue)
            self.con.commit()
            # Check that I have modified the user
            if cur.rowcount < 1:
                return None
            return username

    # Modified from append_user
    def append_user(self, username, user):
        '''
        Create a new user in the database.

        :param str username: The username of the user to modify
        :param dict user: a dictionary with the information to be modified. The
                dictionary has the following structure:

                .. code-block:: javascript

                    {'public_profile':{'reg_date':,'username':'',
                                       'speciality':'', user_type':''},
                    'restricted_profile':{'firstname':'','lastname':'',
                                          'work_address':'','gender':'',
                                          'picture':'', 'age':'', 'email':''}
                    }

                where:

                * ``reg_date``: UNIX timestamp when the user registered in
                                     the system (long integer)
                * ``user_type``: can either be a doctor or patient
                * ``username``: username of the user
                * ``speciality``: text chosen by the user for speciality
                * ``age``: name of the image file used as age
                * ``firstanme``: given name of the user
                * ``lastname``: family name of the user
                * ``phone``: string showing the user's phone number. Can be None.
                * ``work_address``: complete user's work address.
                * ``picture``: file which contains an image of the user.
                * ``gender``: User's gender ('male' or 'female').
                * ``email``: User's email

                Note that all values are string if they are not otherwise indicated.

        :return: the username of the modified user or None if the
            ``username`` passed as parameter is not  in the database.
        :raise ValueError: if the user argument is not well formed.

        '''
        select_user_query = 'SELECT user_id FROM users WHERE username = ?'
        insert_user_query = 'INSERT INTO users(username,reg_date,last_login, pass_hash) VALUES(?,?,?,?)'
        insert_user_profile_query = (
            'INSERT INTO users_profile (user_id, firstname,lastname, speciality, picture, '
            'age, work_address, gender, email, user_type, phone, weight, height) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)')
        # temporal variables for user table
        # timestamp will be used for last login and reg_date.
        timestamp = time.mktime(datetime.now().timetuple())
        # TODO pass_hash = user['pass_hash']
        pass_hash = 'pass_hash'
        # temporal variables for user profiles
        p_profile = user['public_profile']
        r_profile = user['restricted_profile']
        _firstname = r_profile.get('firstname', None)
        _lastname = r_profile.get('lastname', None)
        _speciality = p_profile.get('speciality', None)
        _picture = r_profile.get('picture', None)
        _age = r_profile.get('age', None)
        _work_address = r_profile.get('work_address', None)
        _gender = r_profile.get('gender', None)
        _email = r_profile.get('email', None)
        _user_type = p_profile.get('user_type', None)
        _phone = r_profile.get('phone', None)
        _weight = r_profile.get('weight', None)
        _height = r_profile.get('height', None)

        row = execute_query(self.con, select_user_query, (username, ), 'one')
        # If there is no user add rows in user and user profile
        if row is None:
            pvalue = (username, timestamp, timestamp, pass_hash)
            lid = execute_query(self.con, insert_user_query, pvalue, 'lastid')
            pvalue = (
                lid, _firstname, _lastname, _speciality, _picture, _age,
                _work_address, _gender, _email, _user_type, _phone, _weight, _height)

            execute_query(self.con, insert_user_profile_query,
                          pvalue, 'commit')
            return username

        return None

    # UTILS
    # Modified from get_user_id
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
        row = execute_query(self.con, query, (username, ), 'one')
        if row is None:
            return None
        return row[0]

    # Modified from contains_user
    def contains_user(self, username):
        '''
        :return: True if the user is in the database. False otherwise
        '''
        return self.get_user_id(username) is not None

    def contains_diagnosis(self, diagnosis_id):
        '''
        :return: True if the user is in the database. False otherwise
        '''
        return self.get_diagnosis(diagnosis_id) is not None
