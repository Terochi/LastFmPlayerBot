import json
import os
from mutagen import File

song_folders = json.loads(os.getenv('LOCAL_AUDIO'))

def find_track_in_folders(target_artist, target_name):
    if target_artist: target_artist = target_artist.lower()
    if target_name: target_name = target_name.lower()
    for folder in song_folders:
        if not os.path.isdir(folder):
            continue
        for root, _, files in os.walk(folder):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    audio = File(filepath)
                    if audio:
                        artist = None
                        title = None

                        if 'artist' in audio.tags:
                            artist = audio.tags.get('artist')[0] if \
                                (isinstance(audio.tags.get('artist'), list)) else \
                                audio.tags.get('artist')
                        elif 'TPE1' in audio.tags:
                            artist = str(audio.tags.get('TPE1'))

                        if 'title' in audio.tags:
                            title = audio.tags.get('title')[0] if \
                                (isinstance(audio.tags.get('title'), list)) else \
                                audio.tags.get('title')
                        elif 'TIT2' in audio.tags:
                            title = str(audio.tags.get('TIT2'))

                        if artist and title:
                            if target_artist in artist.lower() and target_name in title.lower():
                                return title, artist, filepath

                    filename_no_ext = os.path.splitext(file)[0]
                    if target_name in filename_no_ext.lower():
                        return filename_no_ext, os.path.split(root)[-1], filepath
                except:
                    continue
    return None
