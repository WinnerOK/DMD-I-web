from flask import Flask, render_template
import re
from os import environ

app = Flask(__name__)

pattern = re.compile(r"^postgres:\/\/(?P<user>.+):(?P<password>.+)@(?P<host>.+):(?P<port>\d+)\/(?P<database>.+)$")


@app.route('/')
def index():
    return render_template('index.html', name="HFDSGSDKLFHHJK")


@app.route('/cred/postgres')
def postgres_cred():
    url = environ["DATABASE_URL"]
    _, user, password, host, port, database, __ = pattern.split(url)
    return f'host: {host}<br>port: {port}<br>dbname: {database}<br>user: {user}<br>password: {password}'


if __name__ == '__main__':
    app.run()
