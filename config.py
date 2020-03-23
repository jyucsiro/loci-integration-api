# -*- coding: utf-8 -*-
#
import sys
import os
module = sys.modules[__name__]
CONFIG = module.CONFIG = {}
TRIPLESTORE_CACHE_URL = os.environ.get('TRIPLESTORE_CACHE_URL')
if TRIPLESTORE_CACHE_URL is None:
    TRIPLESTORE_CACHE_URL = CONFIG["TRIPLESTORE_CACHE_URL"] = "http://db.loci.cat"
TRIPLESTORE_CACHE_PORT = CONFIG["TRIPLESTORE_CACHE_PORT"] = "80"
TRIPLESTORE_CACHE_SPARQL_ENDPOINT = CONFIG["TRIPLESTORE_CACHE_SPARQL_ENDPOINT"] = \
    "{}:{}/repositories/loci-cache".format(TRIPLESTORE_CACHE_URL, TRIPLESTORE_CACHE_PORT)

ES_URL = CONFIG["ES_URL"] = "http://elasticsearch"
ES_PORT = CONFIG["ES_ENDPOINT"] = "9200"
ES_ENDPOINT = CONFIG["ES_ENDPOINT"] = \
    "{}:{}/_search".format(ES_URL, ES_PORT)


GEOM_DATA_SVC_ENDPOINT = CONFIG["GEOM_DATA_SVC_ENDPOINT"] = "https://gds.loci.cat"
