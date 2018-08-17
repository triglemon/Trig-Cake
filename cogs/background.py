"""
This module runs the background loop as bot becomes ready. For every app id in
steam.json, the loop makes a SteamApp object and checks if it's gone on sale or
a new headline has been posted every 5 minutes.
"""
import asyncio
import json
from modules.steamapp import SteamApp


class Background:
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.background())

    async def background(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            with open('json/steam.json') as steam:
                steam_dict = json.load(steam)
            for steam_id in steam_dict:
                steam_game = SteamApp(steam_id, self.bot)
                steam_game.fetch_name()
                steam_game.fetch_update()
                await steam_game.parse_news()
                await steam_game.news_trigger()
                steam_game.fetch_sale()
                await steam_game.gaben_pls()
                await steam_game.sale_trigger()
            await asyncio.sleep(60 * 5)


def setup(bot):
    bot.add_cog(Background(bot))
