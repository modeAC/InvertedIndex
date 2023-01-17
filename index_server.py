import copy

import jsonpickle
from flask import Flask, request, Response

from index import Index

app = Flask(__name__)

thread_no = 5
index = Index()


@app.route('/api/add_files', methods=['POST'])
def add_files():
    r = request
    data = jsonpickle.decode(r.data)
    path = data['path']
    var = data['var'] if data['var'] != '/' else None

    ret = index.add(path, th_no=thread_no, var=var)

    response = {'files': ret}
    status = 200
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=status, mimetype="application/json")


@app.route('/api/search', methods=['GET'])
def search():
    r = request
    data = jsonpickle.decode(r.data)
    words = data['words']

    _aux = {}
    ret = {}

    for w in words:
        for s_res in index.search(w):
            if not w in _aux:
                _aux[w] = set()
            _aux[w].add(s_res[0])
            if not s_res[0] in ret:
                ret[s_res[0]] = list()
            ret[s_res[0]].append(s_res[1])

    _aux = set.intersection(*list(_aux.values()))

    for k, v in copy.copy(ret).items():
        if k not in _aux:
            ret.pop(k)

    response = {'results': ret}
    status = 200
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=status, mimetype="application/json")


@app.route('/api/clear', methods=['POST'])
def clear():
    index.reset()
    response = {}
    status = 200
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=status, mimetype="application/json")


port = 5000
app.run(host="0.0.0.0", port=port)
