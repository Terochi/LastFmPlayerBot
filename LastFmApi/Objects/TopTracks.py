class TopTracks:
    def __init__(self, json: dict):
        root = json["toptracks"]
        attr = root["@attr"]

        self.total_pages = int(attr["totalPages"])
        self.page = int(attr["page"])
        self.page_limit = int(attr["perPage"])
        self.total = int(attr["total"])

        self.tracks = [TopTrackInfo(item) for item in root["track"]]


class TopTrackInfo:
    def __init__(self, json: dict):
        self.track = json["name"]
        self.track_url = json["url"]
        self.play_count = int(json["playcount"])
        self.rank = int(json["@attr"]["rank"])
        artist = json["artist"]
        self.artist = artist["name"]
        self.artist_url = artist["url"]
