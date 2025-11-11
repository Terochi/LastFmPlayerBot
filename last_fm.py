from last_fm_helper import *

async def get_loved_tracks(username: str, period: Period = Period.ALLTIME, limit: int = 50, page: int = 1):
    return await last_fm_user("lovedtracks", username, period, limit, page)

async def get_top_tracks(username: str, period: Period = Period.ALLTIME, limit: int = 50, page: int = 1):
    return await last_fm_user("toptracks", username, period, limit, page)

async def get_top_albums(username: str, period: Period = Period.ALLTIME, limit: int = 50, page: int = 1):
    return await last_fm_user("topalbums", username, period, limit, page)

async def get_top_artists(username: str, period: Period = Period.ALLTIME, limit: int = 50, page: int = 1):
    return await last_fm_user("topartists", username, period, limit, page)


async def get_tracks_range(username: str, start: int = None, end: int = None):
    return await last_fm_user_ranged("track", username, start, end)

async def get_artists_range(username: str, start: int = None, end: int = None):
    return await last_fm_user_ranged("artist", username, start, end)

async def get_albums_range(username: str, start: int = None, end: int = None):
    return await last_fm_user_ranged("album", username, start, end)


async def get_track_info(username: str, track: str, artist: str):
    return await last_fm_track_info(username, track, artist)

async def get_user_info(username: str):
    return await last_fm_user_info(username)