from flask import Flask, send_file

app = Flask(__name__)


@app.route('/')
def index():
    return send_file('graph.png', mimetype='image/png')


@app.route('/info')
def info():
    with open('graph_info.txt', 'r') as f:
        txt = f.read()
    return txt



if __name__ == '__main__':
    app.run()
