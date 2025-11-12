import random

from DiscordBot.AudioLoader import *
from DiscordBot.Init import bot, voice_clients
from DiscordBot.QueueHelper import *
from DiscordBot.VoiceClient import VoiceClient
from LastFmApi.Auth import *


async def join(ctx) -> VoiceClient | None:
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel.")
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


@bot.command(name="play")
async def play(ctx, *, search: str = None):
    vc = await join(ctx)
    if not vc:
        return

    if search:
        await populate_queue_for_query(ctx, vc, search)
        await play_next(ctx)
    elif not vc.queue:
        tracks = await get_last_fm_tracks_for_channel(vc.client.channel)
        random.shuffle(tracks)
        for i in range(len(tracks)):
            item = await get_item_from_track(tracks[i])
            if not item: continue
            vc.queue.append(item)
            await play_next(ctx)
            await populate_queue_for_tracks(vc, tracks[i + 1:])
            random.shuffle(vc.queue)
            break

    if not vc.queue:
        await ctx.send("The music queue is empty.")


@bot.command(name="skip")
async def skip(ctx):
    vc = voice_clients.get(ctx.guild.id)
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
    vc = voice_clients.get(ctx.guild.id)
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
    global playing
    guild_id = ctx.guild.id
    vc = voice_clients.get(guild_id)
    if not vc or not vc.queue:
        if vc:
            await vc.client.disconnect()
            voice_clients.pop(guild_id)
            playing = False
        return

    if vc.client.is_playing() and playing:
        return

    item = vc.queue.pop(0)

    def after_playing(_):
        if not playing: return
        fut = asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        try:
            fut.result()
        except:
            pass

    await ctx.send(f"Playing: {item.artist} - {item.track}")
    playing = True

    source = source_file(item.uri) if item.is_file else source_link(item.uri)
    vc.client.play(source, after=after_playing)


@bot.command(name="leave")
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.disconnect()
