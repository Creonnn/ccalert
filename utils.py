from config import Config as conf
import asyncio, aiohttp


async def fetch(url: str, session):
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"}
    try:
        async with conf.limiter:  # Ensures requests stay within limit
            async with session.get(url, headers=headers, timeout=conf.timeout) as response:
                return await response.text(), None
    except asyncio.TimeoutError:
        return None, "timed out"
    except aiohttp.ClientError as e:
        return None, "experienced client error"
    
async def shorten_url(url: str):
    api_url = f"https://tinyurl.com/api-create.php?url={url}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=conf.timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    return html, None
                else:
                    return None, "timed out"
    except asyncio.TimeoutError:
        return None, "timed out"
    except aiohttp.ClientError as e:
        return None, "experienced client error"