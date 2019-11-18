from flask import Flask, render_template, send_from_directory, request
from queries import exe_first_query
from utils import get_pg_credentials
app = Flask(__name__)

@app.route('/static/<path:path>')
def senc_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    id = request.args.get('id')
    data, head = exe_first_query()
    if id:
        return render_template('index.html', data=data, head=head)
    else:
        return render_template('index.html', data=data, head=head)


@app.route('/cred/postgres')
def postgres_cred():
    return get_pg_credentials()


if __name__ == '__main__':
    app.run()
