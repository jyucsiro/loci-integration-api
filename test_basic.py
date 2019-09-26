import pytest
import json
import logging
logging.basicConfig(level=logging.DEBUG)
from app import create_app


data = []
with open('./loci-testdata/test_case_contains_result.json') as json_file:
    json_data = json.load(json_file)

data = [{ "uri": aData[1], "test_data": aData[2], "test_name": aData[0]} for aData in json_data]

@pytest.yield_fixture
def app():
    yield create_app()

@pytest.fixture
def test_cli(loop, sanic_client, app):
    return loop.run_until_complete(sanic_client(app))

async def test_index(test_cli):
    resp = await test_cli.get('/')
    assert resp.status == 200

@pytest.mark.parametrize("get_data", data)
async def test_overlaps_within(test_cli, get_data):
    aUri = get_data["uri"]
    test_name = get_data["test_name"]
    logging.debug("Test Name {}".format(test_name))
    resp = await test_cli.get('/api/v1/location/overlaps?uri={}&areas=false&proportion=true&contains=true&within=false&count=1000000&offset=0'.format(aUri))
    result_dict = await resp.json()
    results_uris = { aResult["uri"]: aResult for aResult in result_dict["overlaps"] } 
    for expected_result in get_data["test_data"]:
        if not expected_result["toAreaDataset"] is None:
            to_area = expected_result["toAreaDataset"]
            result_uri = expected_result["to"]
        else:
            to_area = expected_result["toAreaLinkset"]
            result_uri = expected_result["toParent"]
        result_proportion = (float(to_area) / float(expected_result["fromAreaDataset"])) * 100
        logging.debug("From Uri {}".format(expected_result["from"]))
        logging.debug("To Uri {}".format(result_uri))
        logging.debug("Expected Proportion {}".format(result_proportion))
        assert result_uri in results_uris.keys()
        logging.debug(results_uris[result_uri])
        if "forwardProportion" in results_uris[result_uri].keys(): 
            returned_proportion = float(results_uris[result_uri]["forwardProportion"])
            logging.debug("Returned Proportion {}".format(returned_proportion))
            assert  returned_proportion == pytest.approx(result_proportion, 0.001)
    assert resp.status == 200
