
from flask import Flask, jsonify, request, abort
app = Flask(__name__)

_store = {}
_next_id = 1

@app.route("/health")
def health():
    return jsonify(status="ok", service="users-service")

@app.route("/items", methods=["GET"])
def list_items():
    return jsonify(list(_store.values()))

@app.route("/items", methods=["POST"])
def create_item():
    global _next_id
    data = request.get_json() or {}
    if not data.get("name"):
        abort(400, "name required")
    item = { "id": _next_id, "name": data.get("name"), "meta": data.get("meta", {}) }
    _store[_next_id] = item
    _next_id += 1
    return jsonify(item), 201

@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = _store.get(item_id)
    if not item:
        abort(404)
    return jsonify(item)

@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json() or {}
    item = _store.get(item_id)
    if not item:
        abort(404)
    # only allow updating name and meta
    for key in ("name","meta"):
        if key in data:
            item[key] = data[key]
    return jsonify(item)

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    if item_id in _store:
        del _store[item_id]
        return "", 204
    abort(404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
