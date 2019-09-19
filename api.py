# -*- coding: utf-8 -*-
#
from collections import OrderedDict
from sanic.response import json, text, HTTPResponse
from sanic.request import Request
from sanic.exceptions import ServiceUnavailable
from sanic_restplus import Api, Resource, fields

from functions import get_linksets, get_datasets, get_locations, get_location_is_within, get_location_contains

url_prefix = 'api/v1'

api_v1 = Api(title="LOCI Integration API",
             version="1.0",
             prefix=url_prefix, doc='/'.join([url_prefix, "doc"]),
             default_mediatype="application/json",
             additional_css="/static/material_swagger.css")
ns = api_v1.default_namespace

@ns.route('/linksets')
class Linkset(Resource):
    """Operations on LOCI Linksets"""

    @ns.doc('get_linksets', params=OrderedDict([
        ("count", {"description": "Number of linksets to return.",
                   "required": False, "type": "number", "format": "integer", "default": 1000}),
        ("offset", {"description": "Skip number of linksets before returning count.",
                    "required": False, "type": "number", "format": "integer", "default": 0}),
    ]), security=None)
    async def get(self, request, *args, **kwargs):
        """Gets all LOCI Linksets"""
        count = int(next(iter(request.args.getlist('count', [1000]))))
        offset = int(next(iter(request.args.getlist('offset', [0]))))
        meta, linksets = await get_linksets(count, offset)
        response = {
            "meta": meta,
            "linksets": linksets,
        }
        return json(response, status=200)


@ns.route('/datasets')
class Dataset(Resource):
    """Operations on LOCI Datasets"""

    @ns.doc('get_datasets', params=OrderedDict([
        ("count", {"description": "Number of datasets to return.",
                   "required": False, "type": "number", "format": "integer", "default": 1000}),
        ("offset", {"description": "Skip number of datasets before returning count.",
                    "required": False, "type": "number", "format": "integer", "default": 0}),
    ]), security=None)
    async def get(self, request, *args, **kwargs):
        """Gets all LOCI Datasets"""
        count = int(next(iter(request.args.getlist('count', [1000]))))
        offset = int(next(iter(request.args.getlist('offset', [0]))))
        meta, datasets = await get_datasets(count, offset)
        response = {
            "meta": meta,
            "datasets": datasets,
        }
        return json(response, status=200)

@ns.route('/locations')
class Location(Resource):
    """Operations on LOCI Locations"""

    @ns.doc('get_locations', params=OrderedDict([
        ("count", {"description": "Number of locations to return.",
                   "required": False, "type": "number", "format": "integer", "default": 1000}),
        ("offset", {"description": "Skip number of locations before returning count.",
                    "required": False, "type": "number", "format": "integer", "default": 0}),
    ]), security=None)
    async def get(self, request, *args, **kwargs):
        """Gets all LOCI Locations"""
        count = int(next(iter(request.args.getlist('count', [1000]))))
        offset = int(next(iter(request.args.getlist('offset', [0]))))
        meta, locations = await get_locations(count, offset)
        response = {
            "meta": meta,
            "locations": locations,
        }
        return json(response, status=200)


## The following are non-standard usage of REST/Swagger.
## These are function routes, not resources. But we still define them as an API resource,
## so that they get a GET endpoint and they get auto-documented.


ns_loc_func = api_v1.namespace(
    "loc-func", "Location Functions",
    api=api_v1,
    path='/location/',
)
@ns_loc_func.route('/within')
class Within(Resource):
    """Function for location is Within"""

    @ns.doc('get_location_within', params=OrderedDict([
        ("uri", {"description": "Target LOCI Location/Feature URI",
                    "required": True, "type": "string"}),
        ("count", {"description": "Number of locations to return.",
                   "required": False, "type": "number", "format": "integer", "default": 1000}),
        ("offset", {"description": "Skip number of locations before returning count.",
                    "required": False, "type": "number", "format": "integer", "default": 0}),
    ]), security=None)
    async def get(self, request, *args, **kwargs):
        """Gets all LOCI Locations that this target LOCI URI is within"""
        count = int(next(iter(request.args.getlist('count', [1000]))))
        offset = int(next(iter(request.args.getlist('offset', [0]))))
        target_uri = str(next(iter(request.args.getlist('uri'))))
        meta, locations = await get_location_is_within(target_uri, count, offset)
        response = {
            "meta": meta,
            "locations": locations,
        }
        return json(response, status=200)

@ns_loc_func.route('/contains')
class Contains(Resource):
    """Function for location Contains"""

    @ns.doc('get_location_contains', params=OrderedDict([
        ("uri", {"description": "Target LOCI Location/Feature URI",
                    "required": True, "type": "string"}),
        ("count", {"description": "Number of locations to return.",
                   "required": False, "type": "number", "format": "integer", "default": 1000}),
        ("offset", {"description": "Skip number of locations before returning count.",
                    "required": False, "type": "number", "format": "integer", "default": 0}),
    ]), security=None)
    async def get(self, request, *args, **kwargs):
        """Gets all LOCI Locations that this target LOCI URI contains"""
        count = int(next(iter(request.args.getlist('count', [1000]))))
        offset = int(next(iter(request.args.getlist('offset', [0]))))
        target_uri = str(next(iter(request.args.getlist('uri'))))
        meta, locations = await get_location_contains(target_uri, count, offset)
        response = {
            "meta": meta,
            "locations": locations,
        }
        return json(response, status=200)
