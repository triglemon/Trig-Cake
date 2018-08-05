from discord.ext import commands


class Ask:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ask(self):
        info = """**I'm tasked with checking Steam games for announcements.**
The following commands are available for users with Administrator perms (minus brackets):
**!cakesub <url of store page>** — Subscribes channel to a game.
**!cakeunsub <url of store page>** — Unsubscribes channel to a game.
**!cakesubbed** — Prints list of games the channel is subscribed to."""
        await self.client.say(info)


def setup(client):
    client.add_cog(Ask(client))
