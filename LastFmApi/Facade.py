from LastFmApi.Helper import *
from LastFmApi.Period import Period


async def get_loved_tracks(username: str, period: Period = Period.ALLTIME, limit: int = 50, page: int = 1):
    result = await last_fm_user("lovedtracks", username, period, limit, page)
    if not result: return None
    from LastFmApi.Objects.LovedTracks import LovedTracks
    return LovedTracks(result)


async def get_top_tracks(username: str, period: Period = Period.ALLTIME, limit: int = 50, page: int = 1):
    result = await last_fm_user("toptracks", username, period, limit, page)
    if not result: return None
    from LastFmApi.Objects.TopTracks import TopTracks
    return TopTracks(result)


async def get_top_albums(username: str, period: Period = Period.ALLTIME, limit: int = 50, page: int = 1):
    result = await last_fm_user("topalbums", username, period, limit, page)
    if not result: return None
    from LastFmApi.Objects.TopAlbums import TopAlbums
    return TopAlbums(result)


async def get_top_artists(username: str, period: Period = Period.ALLTIME, limit: int = 50, page: int = 1):
    result = await last_fm_user("topartists", username, period, limit, page)
    if not result: return None
    from LastFmApi.Objects.TopArtists import TopArtists
    return TopArtists(result)


async def get_ranged_tracks(username: str, start: int = None, end: int = None):
    result = await last_fm_user_ranged("track", username, start, end)
    if not result: return None
    from LastFmApi.Objects.RangedTracks import RangedTracks
    return RangedTracks(result)


async def get_ranged_artists(username: str, start: int = None, end: int = None):
    result = await last_fm_user_ranged("artist", username, start, end)
    if not result: return None
    from LastFmApi.Objects.RangedArtists import RangedArtists
    return RangedArtists(result)


async def get_ranged_albums(username: str, start: int = None, end: int = None):
    result = await last_fm_user_ranged("album", username, start, end)
    if not result: return None
    from LastFmApi.Objects.RangedAlbums import RangedAlbums
    return RangedAlbums(result)


async def get_track_info(username: str, track: str, artist: str):
    result = await last_fm_track_info(username, track, artist)
    if not result: return None
    from LastFmApi.Objects.TrackInfo import TrackInfo
    return TrackInfo(result)


async def get_user_info(username: str):
    result = await last_fm_user_info(username)
    if not result: return None
    from LastFmApi.Objects.UserInfo import UserInfo
    return UserInfo(result)
