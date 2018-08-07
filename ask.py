from discord.ext import commands
import discord


class Ask:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ask(self):
        description = "I'm tasked with checking Steam games for announcements and Steam sales. Most of the following " \
                      "commands are available to all users (minus hyphens), except for a few which are only " \
                      "available to those with admin perms."
        embed = discord.Embed(title="Trig Cake", description=description)
        embed.set_author(name="Github Repo ",
                         url="https://github.com/triglemon/Trig-Cake",
                         icon_url="https://raw.githubusercontent.com/triglemon/Trig-Cake/Cog-Cake/Logo.png")
        embed.add_field(name="!cakesub -url of store page-", value="Subscribes channel to a game.", inline=False)
        embed.add_field(name="!cakeunsub -url of store page-", value="Unsubscribes channel to a game.", inline=False)
        embed.add_field(name="!cakesubbed", value="Prints list of games the channel is subscribed to.", inline=False)
        embed.add_field(name="!cakesale -url of store page-", value="Informs if the game is on sale or not.",
                        inline=False)
        embed.add_field(name="!cakeslice -id-",
                        value="id can be 'me' or 'anon' (minus quotes). This sends the team a 'slice of cake', a small "
                              "gesture of appreciation for our work. 'me' sends a message with your name and can only "
                              "be done once, while 'anon' is 100% anonymous and can be done as many times as you want.",
                        inline=False)

        await self.client.say(embed=embed)


def setup(client):
    client.add_cog(Ask(client))
