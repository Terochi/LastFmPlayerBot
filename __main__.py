import os
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()
    from DiscordBot.Commands import bot
    bot.run(os.getenv('BOT_TOKEN'))

# import asyncio

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