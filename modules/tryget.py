"""
This module gets requests, mainly from steam sites, using the modified cookies.
"""
import asyncio
import aiohttp

AGE = {'birthtime': '283993201', 'mature_content': '1'}
AIO_SESSION = aiohttp.ClientSession(cookies=AGE)


async def try_get(url):
    """Requests to steam site until proper 200 status."""
    async with AIO_SESSION.get(url) as doc:
        while True:
            if doc.status == 200:
                break
            await asyncio.sleep(5)
        return await doc.text()
