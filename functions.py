# -*- coding: utf-8 -*-
#
from decimal import Decimal
from aiohttp import ClientSession
from config import TRIPLESTORE_CACHE_SPARQL_ENDPOINT
from json import loads

from errors import ReportableAPIError


async def query_graphdb_endpoint(sparql, infer=True, same_as=True, limit=1000, offset=0):
    session = query_graphdb_endpoint.session
    if not session:
        query_graphdb_endpoint.session = session = ClientSession()
    args = {
        'query': sparql,
        'infer': 'true' if bool(infer) else 'false',
        'sameAs': 'true' if bool(same_as) else 'false',
        'limit': int(limit),
        'offset': int(offset),
    }
    headers = {
        'Accept': "application/sparql-results+json,*/*;q=0.9",
        'Accept-Encoding': "gzip, deflate",
    }
    resp = await session.request('POST', TRIPLESTORE_CACHE_SPARQL_ENDPOINT, data=args, headers=headers)
    resp_content = await resp.text()
    return loads(resp_content)
query_graphdb_endpoint.session = None


async def get_resource(resource_uri):
    """
    :param resource_uri:
    :type resource_uri: str
    :return:
    """
    sparql = """\
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?p ?o ?p1 ?o1 ?p2 ?o2
WHERE {
    {
        ?s rdf:subject <URI> ;
           rdf:predicate ?p;
           rdf:object ?o .
        OPTIONAL { FILTER (isBlank(?o))
            {
                ?s2 rdf:subject ?o ;
                rdf:predicate ?p;
                rdf:object ?o1 .
            }
            UNION
            { ?o ?p1 ?o1 . }
            OPTIONAL { FILTER (isBlank(?o1))
                ?o1 ?p2 ?o2 .
            }
        }
    }
    UNION
    {
        <URI> ?p ?o .
        OPTIONAL { FILTER (isBlank(?o))
            {
                ?s3 rdf:subject ?o ;
                rdf:predicate ?p;
                rdf:object ?o1 .
            }
            UNION
            { ?o ?p1 ?o1 . }
            OPTIONAL { FILTER (isBlank(?o1))
                ?o1 ?p2 ?o2 .
            }
        }
    }
}
"""
    sparql = sparql.replace("<URI>", "<{}>".format(str(resource_uri)))
    resp = await query_graphdb_endpoint(sparql)
    resp_object = {}
    if 'results' not in resp:
        return resp_object
    bindings = resp['results']['bindings']
    for b in bindings:
        pred = b['p']['value']
        obj = b['o']
        if obj['type'] == "bnode":
            try:
                obj = resp_object[pred]
            except KeyError:
                resp_object[pred] = obj = {}
            pred1 = b['p1']['value']
            obj1 = b['o1']
            if obj1['type'] == "bnode":
                try:
                    obj1 = obj[pred1]
                except KeyError:
                    obj[pred1] = obj1 = {}
                pred2 = b['p2']['value']
                obj2 = b['o2']['value']
                obj1[pred2] = obj2
            else:
                obj1 = obj1['value']
            obj[pred1] = obj1
        else:
            obj = obj['value']
        resp_object[pred] = obj
    return resp_object


async def get_linksets(count=1000, offset=0):
    """
    :param count:
    :type count: int
    :param offset:
    :type offset: int
    :return:
    """
    sparql = """\
PREFIX loci: <http://linked.data.gov.au/def/loci#>
SELECT ?l
WHERE {
    ?l a loci:Linkset .
}
"""
    resp = await query_graphdb_endpoint(sparql, limit=count, offset=offset)
    linksets = []
    if 'results' not in resp:
        return linksets
    bindings = resp['results']['bindings']
    for b in bindings:
        linksets.append(b['l']['value'])
    meta = {
        'count': len(linksets),
        'offset': offset,
    }
    return meta, linksets

async def get_datasets(count=1000, offset=0):
    """
    :param count:
    :type count: int
    :param offset:
    :type offset: int
    :return:
    """
    sparql = """\
PREFIX dcat: <http://www.w3.org/ns/dcat#>
SELECT ?d
WHERE {
    ?d a dcat:Dataset .
}
"""
    resp = await query_graphdb_endpoint(sparql, limit=count, offset=offset)
    datasets = []
    if 'results' not in resp:
        return datasets
    bindings = resp['results']['bindings']
    for b in bindings:
        datasets.append(b['d']['value'])
    meta = {
        'count': len(datasets),
        'offset': offset,
    }
    return meta, datasets

async def get_locations(count=1000, offset=0):
    """
    :param count:
    :type count: int
    :param offset:
    :type offset: int
    :return:
    """
    sparql = """\
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT DISTINCT ?l
WHERE {
    { ?l a geo:Feature }
    UNION
    { ?l a prov:Location } .
}
"""
    resp = await query_graphdb_endpoint(sparql, limit=count, offset=offset)
    locations = []
    if 'results' not in resp:
        return locations
    bindings = resp['results']['bindings']
    for b in bindings:
        locations.append(b['l']['value'])
    meta = {
        'count': len(locations),
        'offset': offset,
    }
    return meta, locations


