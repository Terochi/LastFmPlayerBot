from discord import FFmpegOpusAudio

from DiscordBot.LinkHelper import get_stream_url


def source_link(url):
    return FFmpegOpusAudio(
        source=get_stream_url(url),
        before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        options='-vn')


def source_file(filename):
    return FFmpegOpusAudio(source=filename)
