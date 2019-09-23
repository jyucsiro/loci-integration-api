import pytest
import json
from app import create_app

data = []
with open('./loci-testdata/test_case_withins_result.json') as json_file:
    json_data = json.load(json_file)

data = [{ akey: json_data[akey]} for akey in json_data.keys()]

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
async def test_within(test_cli, get_data):
    for aUri in get_data.keys():
        resp = await test_cli.get('/api/v1/linksets'.format(aUri))
        assert resp.status == 200
