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
