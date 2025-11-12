import importlib.util
import os
import discord

from discord.ext import commands
from DiscordBot.VoiceClient import VoiceClient

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

voice_clients: dict[int, VoiceClient] = {}

for root, _, files in os.walk(os.path.join(os.path.dirname(__file__), "Commands")):
    for file in files:
        if file[-3:] != ".py": continue
        filepath = os.path.join(root, file)
        module_name = file[:-3]
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
