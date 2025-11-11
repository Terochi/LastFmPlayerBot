from os import getenv

from LastFmApi.Period import Period
from RequestHelper import *


async def last_fm_user(method: str, username: str, period: Period, limit: int, page: int):
    return await get_json_async(
        f"http://ws.audioscrobbler.com/2.0/"
        f"?method=user.get{method}"
        f"&user={username}"
        f"&api_key={getenv('LASTFM_API_KEY')}"
        f"&period={period.value}"
        f"&limit={limit}"
        f"&page={page}"
        f"&format=json")


async def last_fm_user_ranged(method: str, username: str, start: int | None, end: int | None):
    return await get_json_async(
        f"http://ws.audioscrobbler.com/2.0/"
        f"?method=user.getweekly{method}chart"
        f"&user={username}" +
        (f"&from={start}" if start else "") +
        (f"&to={end}" if end else "") +
        f"&api_key={getenv('LASTFM_API_KEY')}"
        f"&format=json")


async def last_fm_user_info(username: str):
    return await get_json_async(
        f"http://ws.audioscrobbler.com/2.0/"
        f"?method=user.getinfo"
        f"&user={username}"
        f"&api_key={getenv('LASTFM_API_KEY')}"
        f"&format=json")


async def last_fm_track_info(username: str, track: str, artist: str):
    return await get_json_async(
        f"http://ws.audioscrobbler.com/2.0/"
        f"?method=track.getinfo"
        f"&track={track}"
        f"&artist={artist}"
        f"&username={username}"
        f"&autocorrect=1"
        f"&api_key={getenv('LASTFM_API_KEY')}"
        f"&format=json")