async def get_location_is_within(target_uri, count=1000, offset=0):
    """
    :param target_uri:
    :type target_uri: str
    :param count:
    :type count: int
    :param offset:
    :type offset: int
    :return:
    """
    sparql = """\
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?l
WHERE {
    {
        ?s rdf:subject <URI> ;
           rdf:predicate geo:sfWithin ;
           rdf:object ?l  .
    }
    UNION
    { <URI> geo:sfWithin ?l }
}
"""
    sparql = sparql.replace("<URI>", "<{}>".format(str(target_uri)))
    resp = await query_graphdb_endpoint(sparql, limit=count, offset=offset)
    locations = []
    if 'results' not in resp:
        return locations
    bindings = resp['results']['bindings']
    for b in bindings:
        locations.append(b['l']['value'])
    meta = {
        'count': len(locations),
        'offset': offset,
    }
    return meta, locations

async def get_location_contains(target_uri, count=1000, offset=0):
    """
    :param target_uri:
    :type target_uri: str
    :param count:
    :type count: int
    :param offset:
    :type offset: int
    :return:
    """
    sparql = """\
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?l
WHERE {
    {
        ?s rdf:subject <URI> ;
           rdf:predicate geo:sfContains;
           rdf:object ?l  .
    }
    UNION
    { <URI> geo:sfContains ?l }
}
"""
    sparql = sparql.replace("<URI>", "<{}>".format(str(target_uri)))
    resp = await query_graphdb_endpoint(sparql, limit=count, offset=offset)
    locations = []
    if 'results' not in resp:
        return locations
    bindings = resp['results']['bindings']
    for b in bindings:
        locations.append(b['l']['value'])
    meta = {
        'count': len(locations),
        'offset': offset,
    }
    return meta, locations

