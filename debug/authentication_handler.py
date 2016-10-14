"""
This file is expected to take a request and return the Authentication status of the requestor

The authetication status has not been decided if it will be true/false if allowed/disallowed or
a permission level that the request_handler is expected to interpreted.

It might be best to have this file contain decorators (instead of a class) that can simply
be added to the app routes defined in the request_handler. (if using flask framework)
"""

import db

class AuthenticationHandler(object):
    pass