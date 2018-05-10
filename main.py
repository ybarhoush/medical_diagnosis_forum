"""
Main medical forum server
"""

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from medical_forum.resources import APP as forum_server
from client_web.client import APP as client_web

CLIENT = DispatcherMiddleware(forum_server, {
    '/medical_forum/client': client_web
})

if __name__ == '__main__':
    run_simple('localhost', 5000, CLIENT,
               use_reloader=True, use_debugger=True, use_evalex=True)
