class RangedTracks:
    def __init__(self, json: dict):
        self.tracks = [RangedTrackInfo(item) for item in json["weeklytrackchart"]["track"]]


class RangedTrackInfo:
    def __init__(self, json: dict):
        self.track = json["name"]
        self.track_url = json["url"]
        self.artist = json["artist"]["#text"]