async def get_location_overlaps(target_uri, include_areas, include_proportion, include_within, include_contains, count=1000, offset=0):
    """
    :param target_uri:
    :type target_uri: str
    :type include_areas: bool
    :type include_proportion: bool
    :type include_within: bool
    :type include_contains: bool
    :param count:
    :type count: int
    :param offset:
    :type offset: int
    :return:
    """
    overlaps_sparql = """\
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX geox: <http://linked.data.gov.au/def/geox#>
PREFIX qb4st: <http://www.w3.org/ns/qb4st/>
PREFIX epsg: <http://www.opengis.net/def/crs/EPSG/0/>
PREFIX dt: <http://linked.data.gov.au/def/datatype/>
SELECT <SELECTS>
WHERE {
    {
        {
           ?s1 rdf:subject <URI> ;
           rdf:predicate geox:transitiveSfOverlap;
           rdf:object ?o  .
        } UNION {
           ?s2 rdf:subject <URI> ;
           rdf:predicate geo:sfOverlaps;
           rdf:object ?o  .
        }
    }
    UNION
    { <URI> geox:transitiveSfOverlap ?o }
    UNION
    { <URI> geo:sfOverlaps ?o }
    <EXTRAS>
}
GROUP BY ?o
"""
    contains_sparql = """\
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX geox: <http://linked.data.gov.au/def/geox#>
    PREFIX qb4st: <http://www.w3.org/ns/qb4st/>
    PREFIX epsg: <http://www.opengis.net/def/crs/EPSG/0/>
    PREFIX dt: <http://linked.data.gov.au/def/datatype/>
    SELECT ?c <SELECTS>
    WHERE {
        {  
            ?s2 rdf:subject <URI> ;
            rdf:predicate geo:sfContains;
            rdf:object ?o  .
        }
        UNION
        { <URI> geo:sfContains+ ?o }
        OPTIONAL { FILTER(bound(?o))
            BIND(true as ?c) .
        }
        <EXTRAS>
    }
    GROUP BY ?c ?o
    """
    within_sparql = """\
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX geox: <http://linked.data.gov.au/def/geox#>
    PREFIX qb4st: <http://www.w3.org/ns/qb4st/>
    PREFIX epsg: <http://www.opengis.net/def/crs/EPSG/0/>
    PREFIX dt: <http://linked.data.gov.au/def/datatype/>
    SELECT ?w <SELECTS>
    WHERE {
        {  
            ?s2 rdf:subject <URI> ;
            rdf:predicate geo:sfWithin;
            rdf:object ?o  .
        }
        UNION
        { <URI> geo:sfWithin+ ?o }
        OPTIONAL { FILTER(bound(?o))
            BIND(true as ?w) .
        }
        <EXTRAS>
    }
    GROUP BY ?w ?o
    """
    use_areas_sparql = include_proportion or include_areas
    use_proportion_sparql = include_proportion

    selects = "?o "
    area_selects = "(MAX(?a1) as ?uarea) (MAX(?a2) as ?oarea) "
    iarea_selects = "(MAX(?a3) as ?iarea) "

    areas_sparql = """\
    OPTIONAL {
        <URI> geox:hasAreaM2 ?ha1 .
        ?ha1 qb4st:crs epsg:3577 .
        ?ha1 dt:value ?a1 .
    }
    OPTIONAL {
        ?o geox:hasAreaM2 ?ha2 .
        ?ha2 qb4st:crs epsg:3577 .
        ?ha2 dt:value ?a2 .
    }
    """
    iarea_sparql = """\
    OPTIONAL {
        { <URI> geo:sfContains ?i }
        UNION 
        {
            ?s3 rdf:subject <URI> ;
                rdf:predicate geo:sfContains ;
                rdf:object ?i 
        } .
        
        { ?o geo:sfContains ?i }
        UNION 
        {
            ?s4 rdf:subject ?o ;
                rdf:predicate geo:sfContains ;
                rdf:object ?i 
        } .
        OPTIONAL {
            ?i geox:hasAreaM2 ?ha3 .
            ?ha3 qb4st:crs epsg:3577 .
            ?ha3 dt:value ?a3 .
        }
    }
    """
    extras = ""
    use_selects = selects
    if use_areas_sparql:
        extras += areas_sparql
        use_selects += area_selects
    if use_proportion_sparql:
        extras += iarea_sparql
        use_selects += iarea_selects
    sparql = overlaps_sparql.replace("<SELECTS>", use_selects)
    sparql = sparql.replace("<EXTRAS>", extras)
    sparql = sparql.replace("<URI>", "<{}>".format(str(target_uri)))
    resp = await query_graphdb_endpoint(sparql, limit=count, offset=offset)
    overlaps = []
    if 'results' not in resp:
        return {'count', 0}, overlaps
    bindings = resp['results']['bindings']
    extras = ""
    if include_contains:
        use_selects = selects
        if include_areas:
            extras = areas_sparql
            use_selects += area_selects
        sparql = contains_sparql.replace("<SELECTS>", use_selects)
        sparql = sparql.replace("<EXTRAS>", extras)
        sparql = sparql.replace("<URI>", "<{}>".format(str(target_uri)))
        resp = await query_graphdb_endpoint(sparql, limit=count, offset=offset)
        if 'results' not in resp:
            return {'count', 0}, overlaps
        bindings.extend(resp['results']['bindings'])
        extras = ""
    if include_within:
        use_selects = selects
        if include_areas:
            extras = areas_sparql
            use_selects += area_selects
        sparql = within_sparql.replace("<SELECTS>", selects)
        sparql = sparql.replace("<EXTRAS>", extras)
        sparql = sparql.replace("<URI>", "<{}>".format(str(target_uri)))
        resp = await query_graphdb_endpoint(sparql, limit=count, offset=offset)
        if 'results' not in resp:
            return {'count', 0}, overlaps
        bindings.extend(resp['results']['bindings'])
    if len(bindings) < 1:
        return {'count', 0}, overlaps
    if not include_proportion and not include_areas:
        my_area = False
        for b in bindings:
            overlaps.append(b['o']['value'])
    else:
        d100 = Decimal(100.0)
        try:
            uarea = bindings[0]['uarea']
        except (LookupError, AttributeError):
            raise ReportableAPIError("Source feature does not have a known geometry area."
                                     "Cannot return areas or calculate proportions.")
        my_area = round(Decimal(uarea['value']), 8)
        for b in bindings:
            o_dict = {"uri": b['o']['value']}
            if include_within:
                try:
                    is_w = b['w']
                except (LookupError, AttributeError):
                    is_w = False
                o_dict["isWithin"] = bool(is_w)
            if include_contains:
                try:
                    has_c = b['c']
                except (LookupError, AttributeError):
                    has_c = False
                o_dict["contains"] = bool(has_c)

            overlaps.append(o_dict)
            try:
                oarea = bindings[0]['oarea']
            except (LookupError, AttributeError):
                continue
            o_area = round(Decimal(oarea['value']), 8)
            if include_areas:
                o_dict['featureArea'] = str(o_area)
            if include_proportion:
                try:
                    i_area = round(Decimal(b['iarea']['value']), 8)
                except (LookupError, AttributeError):
                    continue

                if include_areas:
                    o_dict['intersectionArea'] = str(i_area)
                my_proportion = round((i_area / my_area) * d100, 8)
                other_proportion = round((i_area / o_area) * d100, 8)
                o_dict['forwardProportion'] = str(my_proportion)
                o_dict['reverseProportion'] = str(other_proportion)

    meta = {
        'count': len(overlaps),
        'offset': offset,
    }
    if my_area and include_areas:
        meta['featureArea'] = str(my_area)
    return meta, overlaps
