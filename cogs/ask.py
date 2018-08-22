"""
This module contains the help command for users seeking information.
"""
from discord.ext import commands
from modules.embed import Embed


class Ask:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help(self, ctx):
        description = ("I'm tasked with checking Steam games for "
                       "announcements and sales. All commands follow the "
                       "prefix <&, and command arguments are closed by "
                       "hyphens. Most of the following commands are available "
                       "to all users, except for a few which are only "
                       "available to those with manage channels.")
        discord_post = Embed("Trig Cake", description, self.bot, ctx=ctx)
        discord_post.message.set_author(
            name="Github Repo ",
            url="https://github.com/triglemon/Trig-Cake",
            icon_url=("https://raw.githubusercontent.com/"
                      "triglemon/Trig-Cake/Cog-Cake/Logo.png"))
        discord_post.message.add_field(name="sub -search terms-",
                                       value="Subscribes channel to a game."
                                             "Channels will automatically "
                                             "unsub after the bot leaves or is"
                                             "blocked from sending messages.",
                                       inline=False)
        discord_post.message.add_field(
            name="subbed",
            value="Prints list of games the channel is subscribed to, with"
                  "further commands available.",
            inline=False)

        await discord_post.launch_normal()


def setup(bot):
    bot.add_cog(Ask(bot))
