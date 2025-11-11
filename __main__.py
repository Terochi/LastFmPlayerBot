import os
import random

import discord
import json
from discord import FFmpegOpusAudio
from discord.ext import commands
import yt_dlp
import asyncio
import re
from dotenv import load_dotenv

from LastFmApi.Facade import *

load_dotenv()

FILE_NAME = 'user_lastfm.json'
LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')
BOT_TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

user_lastfm = {}
def save_user_lastfm():
    global user_lastfm
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(user_lastfm, f, ensure_ascii=False, indent=4)

def load_user_lastfm():
    global user_lastfm
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            user_lastfm = json.load(f)
    else:
        user_lastfm = {}

load_user_lastfm()

@bot.command(name="register")
async def register(ctx, lastfm_username: str):
    user_lastfm[str(ctx.author.id)] = lastfm_username
    save_user_lastfm()
    await ctx.send(f"Registered your Last.fm username as: {lastfm_username}")

ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'extract_flat': 'in_playlist',
}

ytdlp_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',  # Bind to IPv4 since some networks give issues
}

ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

def create_source(url):
    ydl = yt_dlp.YoutubeDL(ytdlp_opts)
    info = ydl.extract_info(url, download=False)
    return FFmpegOpusAudio(info['url'], **ffmpeg_opts)

music_queue = []

