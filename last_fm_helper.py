from os import getenv
from bs4 import BeautifulSoup
from enum import Enum

from request_helper import *

class UserInfo:
    def __init__(self, json: dict):
        user = json["user"]

        self.play_count = int(user["playcount"])
        self.artist_count = int(user["artist_count"])
        self.track_count = int(user["track_count"])
        self.album_count = int(user["album_count"])
        self.playlist_count = int(user["playlists"])

class TrackInfo:
    def __init__(self, json: dict):
        track = json["track"]
        artist = track["artist"]

        self.track = track["name"]
        self.track_url = track["url"]
        self.artist = artist["name"]
        self.artist_url = artist["url"]
        self.listeners = int(track["listeners"])
        self.play_count = int(track["playcount"])
        self.user_play_count = int(track["userplaycount"])

class ItemInfo:
    def __init__(self, json: dict):
        self.name = json["name"]
        self.url = json["url"]
        play_count = json.get("playcount")
        if play_count:
            self.play_count = int(play_count)
            self.rank = int(json["@attr"]["rank"])

        artist = json.get("artist")
        if artist:
            text = artist.get("#text")
            if text:
                self.artist = text
            else:
                self.artist = artist["name"]
                self.artist_url = artist["url"]

class RangedInfo:
    def __init__(self, json: dict, name: str):
        root = json[f"weekly{name}chart"]
        inner = root[name]
        self.list = [ItemInfo(item) for item in inner]

class TotalInfo:
    def __init__(self, json: dict, root_name: str, inner_name: str):
        root = json[root_name]
        inner = root[inner_name]
        attr = root["@attr"]

        self.total_pages = int(attr["totalPages"])
        self.page = int(attr["page"])
        self.page_limit = int(attr["perPage"])
        self.total = int(attr["total"])

        self.list = [ItemInfo(item) for item in inner]

class Period(Enum):
    ALLTIME = "overall"
    WEEK = "7day"
    MONTH = "1month"
    MONTHS3 = "3month"
    MONTHS6 = "6month"
    YEAR = "12month"

async def last_fm_user(method: str, username: str, period: Period = Period.ALLTIME, limit: int = 50, page: int = 1):
    result = await get_json_async(
        f"http://ws.audioscrobbler.com/2.0/"
        f"?method=user.get{method}"
        f"&user={username}"
        f"&api_key={getenv('LASTFM_API_KEY')}"
        f"&period={period.value}"
        f"&limit={limit}"
        f"&page={page}"
        f"&format=json")

    if not result: return None
    inner_name = method[3:-1] if method[0:3] == "top" else method[5:-1]
    return TotalInfo(result, method, inner_name)

async def last_fm_user_ranged(method: str, username: str, start: int = None, end: int = None):
    result = await get_json_async(
        f"http://ws.audioscrobbler.com/2.0/"
        f"?method=user.getweekly{method}chart"
        f"&user={username}" +
        (f"&from={start}" if start else "") +
        (f"&to={end}" if end else "") +
        f"&api_key={getenv('LASTFM_API_KEY')}"
        f"&format=json")

    if not result: return None
    return RangedInfo(result, method)

async def last_fm_user_info(username: str):
    result = await get_json_async(
        f"http://ws.audioscrobbler.com/2.0/"
        f"?method=user.getinfo"
        f"&user={username}"
        f"&api_key={getenv('LASTFM_API_KEY')}"
        f"&format=json")

    if not result: return None
    return UserInfo(result)

async def last_fm_track_info(username: str, track: str, artist: str):
    result = await get_json_async(
        f"http://ws.audioscrobbler.com/2.0/"
        f"?method=track.getinfo"
        f"&track={track}"
        f"&artist={artist}"
        f"&username={username}"
        f"&autocorrect=1"
        f"&api_key={getenv('LASTFM_API_KEY')}"
        f"&format=json")

    if not result: return None
    return TrackInfo(result)

async def get_youtube_ids(url):
    text = await get_text_async(url)
    soup = BeautifulSoup(text, 'html.parser')
    youtube_ids = set()
    for a_tag in soup.find_all('a', attrs={'data-youtube-id': True}):
        youtube_id = a_tag['data-youtube-id']
        youtube_ids.add(youtube_id)
    return youtube_ids
