from flask import Flask, render_template, send_from_directory, request
import utils

app = Flask(__name__)

@app.route('/static/<path:path>')
def senc_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    id = request.args.get('id')
    if id:
        return render_template('index.html', data=id)
    else:
        return render_template('index.html', data=1)


@app.route('/cred/postgres')
def postgres_cred():
    return utils.get_pg_credentials()


if __name__ == '__main__':
    app.run()
