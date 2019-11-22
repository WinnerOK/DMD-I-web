from flask import Flask, render_template, send_from_directory, request
import queries
from utils import get_pg_credentials
app = Flask(__name__)

@app.route('/static/<path:path>')
def senc_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    id = request.args.get('id')
    if (id and int(id) == 1) or not id:
        data, head = queries.execute_query(1)
        return render_template('index.html', data=data, head=head)
    elif (id):
        data, head = queries.execute_query(int(id))
        return render_template('index.html', data=data, head=head)


@app.route('/cred/postgres')
def postgres_cred():
    return get_pg_credentials()

@app.route('/custom', methods=['POST'])
def custom_query():
    query = request.get_json()['query']
    data, head = queries.custom_query(query)
    return render_template('index.html', data=data, head=head)


if __name__ == '__main__':
    app.run()
