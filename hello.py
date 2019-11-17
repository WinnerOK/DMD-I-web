from flask import Flask, render_template
import utils

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', name="HFDSGSDKLFHHJK")


@app.route('/cred/postgres')
def postgres_cred():
    return utils.get_pg_credentials()


if __name__ == '__main__':
    app.run()