async def search_youtube(query):
    if re.match(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/', query):
        return query

    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{query}", download=False))
    if 'entries' in info and len(info['entries']) > 0:
        return info['entries'][0]['url']
    return None

async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to play music.")
        return None
    channel = ctx.author.voice.channel
    guild_id = ctx.guild.id

    if guild_id not in voice_clients or not voice_clients[guild_id].is_connected():
        vc = await channel.connect()
        voice_clients[guild_id] = vc
        return vc
    else:
        return voice_clients[guild_id]

@bot.command(name="play")
async def play(ctx):
    vc = await join(ctx)
    if not vc:
        return

    if not music_queue:
        await ctx.send("The music queue is empty.")
        return

    if vc and vc.is_playing() and not skip:
        return

    await play_next(ctx)

@bot.command(name='shuffle')
async def shuffle(ctx):
    if not music_queue:
        await ctx.send("The queue is empty, nothing to shuffle.")
        return
    random.shuffle(music_queue)
    await ctx.send("Shuffled the music queue!")

@bot.command(name="list")
async def list_queue(ctx):
    if not music_queue:
        await ctx.send("The queue is currently empty.")
        return
    message = "Current Queue:\n"
    for i, track in enumerate(music_queue, start=1):
        message += f"{i}. {track}\n"
    await ctx.send(message)

async def add_tracks_from_lastfm(ctx, lastfm_user, start_playing=False):
    tracks = await fetch_lastfm_tracks(lastfm_user, LASTFM_API_KEY)
    for track in tracks:
        query = f"{track['artist']} - {track['title']}"
        youtube_url = await search_youtube(query)
        if youtube_url:
            await ctx.send(f"Added {query}")
            music_queue.append((query, youtube_url))
            if start_playing:
                await play(ctx)
        else:
            await ctx.send(f"Couldn't fetch {query}")

async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def fetch_last_fm_user(method, username, limit=50):
    return await fetch_url(f"http://ws.audioscrobbler.com/2.0/?method=user.{method}&user={username}&api_key={LASTFM_API_KEY}&format=json&limit={limit}")

async def fetch_lastfm_tracks(username, api_key, limit=20):
    url = f"http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={username}&api_key={api_key}&format=json&limit={limit}"
    data = await fetch_url(url)
    # Extract tracks from the JSON response
    tracks = data.get('toptracks', {}).get('track', [])
    # Map to simple dict list with artist and title
    result = []
    for track in tracks:
        artist_name = track.get('artist', {}).get('name')
        track_name = track.get('name')
        if artist_name and track_name:
            result.append({'artist': artist_name, 'title': track_name})
    return result

voice_clients = {}

# Example command to add a song to the queue from Last.fm or manual input
@bot.command(name="add")
async def add(ctx, *, search: str):
    yt_url = await search_youtube(search)
    music_queue.append((search, yt_url))
    await ctx.send(f"Added to queue: {search}")

@bot.command(name="skip")
async def skip(ctx):
    guild_id = ctx.guild.id
    vc = voice_clients.get(guild_id)
    if not vc or not vc.is_connected():
        await ctx.send("I'm not connected to a voice channel.")
        return
    if not vc.is_playing():
        await ctx.send("There is no song playing right now.")
        return
    vc.stop()  # This triggers after_playing callback to play the next track
    await ctx.send("Skipped the current track.")

async def play_next(ctx):
    guild_id = ctx.guild.id
    vc = voice_clients.get(guild_id)
    if not vc or not music_queue:
        if vc:
            await vc.disconnect()
            voice_clients.pop(guild_id, None)
        return

    query, track_url = music_queue.pop(0)

    def after_playing(error):
        fut = asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        try:
            fut.result()
        except:
            pass

    await ctx.send(f"Playing {query}")
    vc.play(create_source(track_url), after=after_playing)

@bot.command()
async def playlastfm(ctx):
    vc = await join(ctx)
    if not vc:
        return

    global music_queue
    music_queue = []
    users = 0
    for member in ctx.author.voice.channel.members:
        lastfm_username = user_lastfm.get(str(member.id))
        if lastfm_username:
            users += 1
            await add_tracks_from_lastfm(ctx, lastfm_username, True)

    await ctx.send(f"Playing playlist from {users} users.")
    await play(ctx)

async def print_tracks(name):
    tracks = await fetch_lastfm_tracks(name, LASTFM_API_KEY)
    for track in tracks:
        print(track)

# asyncio.run(print_tracks("troen"))

async def fetch_and_print(method, username):
    r = await fetch_last_fm_user(method, username)
    print(method)
    print(r)
    print("\n")

user = "terochi"
track_name = "たぶん終わり"
artist_name = "Iyowa"

# uri = "https://www.last.fm/music/%E3%81%84%E3%82%88%E3%82%8F/%E6%98%A0%E7%94%BB%E3%80%81%E9%99%BD%E3%81%A0%E3%81%BE%E3%82%8A%E3%80%81%E5%8D%92%E6%A5%AD%E5%BC%8F"
#
# response = requests.get(uri)
# response.raise_for_status()  # Ensure we got a successful response
#
# # Step 2: Parse HTML
# soup = BeautifulSoup(response.text, 'html.parser')
#
# # Step 3: Extract all 'data-youtube-id' attributes from <a> tags
# youtube_ids = set()
# for a_tag in soup.find_all('a', attrs={'data-youtube-id': True}):
#     youtube_id = a_tag['data-youtube-id']
#     youtube_ids.add(youtube_id)
#
# # Step 4: Output unique data-youtube-id values
# for uid in youtube_ids:
#     print(f"https://www.youtube.com/watch?v={uid}")
# else:
#     print("No video found")

# print(requests.get(f"http://ws.audioscrobbler.com/2.0/?method=track.getinfo&username={user}&api_key={LASTFM_API_KEY}&format=json&track={track_name}&artist={artist_name}").json())
# user_info = asyncio.run(get_user_info(user))
# track_info = asyncio.run(get_track_info(user, track_name, artist_name))

# track_range = asyncio.run(get_ranged_tracks(user))
# artist_range = asyncio.run(get_ranged_artists(user))
# albums_range = asyncio.run(get_ranged_albums(user))

# loved_tracks = asyncio.run(get_loved_tracks(user))
# top_tracks = asyncio.run(get_top_tracks(user))
# top_tracks5 = asyncio.run(get_top_tracks(user, limit=1, page=5))
# top_albums = asyncio.run(get_top_albums(user))
# top_artists = asyncio.run(get_top_artists(user))

import YoutubeApi.LinkHelper

async def main():
    async for link in YoutubeApi.LinkHelper.search_links(["iyowa kyuu kurarin", "rule ado", "missing, missing miku 7"]):
        print(f"Result: {link}")

asyncio.run(main())

# bot.run(BOT_TOKEN)
