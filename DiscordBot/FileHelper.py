import json
import os
from mutagen import File

from DiscordBot.QueueItem import QueueItem

song_folders = json.loads(os.getenv('LOCAL_AUDIO'))


def get_audio_tags(filepath):
    artist = None
    title = None
    try:
        audio = File(filepath)
        if not audio: return None, None

        if 'artist' in audio.tags:
            artist = (audio.tags.get('artist')[0] if
                      (isinstance(audio.tags.get('artist'), list)) else
                      audio.tags.get('artist'))
        elif 'TPE1' in audio.tags:
            artist = str(audio.tags.get('TPE1'))

        if 'title' in audio.tags:
            title = (audio.tags.get('title')[0] if
                     (isinstance(audio.tags.get('title'), list)) else
                     audio.tags.get('title'))
        elif 'TIT2' in audio.tags:
            title = str(audio.tags.get('TIT2'))
    except:
        return None, None

    return artist, title


def rank_match(target_name, target_artist, dir_name, file_name, artist, title):
    rank = 0
    if artist and target_artist:
        if target_artist in artist.lower():
            rank += 2
    if title and target_name:
        if target_name in title.lower():
            rank += 4

    if target_artist in dir_name.lower():
        rank += 1
    if target_name in file_name.lower():
        rank += 3

    return rank


def find_track_in_folders(target_name, target_artist, known_order=True):
    if target_name: target_name = target_name.lower()
    if target_artist: target_artist = target_artist.lower()

    possible_result = None
    possible_rank = 0

    for folder in song_folders:
        if not os.path.isdir(folder):
            continue
        for root, _, files in os.walk(folder):
            dir_name = os.path.split(root)[-1]
            dir_name_lower = dir_name.lower()
            for file in files:
                filepath = os.path.join(root, file)
                artist, title = get_audio_tags(filepath)
                file_name = os.path.splitext(file)[0]
                rank = rank_match(target_name, target_artist, dir_name_lower, file_name, artist, title)
                if not known_order:
                    rank = max(rank, rank_match(target_artist, target_name, dir_name_lower, file_name, artist, title))

                if rank > possible_rank:
                    possible_result = QueueItem(
                        title or file_name,
                        artist or dir_name,
                        filepath,
                        True
                    )

    return possible_result
