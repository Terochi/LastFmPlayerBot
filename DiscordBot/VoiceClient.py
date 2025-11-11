import discord

from DiscordBot.QueueItem import QueueItem


class VoiceClient:
    def __init__(self, client):
        self.client: discord.VoiceClient = client
        self.queue: list[QueueItem] = []
