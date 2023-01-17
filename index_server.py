import threading

import jsonpickle
from flask import Flask, request, Response

from index import Index

app = Flask(__name__)
sem = threading.Semaphore()

thread_no = 5
index = Index()


@app.route('/api/add_files', methods=['POST'])
def add_files():
    r = request
    data = jsonpickle.decode(r.data)
    path = data['path']
    var = data['var'] if data['var'] != '/' else None

    sem.acquire()
    ret = index.add(path, th_no=thread_no, var=var)
    sem.release()

    response = {'files': ret}
    status = 200
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=status, mimetype="application/json")


@app.route('/api/search', methods=['GET'])
def search():
    r = request
    data = jsonpickle.decode(r.data)
    word = data['words'][0]

    ret = index.search(word)

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
