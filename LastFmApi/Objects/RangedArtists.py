class RangedArtists:
    def __init__(self, json: dict):
        self.artists = [RangedArtistInfo(item) for item in json["weeklyartistchart"]["artist"]]


class RangedArtistInfo:
    def __init__(self, json: dict):
        self.artist = json["name"]
        self.artist_url = json["url"]
