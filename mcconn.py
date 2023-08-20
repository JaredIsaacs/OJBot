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
    with MCRcon('localhost', str(os.getenv('RCON_PASS'))) as mcr:
        mcr.command(f'lp user {username} meta removeprefix 20')
        mcr.command(f'lp user {username} meta addprefix 20 {prefix}')


def message_user(username: str, message: str):
    with MCRcon('localhost', str(os.getenv('RCON_PASS'))) as mcr:
        mcr.command(f'msg {username} {message}')
                


def get_admins():
    with MCRcon('localhost', str(os.getenv('RCON_PASS'))) as mcr:
        admins = mcr.command(f'lp groups admin listmembers')


def start_server():
    os.system('./run.sh') 

get_admins()