import json
from discord.ext import commands
from bs4 import BeautifulSoup as Soup
from modules.tryget import tryget
from modules.embed import *


class SteamGames:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='sub')
    async def sub(self, ctx, *args):
        searchurl = 'https://store.steampowered.com/search/?term='
        keyword = ""
        for arg in args:
            keyword = keyword + " " + arg
            searchurl = searchurl + f'{arg}+'
        searchurl = searchurl[:-1]
        result = await tryget(searchurl)
        resultpage = Soup(result, 'html.parser')
        top5 = [title for title in resultpage('span', {'class': 'title'})[0:5]]
        message = embed(f"Searching for {keyword}", "The following search results were found...")
        commandlist = []
        for entry in top5:
            place = top5.index(entry) + 1
            message.add_field(name=f"Entry #{place}", value=entry.text, inline=False)
            commandlist.append(f'{place}\u20e3')
        decision = await launch(message, ctx, self.bot, 30.0, commandlist)
        appid = top5[int(decision[0]) - 1].parent.parent.parent['data-ds-appid']
        with open('json/steam.json') as steam:
            steamdict = json.load(steam)
        if appid not in steamdict:
            steamdict[appid] = []
        if ctx.message.channel.id in steamdict[appid]:
            unsuccessful = embed("Unsuccessful.", f"This channel is already subscribed to {entry.text}.")
            await launch(unsuccessful, ctx, self.bot)
        else:
            steamdict[appid].append(ctx.message.channel.id)
            with open('json/steam.json', 'w') as newsteam:
                json.dump(steamdict, newsteam)
            success = embed("Success!", f"This channel is now subscribed to {entry.text}!")
            await launch(success, ctx, self.bot)
            for file in ['steam', 'sale']:
                with open(f'json/{file}.json') as jfile:
                    dict = json.load(jfile)
                # if appid not in dict:


def setup(bot):
    bot.add_cog(SteamGames(bot))
