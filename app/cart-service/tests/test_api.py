
import json
from app import app
import pytest

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as c:
        yield c

def test_crud_flow(client):
    # create
    rv = client.post("/items", json={"name":"item1"})
    assert rv.status_code == 201
    j = rv.get_json()
    assert j["name"] == "item1"
    item_id = j["id"]

    # read
    rv = client.get(f"/items/{item_id}")
    assert rv.status_code == 200

    # update
    rv = client.put(f"/items/{item_id}", json={"name":"updated"})
    assert rv.status_code == 200
    assert rv.get_json()["name"] == "updated"

    # delete
    rv = client.delete(f"/items/{item_id}")
    assert rv.status_code == 204
