class LovedTracks:
    def __init__(self, json: dict):
        root = json["lovedtracks"]
        attr = root["@attr"]

        self.total_pages = int(attr["totalPages"])
        self.page = int(attr["page"])
        self.page_limit = int(attr["perPage"])
        self.total = int(attr["total"])

        self.tracks = [LovedTrackInfo(item) for item in root["track"]]


class LovedTrackInfo:
    def __init__(self, json: dict):
        self.track = json["name"]
        self.track_url = json["url"]
        artist = json["artist"]
        self.artist = artist["name"]
        self.artist_url = artist["url"]
