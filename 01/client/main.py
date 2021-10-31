import requests
import socket
from flask import Flask, request, jsonify

from Monitor import MonitorThread, get_backend_signature
from config import NODE_PORT, NODES

app = Flask(__name__)
monitor = MonitorThread()

app.secret_key = 'BAD_SECRET_KEY'
app.config["SESSION_COOKIE_PATH"] = '/'


@app.route('/')
def home():
    about_html = '<br>'
    # for i in range(len(NODES)):
    #     try:
    #         about_html += str(requests.post(f'http://{NODES[i]}:{NODE_PORT}/about', timeout=1)) + '<br>'
    #     except requests.exceptions.ConnectionError:
    #         about_html += '???<br>'

    return '<html><head><title>DS01 : kvetont</title></head>' + \
           '<body><h2>DS01 : kvetont</h2>' + \
           get_backend_signature() + '<br>' + \
           about_html + '</body></html>\n'


@app.route('/endpoint', methods=['POST'])
def endpoint():
    # Get the message (JSON)
    input_json = request.get_json(force=True)
    # force=True, above, is necessary if another developer
    # forgot to set the MIME type to 'application/json'
    print('Received data:', input_json, flush=True)

    # Create response
    res = {'status': 0}

    # Call receive node handler
    data = monitor.node.receive(input_json)
    if bool(data):  # if any data response...
        res['data'] = data

    # Return response
    return jsonify(res)
    # return redirect(url_for("hello"))


@app.route('/enable', methods=['POST'])
def enable():
    monitor.node.enable()
    # Create response
    res = {'status': 0}
    # Return response
    return jsonify(res)


@app.route('/disable', methods=['POST'])
def disable():
    monitor.node.disable()
    # Create response
    res = {'status': 0}
    # Return response
    return jsonify(res)


@app.route('/about', methods=['GET', 'POST'])
def about():
    # Return response
    return jsonify(monitor.node.about())


if __name__ == '__main__':
    monitor.start()
    app.run(host="0.0.0.0")
    # app.run(host="127.0.0.1", port=NODE_PORT)

# EOF
