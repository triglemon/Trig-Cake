from modules.steamapp import SteamApp
import asyncio
import json


class Background:
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.background())

    async def background(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            with open('json/steam.json') as steam:
                steamdict = json.load(steam)
            for steamid in steamdict:
                steamgame = SteamApp(steamid, self.bot)
                steamgame.fetchname()
                steamgame.fetchupdate()
                await steamgame.parse()
                await steamgame.trigger()
                steamgame.fetchsale()
                await steamgame.gaben()
                await steamgame.saletrigger()
            await asyncio.sleep(60 * 5)


def setup(bot):
    bot.add_cog(Background(bot))
