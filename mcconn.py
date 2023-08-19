import json
import os
import subprocess

from pathlib import Path
from mcrcon import MCRcon

wd = os.getcwd()
p = Path(wd)

mcserver = p.parent / 'mcserver'
user_data = mcserver / 'usercache.json'
lp_user_data = mcserver / 'plugins' / 'LuckPerms' / 'json-storage' / 'users'


lp_user = {
            "uuid": "placeholder",
            "name": "placeholder",
            "primaryGroup": "default",
            "parents": [
                    {
                    "group": "default"
                    }
                ],
            "prefixes": [
                    {
                    "prefix": "placeholder",
                    "priority": 20
                    }
                ]
            }


def get_user_uuid(username: str):
    f = open(user_data)
    data = json.load(f)

    for user in data:
        if user['name'] == username:
            return user['uuid']

    raise IndexError


def add_user_prefix(username: str, prefix: str):
    uuid = get_user_uuid(username)
    
    lp_user['uuid'] = uuid
    lp_user['name'] = username
    lp_user['prefixes'][0]['prefix'] = prefix

    with open(lp_user_data / f'{uuid}.json', 'w') as outfile:
        json.dump(lp_user, outfile)


def message_user(username: str, message: str):
    with MCRcon('localhost', str(os.getenv('RCON_PASS'))) as mcr:
        mcr.command(f'msg {username} {message}')
                

def start_server():
    subprocess.call(['screen', '-dmS', 'minecraft', mcserver / 'run.sh'])