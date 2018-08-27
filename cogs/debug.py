"""
This module contains commands for testing/debugging purposes. Mostly obselete.
"""
from discord.ext import commands
from modules.tryget import TryGet
from bs4 import BeautifulSoup as Soup


class Debug:
    def __init__(self, bot):
        self.bot = bot
        self.session = TryGet()

    @commands.command(name='status')
    @commands.is_owner()
    async def status(self, ctx):
        await ctx.send("Is closed: " + str(self.session.session_status()))

    @commands.command(name='refresh')
    @commands.is_owner()
    async def refresh(self, ctx):
        await self.session.refresh_session()
        await ctx.send("Is closed: " + str(self.session.session_status()))

    @commands.command(name='purge')
    @commands.is_owner()
    async def purge_channel(self, ctx):
        """Purges testing channel only"""
        channel = self.bot.get_channel(466807163323416588)
        await channel.purge(limit=100)
        await ctx.send("Purged!")

    @commands.command(name='me')
    @commands.is_owner()
    async def me(self, ctx):
        my_request = await self.session.get_request(
            'https://steamcommunity.com/id/punnedit/')
        my_soup = Soup(my_request, 'html.parser')
        my_quote = my_soup.find('meta', {'property': 'og:description'})
        my_excerpt = my_quote['content']
        await ctx.send(my_excerpt)


def setup(bot):
    bot.add_cog(Debug(bot))
