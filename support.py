from discord.ext import commands
import json
import discord


class Support:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def slice(self, ctx, anon):
        if anon == "anon":
            embed = discord.Embed(title="Thanks for sending the team a slice of cake, anonymous user!",
                                  description="This is a small act that shows us your appreciation.",
                                  color=0xebbe23)
            await self.client.say(embed=embed)
            with open('slice.json') as slice:
                slicedict = json.load(slice)
            if 'anon' not in slicedict:
                slicedict['anon'] = 1
            else:
                slicedict['anon'] += 1
            if 'total' not in slicedict:
                slicedict['total'] = 1
            else:
                slicedict['total'] += 1
            with open('slice.json', 'w') as newslice:
                json.dump(slicedict, newslice)
            sliceembed = discord.Embed(title="You got sent a slice from anon!",
                                  description=f"Slices recieved: {str(slicedict['total'])}",
                                  color=0xebbe23)
            await self.client.send_message(discord.Object(id='466807163323416588'), embed=sliceembed)
        if anon == "me":
            with open('slice.json') as slice:
                slicedict = json.load(slice)
            username = ctx.message.author.name
            userid = ctx.message.author.id
            if 'users' not in slicedict:
                slicedict['users'] = []
            if userid in slicedict['users']:
                embed = discord.Embed(title="You already sent us a slice...",
                                      description=" ...but thanks for the support!",
                                      color=0xebbe23)
                await self.client.say(embed=embed)
            else:
                embed = discord.Embed(title=f"Thanks for sending the team a slice of cake, {username}!",
                                      description="This is a small act that shows us your appreciation.",
                                      color=0xebbe23)
                await self.client.say(embed=embed)
                slicedict['users'].append(userid)
                slicedict['total'] += 1
                with open('slice.json', 'w') as newslice:
                    json.dump(slicedict, newslice)
                sliceembed = discord.Embed(title=f"You got sent a slice from {username}!",
                                      description=f"Slices recieved: {str(slicedict['total'])}",
                                      color=0xebbe23)
                await self.client.send_message(discord.Object(id='466807163323416588'), embed=sliceembed)


def setup(client):
    client.add_cog(Support(client))