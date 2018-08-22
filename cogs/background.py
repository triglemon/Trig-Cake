"""
This module runs the background loop as bot becomes ready. For every app id in
steam.json, the loop makes a SteamApp object and checks if it's gone on sale or
a new headline has been posted every 5 minutes.

At the start of the task, any unavailable channels are purges.
"""
import asyncio
import logging
import json
from modules.steamapp import SteamApp


class Background:
    def __init__(self, bot):
        def task_after(task):
            exc = task.exception()
            if exc is not None:
                exc_info = exc.__class__, exc, exc.__traceback__
                logging.log(logging.ERROR,
                            'Error occurred in background task',
                            exc_info=exc_info)
        self.bot = bot
        task = self.bot.loop.create_task(self.background())
        task.add_done_callback(task_after)

    async def background(self):

        def purge_channel(channel_id):
            id_list = subbed_dict[channel_id]
            del subbed_dict[channel_id]
            with open('json/subbed.json', 'w') as new_subbed:
                json.dump(subbed_dict, new_subbed)
            with open('json/steam.json') as steam:
                steam_dict = json.load(steam)
            for app_id in id_list:
                steam_dict[app_id].remove(int(channel_id))
                if not steam_dict[app_id]:
                    del steam_dict[app_id]
                    for file_name in ['name', 'sale', 'update']:
                        with open(f'json/{file_name}.json') as json_file:
                            json_dict = json.load(json_file)
                        del json_dict[app_id]
                        with open(f'json/{file_name}.json', 'w') as new_json:
                            json.dump(json_dict, new_json)
            with open('json/steam.json', 'w') as new_steam:
                json.dump(steam_dict, new_steam)

        await self.bot.wait_until_ready()
        with open('json/subbed.json') as subbed:
            subbed_dict = json.load(subbed)
        for channel_id in list(subbed_dict):
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                purge_channel(channel_id)
            else:
                guild = channel.guild
                if not guild.me.permissions_in(channel).send_messages:
                    purge_channel(channel_id)

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
