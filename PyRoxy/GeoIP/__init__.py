from pathlib import Path as _path
from maxminddb import open_database as _open

__dir__ = _path(__file__).parent

_reader = _open(__dir__ / 'Sqlite/GeoLite2-Country.mmdb')

def get(ip: str):
    return _reader.get(ip)


def get_with_prefix_len(ip: str):
    return _reader.get_with_prefix_len(ip)
