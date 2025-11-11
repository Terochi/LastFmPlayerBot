class RangedAlbums:
    def __init__(self, json: dict):
        self.albums = [RangedAlbumInfo(item) for item in json["weeklyalbumchart"]["album"]]


class RangedAlbumInfo:
    def __init__(self, json: dict):
        self.album = json["name"]
        self.album_url = json["url"]
        self.artist = json["artist"]["#text"]
