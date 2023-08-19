import json
import os

from pathlib import Path
from mcrcon import MCRcon

wd = os.getcwd()
p = Path(wd)

user_data = p.parent / 'mcserver' / 'usercache.json'
lp_user_data = user_data.parent / 'plugins' / 'LuckPerms' / 'json-storage' / 'users'


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


def message_user(username: str, key: str):
    with MCRcon('localhost', str(os.getenv('RCON_PASS'))) as mcr:
        mcr.command(f'msg {username} Your discord verifcation code is {key}.')
                
