import random
import os
from flask import Flask, make_response, jsonify, abort, request
import json
import redis
import logging
import traceback


logging.basicConfig(filename='bot.log',level=logging.DEBUG)

logging.info("New session started!")

r = redis.Redis(host=os.environ['REDIS_SERVICE_HOST'], port=6379, db=0, decode_responses=True)

app = Flask(__name__)


def generate_id(n=10):
    id = ''
    for _ in range(n):
        id += str(random.randint(0, 9))
    return int(id)


@app.route('/')
def index():
    return "This is IK-15 database."


@app.route("/convicts", methods=['GET'])
def get_convicts():
    convicts = dict()
    for id in r.scan_iter():
        convicts[id] = json.loads(str(r.get(id)))
    return jsonify({'convicts': convicts})


@app.route("/convicts/<int:id>", methods=['GET'])
def get_convict(id):
    convict = r.get(id)
    if convict is None:
        abort(404)
    convict = json.loads(str(convict))
    return jsonify({'convict': convict})


@app.route('/convicts', methods=['POST'])
def create_convict():
    if not request.json or not 'name' in request.json or not 'article' in request.json or not 'term' in request.json:
        abort(400)
    id = generate_id()
    while r.get(id) is not None:
        id = generate_id
    convict = {
        'id': id,
        'name': request.json['name'],
        'article': request.json['article'],
        'term': request.json['term'],
        'type': request.json.get('type', ""),
        'released': False
    }
    r.set(id, json.dumps(convict))
    return jsonify({'convict': convict}), 201


@app.route('/convicts/<int:id>', methods=['PUT'])
def update_convict(id):
    convict = r.get(id)
    if convict is None:
        abort(404)
    convict = json.loads(str(convict))
    if not request.json:
        abort(400)
    if 'released' in request.json:
        if type(request.json['released']) is not bool:
            abort(400)
        convict['released'] = request.json.get('released', convict['released'])
        r.set(id, json.dumps(convict))
    if 'type' in request.json:
        if type(request.json['type']) is not str:
            abort(400)
        convict['type'] = request.json.get('type', convict['type'])
        r.set(id, json.dumps(convict))
    return jsonify({'convict': convict})


@app.route('/convicts/<int:id>', methods=['DELETE'])
def delete_convict(id):
    convict = r.get(id)
    if convict is None:
        abort(404)
    r.delete(id)
    return jsonify({'result': True})


# if __name__ == "__main__":
#     app.run()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
