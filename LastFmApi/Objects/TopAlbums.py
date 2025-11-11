class TopAlbums:
    def __init__(self, json: dict):
        root = json["topalbums"]
        attr = root["@attr"]

        self.total_pages = int(attr["totalPages"])
        self.page = int(attr["page"])
        self.page_limit = int(attr["perPage"])
        self.total = int(attr["total"])

        self.albums = [TopAlbumInfo(item) for item in root["album"]]


class TopAlbumInfo:
    def __init__(self, json: dict):
        self.album = json["name"]
        self.album_url = json["url"]
        self.play_count = int(json["playcount"])
        self.rank = int(json["@attr"]["rank"])
        artist = json["artist"]
        self.artist = artist["name"]
        self.artist_url = artist["url"]
