import asyncio
import string

from DiscordBot.FileHelper import find_track_in_folders
from DiscordBot.LinkHelper import get_links_from_last_fm, get_link, run_in_parallel, run_in_parallel_async
from DiscordBot.QueueItem import QueueItem
from LastFmApi.Facade import get_loved_tracks, get_top_tracks
from LastFmApi.Users import last_fm_users


async def populate_queue_for_query(ctx, vc, query):
    item = find_file(query)
    if item:
        vc.queue.append(item)
        return

    item = get_link(query)
    if item:
        vc.queue.append(item)
        return

    await ctx.send("Couldn't find a song to add.")


async def populate_queue_for_tracks(vc, tracks):
    async for item in run_in_parallel_async([get_item_from_track(track) for track in tracks]):
        vc.queue.append(item)


def find_file(query):
    def is_word(word):
        if not word: return False
        return any([c in string.ascii_letters or c in string.digits for c in word])

    words = [word for word in query.split() if is_word(word)]
    word_count = len(words)
    if word_count == 1:
        return find_track_in_folders(words[0], None, True)
    if word_count == 2:
        return find_track_in_folders(words[0], words[1], False)
    return None


async def get_last_fm_tracks_for_channel(channel):
    users = 0
    all_tracks = dict()
    for member in channel.members:
        last_fm = last_fm_users.get(str(member.id))
        if not last_fm: continue
        last_fm_username = last_fm["name"]
        users += 1
        # info = await get_user_info(last_fm_username)
        tracks = await get_loved_tracks(last_fm_username)
        if tracks:
            for t in tracks.tracks:
                all_tracks[t.track_url] = t # Add track to output
        tracks = await get_top_tracks(last_fm_username, limit=10, page=7) # track 71-80
        if tracks:
            for t in tracks.tracks:
                all_tracks[t.track_url] = t

    return list(all_tracks.values())


async def get_item_from_track(track):
    found = find_track_in_folders(track.track, track.artist)
    if found:
        print(f"Found from folders: {track.artist} - {track.track}")
        return found
    links = await get_links_from_last_fm(track.track_url)
    if links:
        print(f"Found from last fm: {track.artist} - {track.track}")
        return QueueItem(track.track, track.artist, next(iter(links)), False)
    link = get_link(f"{track.artist} - {track.track}")
    if link:
        link.track = track.track
        link.artist = track.artist
        print(f"Found from yt search: {track.artist} - {track.track}")
    return link

