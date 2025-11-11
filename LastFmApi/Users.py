import json
import os

FILE_NAME = 'last_fm_users.json'
last_fm_users = {}


def save_last_fm_users():
    global last_fm_users
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(last_fm_users, f, ensure_ascii=False, separators=(',', ':'))


def load_last_fm_users():
    global last_fm_users
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            last_fm_users = json.load(f)
    else:
        last_fm_users = {}


load_last_fm_users()
