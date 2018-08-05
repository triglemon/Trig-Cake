from discord.ext import commands
import json


class Unsub:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def unsub(self, ctx, link):
        if ctx.message.author.server_permissions.administrator:
            url = link
            channelid = ctx.message.channel.id
            with open('steam.json') as steam:
                steamdict = json.load(steam)
            if url in steamdict:
                if channelid in steamdict[url]:
                    steamdict[url].remove(channelid)
                    if len(steamdict[url]) == 0:
                        del steamdict[url]
                        with open('updates.json') as updates:
                            updatesdict = json.load(updates)
                        del updatesdict[url]
                        with open('updates.json', 'w') as newupdates:
                            json.dump(updatesdict, newupdates)
                    with open('steam.json', 'w') as newsteam:
                        json.dump(steamdict, newsteam)

                        await self.client.say("Channel is now unsubscribed from that game.")
                else:
                    await self.client.say("Channel is not subscribed to that game.")
            else:
                await self.client.say("Channel is not subscribed to that game.")


def setup(client):
    client.add_cog(Unsub(client))
