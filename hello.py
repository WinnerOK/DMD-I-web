from flask import Flask, render_template, send_from_directory
import utils

app = Flask(__name__)

@app.route('/css/<path:path>')
def send_js(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    return render_template('index.html', name="HFDSGSDKLFHHJK")


@app.route('/cred/postgres')
def postgres_cred():
    return utils.get_pg_credentials()


if __name__ == '__main__':
    app.run()
