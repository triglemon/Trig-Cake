from discord.ext import commands
from modules.tryget import tryget
from bs4 import BeautifulSoup as Soup


class SteamGames:
    def __init__(self, client):
        self.client = client

    @commands.command
    async def sub(self, ctx, *args):
        searchurl = 'https://store.steampowered.com/search/?term='
        for arg in args:
            searchurl = searchurl + f"{arg}+"
        searchurl = searchurl[:-1]
        result = await tryget(searchurl)
        resultpage = Soup(result, 'html.parser')
        
