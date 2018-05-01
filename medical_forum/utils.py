# coding= utf-8
'''
Created on 26.01.2013
Modified on 26.03.2018
@author: mika oja
@author: ivan
'''

import sqlite3
from werkzeug.routing import BaseConverter

FOREIGN_KEYS_ON = 'PRAGMA foreign_keys = ON'


class RegexConverter(BaseConverter):
    '''
    This class is used to allow regex expressions as converters in the url
    '''

    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def execute_query(connection, query, pvalue, fetch_type=''):
    """
    This is a helper method to facilitate and be used by many methods.
    This method is used to handle the execution of queries and return the result of that query.
    :param self: to pass the context of the parent method.
    :param query: the query to execute.
    :param fetch_type: whether to return one or all results from the cursor instance
            after query execution.
    :return: Either one or all tuple of results.
    """

    with connection:
        # Cursor and row initialization
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        # Provide support for foreign keys
        cursor.execute(FOREIGN_KEYS_ON)
        # Execute main SQL Statement
        cursor.execute(query, pvalue)
        if fetch_type == 'one':
            return cursor.fetchone()
        elif fetch_type == 'lastid':
            return cursor.lastrowid
        elif fetch_type == 'commit':
            return connection.commit()
        return cursor.fetchall()
