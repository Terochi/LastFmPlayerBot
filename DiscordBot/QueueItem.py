class QueueItem:
    def __init__(self, track, artist, uri, is_file=False):
        self.track = track
        self.artist = artist
        self.uri = uri
        self.is_file = is_file