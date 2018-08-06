import asyncio
import aiohttp

age = {'birthtime': '283993201', 'mature_content': '1'}
aiosess = aiohttp.ClientSession(cookies=age)


async def tryget(url):
    async with aiosess.get(url) as doc:
        while True:
            if doc.status == 200:
                break
            await asyncio.sleep(5)
        return await doc.text()
