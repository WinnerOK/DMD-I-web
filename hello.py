from flask import Flask
import re
from os import environ

app = Flask(__name__)

pattern = re.compile(r"^postgres:\/\/(?P<user>.+):(?P<password>.+)@(?P<host>.+):(?P<port>\d+)\/(?P<database>.+)$")

@app.route('/')
def hello_world():
    url = environ["DATABASE_URL"]
    _, user, password,  host, port, database, __ = pattern.split(url)
    return f'host: {host}\nport: {port}\ndatabase: {database}\nuser: {user}\npassword: {password}'

if __name__ == '__main__':
    app.run()
