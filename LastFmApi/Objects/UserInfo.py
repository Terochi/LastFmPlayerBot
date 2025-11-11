class UserInfo:
    def __init__(self, json: dict):
        user = json["user"]

        self.play_count = int(user["playcount"])
        self.artist_count = int(user["artist_count"])
        self.track_count = int(user["track_count"])
        self.album_count = int(user["album_count"])
        self.playlist_count = int(user["playlists"])
