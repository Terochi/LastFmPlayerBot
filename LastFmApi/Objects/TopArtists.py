class TopArtists:
    def __init__(self, json: dict):
        root = json["topartists"]
        attr = root["@attr"]

        self.total_pages = int(attr["totalPages"])
        self.page = int(attr["page"])
        self.page_limit = int(attr["perPage"])
        self.total = int(attr["total"])

        self.loved_tracks = [TopArtistInfo(item) for item in root["artist"]]


class TopArtistInfo:
    def __init__(self, json: dict):
        self.artist = json["name"]
        self.artist_url = json["url"]
        self.play_count = int(json["playcount"])
        self.rank = int(json["@attr"]["rank"])
