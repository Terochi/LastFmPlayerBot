import yt_dlp
import asyncio
import re

from bs4 import BeautifulSoup
from RequestHelper import get_text_async

ytdl = yt_dlp.YoutubeDL({
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'extract_flat': 'in_playlist',
})

def get_link(query):
    if re.match(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/', query):
        return query

    info = ytdl.extract_info(f"ytsearch:{query}", download=False)
    if 'entries' in info and len(info['entries']) > 0:
        return info['entries'][0]['url']

    print(f"Could not get link for {query}")
    return None

async def get_links_from_last_fm(url):
    text = await get_text_async(url)
    soup = BeautifulSoup(text, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', attrs={'data-youtube-id': True}):
        uid = a_tag['data-youtube-id']
        links.add(f"https://www.youtube.com/watch?v={uid}")
    return links

async def search_links(urls):
    loop = asyncio.get_running_loop()
    tasks = [loop.run_in_executor(None, get_link, urls[i]) for i in range(len(urls))]
    for completed_task in asyncio.as_completed(tasks):
        yield await completed_task
