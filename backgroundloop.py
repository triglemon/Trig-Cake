from SteamApp import SteamApp
import asyncio
import json


class BackgroundLoop:
    def __init__(self, client):
        self.client = client
        self.client.loop.create_task(self.backgroundloop())

    async def backgroundloop(self):
        while not self.client.is_closed:
            with open('steam.json') as steam:
                steamdict = json.load(steam)
            for url in steamdict:
                splices = url.split('/')
                appid = splices[3] + splices[4]
                vars()[appid] = SteamApp(url, self.client)
                await vars()[appid].acquire()
                await vars()[appid].parse()
                vars()[appid].fetchjson()
                await vars()[appid].trigger()
                await vars()[appid].saletrigger()

            print("looped")
            await asyncio.sleep(60 * 5)


def setup(client):
    client.add_cog(BackgroundLoop(client))
