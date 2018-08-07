from discord.ext import commands
import json
import discord


class Support:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def slice(self, ctx, anon):
        if anon == "anon":
            message = "Thanks for sending the team a slice of cake, anonymous user! " \
                      "This is a small act that lets them know their work does not go unappreciated."
            await self.client.say(message)
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
            teammessage = f"You got sent a slice from anon! Slices recieved: {str(slicedict['total'])}"
            await self.client.send_message(discord.Object(id='466807163323416588'), teammessage)
        if anon == "me":
            with open('slice.json') as slice:
                slicedict = json.load(slice)
            username = ctx.message.author.name
            userid = ctx.message.author.id
            if 'users' not in slicedict:
                slicedict['users'] = []
            if userid in slicedict['users']:
                await self.client.say("You already sent us a slice, but thanks for the support!")
            else:
                message = f"Thanks for sending the team a slice of cake, {username}! " \
                           "This is a small act that lets us know our work does not go unappreciated."
                await self.client.say(message)
                slicedict['users'].append(userid)
                slicedict['total'] += 1
                with open('slice.json', 'w') as newslice:
                    json.dump(slicedict, newslice)
                teammessage = f"You got sent a slice from {username}! Slices recieved: {str(slicedict['total'])}"
                await self.client.send_message(discord.Object(id='466807163323416588'), teammessage)


def setup(client):
    client.add_cog(Support(client))
