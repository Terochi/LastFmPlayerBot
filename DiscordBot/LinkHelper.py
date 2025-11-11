import yt_dlp
import asyncio
import re

from bs4 import BeautifulSoup

from DiscordBot.QueueItem import QueueItem
from RequestHelper import get_text_async

ytdl = yt_dlp.YoutubeDL({
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'nocheckcertificate': True,
    'default_search': 'ytsearch',
    'extract_flat': 'in_playlist',
    'source_address': '0.0.0.0',
})

def get_stream_url(url):
    return ytdl.extract_info(url, download=False)['url']

def get_link(query):
    if re.match(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/', query):
        return query

    info = ytdl.extract_info(f"ytsearch:{query}", download=False)
    if 'entries' in info and len(info['entries']) > 0:
        first = info['entries'][0]
        return QueueItem(first['title'], first['channel'], first['url'])

    print(f"Could not get link for {query}")
    return None


def populate_link(queue_item: QueueItem, query):
    link = get_link(query)
    if not link: return None
    queue_item.uri = link
    return queue_item

async def get_links_from_last_fm(url):
    text = await get_text_async(url)
    if not text: return None
    soup = BeautifulSoup(text, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', attrs={'data-youtube-id': True}):
        uid = a_tag['data-youtube-id']
        links.add(f"https://www.youtube.com/watch?v={uid}")
    return links


async def search_links(queries):
    loop = asyncio.get_running_loop()
    tasks = [loop.run_in_executor(None, get_link, queries[i]) for i in range(len(queries))]
    for completed_task in asyncio.as_completed(tasks):
        result = await completed_task
        if result:
            yield result


async def populate_links(queue_items, queries):
    loop = asyncio.get_running_loop()
    tasks = [loop.run_in_executor(None, populate_link, queue_items[i], queries[i]) for i in
             range(min(len(queries), len(queue_items)))]
    for completed_task in asyncio.as_completed(tasks):
        result = await completed_task
        if result:
            yield result
