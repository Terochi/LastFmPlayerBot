import asyncio
import hashlib
import os
from time import time

from RequestHelper import get_json_async


def create_signature(token):
    key = os.getenv('LASTFM_API_KEY')
    secret = os.getenv('LASTFM_API_SECRET')
    sig = f"api_key{key}methodauth.getsessiontoken{token}{secret}"
    return hashlib.md5(sig.encode("utf-8")).hexdigest().upper()


async def get_token():
    result = await get_json_async(
        f"http://ws.audioscrobbler.com/2.0/"
        f"?method=auth.gettoken"
        f"&api_key={os.getenv('LASTFM_API_KEY')}"
        f"&format=json")
    if not result: return None
    return result["token"]


async def get_session(token):
    sig = create_signature(token)
    return await get_json_async(
        f"http://ws.audioscrobbler.com/2.0/"
        f"?method=auth.getsession"
        f"&token={token}"
        f"&api_key={os.getenv('LASTFM_API_KEY')}"
        f"&api_sig={sig}"
        f"&format=json")


def get_auth_link(token):
    return f"http://www.last.fm/api/auth/?api_key={os.getenv('LASTFM_API_KEY')}&token={token}"


async def wait_for_session(token, timeout=60):
    end = time() + timeout
    while time() < end:
        await asyncio.sleep(0.25)
        session = await get_session(token)
        if session:
            return session["session"]
    return None
