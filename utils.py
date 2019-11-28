import re
from os import environ
from typing import Tuple

from psycopg2 import connect
from psycopg2.extensions import connection, cursor

POSTGRES_PATTERN = re.compile(
    r"^postgres:\/\/(?P<user>.+):(?P<password>.+)@(?P<host>.+):(?P<port>\d+)\/(?P<database>.+)$")

MYSQL_PATTERN = re.compile(
    r"^mysql:\/\/(?P<user>.+):(?P<password>.+)@(?P<host>.+):(?P<port>\d+)\/(?P<database>.+)$"
)

def get_pg_credentials() -> str:
    url = environ["DATABASE_URL"]
    _, user, password, host, port, database, __ = POSTGRES_PATTERN.split(url)
    return f'host: {host}<br>port: {port}<br>dbname: {database}<br>user: {user}<br>password: {password}'

def get_connection() -> Tuple[connection, cursor]:
    credentials = dict(item.split(":") for item in get_pg_credentials().split('<br>'))
    conn = connect(' '.join(map(lambda item: '='.join(item), credentials.items())))
    cur = conn.cursor()
    return conn, cur
