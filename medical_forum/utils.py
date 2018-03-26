# coding= utf-8
'''
Created on 26.01.2013
Modified on 26.03.2018
@author: mika oja
@author: ivan
'''

from werkzeug.routing import BaseConverter

class RegexConverter(BaseConverter):
    '''
    This class is used to allow regex expressions as converters in the url
    '''
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]