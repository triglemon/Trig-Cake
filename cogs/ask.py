from discord.ext import commands
from modules.embed import *


class Ask:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        description = "I'm tasked with checking Steam games for announcements and Steam sales. All commands follow " \
                      "the prefix <&, and command arguments are closed by hyphens. Most of the following commands " \
                      "are available to all users, except for a few which are only available to those with admin perms."
        message = embed("Trig Cake", description)
        message.set_author(name="Github Repo ",
                           url="https://github.com/triglemon/Trig-Cake",
                           icon_url="https://raw.githubusercontent.com/triglemon/Trig-Cake/Cog-Cake/Logo.png")
        message.add_field(name="sub -url of store page-", value="Subscribes channel to a game.", inline=False)
        message.add_field(name="subbed", value="Prints list of games the channel is subscribed to.", inline=False)

        await launch(embed, ctx, self.bot)


def setup(client):
    client.add_cog(Ask(client))
