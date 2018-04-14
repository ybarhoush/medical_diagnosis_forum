"""
Error handling methods for the medical forum request
"""

import json
from flask import request, Response, _request_ctx_stack
from .mason_object import MasonObject
from . import hypermedia_formats as hyper_const
from .api import APP


def create_error_response(status_code, title, message=None):
    """
    Creates a: py: class:`flask.Response` instance when sending back an
    HTTP error response

    : param integer status_code: The HTTP status code of the response
    : param str title: A short description of the problem
    : param message: A long description of the problem
    : rtype:: py: class:`flask.Response`
    """

    resource_url = None
    # We need to access the context in order to access the request.path
    context = _request_ctx_stack.top
    if context is not None:
        resource_url = request.path
    envelope = MasonObject(resource_url=resource_url)
    envelope.add_error(title, message)

    return Response(json.dumps(envelope), status_code, mimetype=hyper_const.MASON + ";" +
                    hyper_const.ERROR_PROFILE)


@APP.errorhandler(404)
def resource_not_found(error):
    """Return error 404 not found"""
    return create_error_response(
        404, "Resource not found", "This resource url does not exit")


@APP.errorhandler(400)
def resource_malformed_input_format(error):
    """Return error 400 malformed input format"""
    return create_error_response(
        400, "Malformed input format", "The format of the input is incorrect")


@APP.errorhandler(500)
def unknown_error(error):
    """Return error 500 unkown error"""
    return create_error_response(
        500, "Error", "The system has failed. Please, contact the administrator")
