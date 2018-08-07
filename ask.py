from discord.ext import commands


class Ask:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ask(self):
        info = """**I'm tasked with checking Steam games for announcements and Steam sales.**
The following commands are available for users with Administrator perms (minus brackets):

**!cakesub <url of store page>** — Subscribes channel to a game.
**!cakeunsub <url of store page>** — Unsubscribes channel to a game.

The following commands are available to regular users too:

**!cakesubbed** — Prints list of games the channel is subscribed to.
**!cakesale <url of store page>** — Informs if the game is on sale or not.
**!cakeslice <id>** — id can be 'me' or 'anon' (minus quotes). 
This sends the team a 'slice of cake', a small gesture of appreciation for our work. 
'me' sends a message with your name and can only be done once, and 'anon' is 100% anonymous if you want to stay hidden!"""
        await self.client.say(info)


def setup(client):
    client.add_cog(Ask(client))
