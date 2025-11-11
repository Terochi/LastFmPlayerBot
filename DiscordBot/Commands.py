import asyncio
import os.path
import random

import discord

from discord.ext import commands
from DiscordBot.AudioLoader import *
from DiscordBot.FileHelper import find_track_in_folders
from DiscordBot.LinkHelper import get_link, search_links, get_links_from_last_fm, populate_links
from DiscordBot.QueueItem import QueueItem
from DiscordBot.VoiceClient import VoiceClient
from LastFmApi.Facade import get_user_info, get_track_info, get_loved_tracks, get_top_tracks
from LastFmApi.Users import last_fm_users, save_last_fm_users

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

voice_clients: dict[int, VoiceClient] = {}


@bot.command(name="list")
async def list_queue(ctx):
    vc = voice_clients.get(ctx.guild.id)
    if not vc or not vc.queue:
        await ctx.send("The queue is currently empty.")
        return

    message = "Current Queue:\n"
    for i, item in enumerate(vc.queue, start=1):
        message += f"{i}. {item.track} - {item.artist}\n"
    await ctx.send(message)


async def join(ctx) -> VoiceClient | None:
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to play music.")
        return None

    channel = ctx.author.voice.channel
    guild_id = ctx.guild.id

    vc = voice_clients.get(guild_id)
    if not vc or not vc.client.is_connected():
        vc = VoiceClient(await channel.connect())
        voice_clients[guild_id] = vc
        return vc
    else:
        return voice_clients[guild_id]


@bot.command(name="clear")
async def clear(ctx):
    guild_id = ctx.guild.id
    vc = voice_clients.get(guild_id)
    if not vc:
        return

    vc.queue.clear()
    await ctx.send("Cleared current queue.")


@bot.command(name="play")
async def play(ctx, *, search: str=None):
    vc = await join(ctx)
    if not vc:
        return

    if search:
        words = search.split()
        item = None
        if len(words) == 2:
            found = find_track_in_folders(words[0], words[1])
            if found:
                item = QueueItem(*found, True)
            else:
                found = find_track_in_folders(words[1], words[0])
                if found:
                    item = QueueItem(*found, True)
        if len(words) == 1:
            found = find_track_in_folders(None, words[0])
            if found:
                item = QueueItem(*found, True)

        if not item:
            item = get_link(search)
        if not item:
            await ctx.send("Couldn't find a song to add.")
            return

        vc.queue.append(item)
        await ctx.send(f"Added to queue: {item.track} - {item.artist}")
    elif not vc.queue:
        users = 0
        all_tracks = dict()
        for member in vc.client.channel.members:
            last_fm_username = last_fm_users.get(str(member.id))
            if not last_fm_username: continue
            users += 1
            # info = await get_user_info(last_fm_username)
            tracks = await get_loved_tracks(last_fm_username)
            if tracks:
                for t in tracks.tracks:
                    all_tracks[t.track_url] = t
            # tracks = await get_top_tracks(last_fm_username)
            # if tracks:
            #     for t in tracks.tracks:
            #         all_tracks[t.track_url] = t

        not_found_tracks = []
        for t in all_tracks.values():
            links = await get_links_from_last_fm(t.track_url)
            if links:
                print(f"Adding {t.track} - {t.artist} from last fm")
                vc.queue.append(QueueItem(t.track, t.artist, next(iter(links)), False))
            else:
                not_found_tracks.append(t)

        async for queue_item in populate_links([QueueItem(t.track, t.artist, None, False) for t in not_found_tracks],
                             [f"{t.track} - {t.artist}" for t in not_found_tracks]):
            print(f"Adding {queue_item.track} - {queue_item.artist} from yt search")
            vc.queue.append(queue_item)

        await shuffle(ctx)

    if not vc.queue:
        await ctx.send("The music queue is empty.")
        return

    if vc and vc.client.is_playing():
        return

    await play_next(ctx)


@bot.command(name="skip")
async def skip(ctx):
    guild_id = ctx.guild.id
    vc = voice_clients.get(guild_id)
    if not vc or not vc.client.is_connected():
        await ctx.send("Not connected to a voice channel.")
        return

    if not vc.client.is_playing():
        await ctx.send("There is no song playing right now.")
        return

    await ctx.send("Skipping current track.")

    vc.client.source.cleanup()
    vc.client.stop()  # Triggers after_playing


@bot.command(name="stop")
async def stop(ctx):
    guild_id = ctx.guild.id
    vc = voice_clients.get(guild_id)
    if not vc or not vc.client.is_connected():
        await ctx.send("Not connected to a voice channel.")
        return

    if not vc.client.is_playing():
        return

    await ctx.send("Stopping current track.")

    global playing
    playing = False
    vc.client.source.cleanup()
    vc.client.stop()


playing = False


async def play_next(ctx):
    guild_id = ctx.guild.id
    vc = voice_clients.get(guild_id)
    if not vc or not vc.queue:
        if vc:
            await vc.client.disconnect()
            voice_clients.pop(guild_id)
        return

    item = vc.queue.pop(0)

    def after_playing(_):
        if not playing: return
        fut = asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        try:
            fut.result()
        except:
            pass

    await ctx.send(f"Playing: {item.track} - {item.artist}")
    global playing
    playing = True

    source = source_file(item.uri) if item.is_file else source_link(item.uri)
    vc.client.play(source, after=after_playing)


@bot.command(name='shuffle')
async def shuffle(ctx):
    guild_id = ctx.guild.id
    vc = voice_clients.get(guild_id)
    if not vc or not vc.queue:
        await ctx.send("The queue is empty, nothing to shuffle.")
        return

    random.shuffle(vc.queue)
    await ctx.send("Shuffled the queue")


@bot.command(name="leave")
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.disconnect()


@bot.command(name="register")
async def register(ctx, lastfm_username: str):
    if not await get_user_info(lastfm_username):
        await ctx.send(f"Your Last.fm username is invalid.")
        return

    last_fm_users[str(ctx.author.id)] = lastfm_username
    save_last_fm_users()
    await ctx.send(f"Registered your Last.fm username as {lastfm_username}.")


@bot.command(name="unregister")
async def unregister(ctx):
    last_fm_users.pop(str(ctx.author.id))
    save_last_fm_users()
    await ctx.send(f"Unregistered your Last.fm username.")
