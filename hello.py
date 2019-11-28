from flask import Flask, render_template, send_from_directory, request, send_file
import fastjsonschema
import queries
import populating
from utils import get_pg_credentials

from os import listdir
from os.path import join
from json import load

SCHEMAS_FOLDER = 'schemas'
schemas = {}
for schema_file in listdir(SCHEMAS_FOLDER):
    with open(join(SCHEMAS_FOLDER, schema_file), 'r') as json:
        schemas[schema_file[:-5]] = fastjsonschema.compile(load(json))

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

@app.route('/generate')
def gen():
    return render_template('generate.html')


@app.route('/cred/postgres')
def postgres_cred():
    return get_pg_credentials()


@app.route('/populate', methods=['POST'])
def populate():
    data = request.get_json()
    try:
        schemas['populate'](data)
    except fastjsonschema.JsonSchemaException as e:
        return f"Incorrect body. Details:\n{e.message}"
    populating.main(**data)
    return "/download"


@app.route('/download')
def download():
    return send_file('populating/queries.sql', mimetype='plain/text', as_attachment=True, attachment_filename='queries.sql')


@app.route('/custom', methods=['POST'])
def custom_query():
    query = request.get_json()['query']
    data, head = queries.custom_query(query)
    return render_template('index.html', data=data, head=head)


if __name__ == '__main__':
    app.run()
