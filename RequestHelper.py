import aiohttp
import requests

def get_json(url):
    result = requests.get(url)
    if result.status_code != 200:
        return None

    return result.json()

def get_text(url):
    result = requests.get(url)
    if result.status_code != 200:
        return None

    return result.text

async def get_json_async(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None

            return await response.json()

async def get_text_async(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None

            return await response.text()