"""
This module makes an aiohttp session in order to get requests using the
modified cookies.
"""
import asyncio
import aiohttp

cookies = {'birthtime': '283993201', 'mature_content': '1'}
session = aiohttp.ClientSession(cookies=cookies)


class TryGet:
    def __init__(self):
        self.session = session

    def session_status(self):
        return self.session.closed

    async def refresh_session(self):
        await self.session.close()
        self.session = aiohttp.ClientSession(cookies=cookies)

    async def get_request(self, url):
        if self.session_status():
            await self.refresh_session()
        async with self.session.get(url) as doc:
            for x in range(0, 5):
                if doc.status == 200:
                    break
                await asyncio.sleep(5)
            if doc.status != 200:
                raise Exception('CakeConnectionError')
            return await doc.text()
