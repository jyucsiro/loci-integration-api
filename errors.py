# -*- coding: utf-8 -*-
#
from sanic import exceptions
class ReportableAPIError(exceptions.ServerError):
    def __init__(self, message):
        super().__init__(message)
