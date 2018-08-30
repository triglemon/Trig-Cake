"""
This module runs the background loop as bot becomes ready. For every app id in
steam.json, the loop makes a SteamApp object and checks if it's gone on sale or
a new headline has been posted every 5 minutes.

At the start of the task, any unavailable channels are purged.
"""
import json
import datetime
import asyncio
import aiofiles
from modules.steamapp import SteamApp
from modules.json import async_load
from modules.json import delete_dump
from modules.json import remove_dump


class Background:
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.purge_task())
        self.bot.loop.create_task(self.scrape_task())

    async def purge_task(self):

        async def purge_channel(channel_id):
            id_list = subbed_dict[channel_id]
            await delete_dump(subbed_dict, channel_id, 'subbed')
            steam_dict = await async_load('steam')
            for app_id in id_list:
                last_entry = await remove_dump(steam_dict,
                                               app_id,
                                               int(channel_id),
                                               'steam')
                if last_entry:
                    for file_name in ['name', 'sale', 'update']:
                        json_dict = await async_load(file_name)
                        await delete_dump(json_dict, app_id, file_name)
            async with aiofiles.open('badlog', 'a') as badlog:
                await badlog.write(str(datetime.datetime.now()) + ' Purge \n')

        await self.bot.wait_until_ready()
        while True:
            subbed_dict = await async_load('subbed')
            for channel_id in list(subbed_dict):
                channel = self.bot.get_channel(int(channel_id))
                if not channel:
                    self.bot.loop.create_task(purge_channel(channel_id))
                else:
                    guild = channel.guild
                    if not guild.me.permissions_in(channel).send_messages:
                        self.bot.loop.create_task(purge_channel(channel_id))
            await asyncio.sleep(60 * 60 * 3)

    async def scrape_task(self):

        async def scrape_steam():
            steam_dict = await async_load('steam')
            for steam_id in steam_dict:
                steam_game = SteamApp(steam_id, self.bot)
                await steam_game.fetch_name()
                await steam_game.fetch_update()
                await steam_game.parse_news()
                await steam_game.news_trigger()
                await steam_game.fetch_sale()
                await steam_game.gaben_pls()
                await steam_game.sale_trigger()
                async with open('badlog', 'a') as badlog:
                    await badlog.write(
                        str(datetime.datetime.now()) + ' Scrape \n')

        while True:
            await self.bot.wait_until_ready()
            self.bot.loop.create_task(scrape_steam())
            await asyncio.sleep(60 * 5)


def setup(bot):
    bot.add_cog(Background(bot))
