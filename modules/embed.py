import discord
import asyncio


def embed(title, description, url=None):
    message = discord.Embed(title=title, url=url, description=description, color=0xebbe23)
    message.set_footer(text="Request an action by reacting with the relevant emojis")
    return message


async def launch(post, ctx, bot, timeout=None, commands=None):
    message = await ctx.send(embed=post)
    if commands:
        for command in commands:
            await message.add_reaction(command)
    await message.add_reaction('🇽')

    def check(reaction, user):
        return user == ctx.message.author and (reaction.emoji == '🇽' or (reaction.emoji in commands or not command))

    try:
        reaction = await bot.wait_for('reaction_add', timeout=timeout, check=check)
    except asyncio.TimeoutError:
        await message.delete()
        await ctx.send('Function has timed out')
    if reaction[0].emoji == '🇽':
        await message.delete()
    else:
        await message.delete()
        return reaction[0].emoji
