"""
This module contains the logic for formatting and sending embeds, and executing
commands based on emoji reactions.
"""
import asyncio
import copy
import discord


class Embed:
    def __init__(self, title, description, bot, ctx=None, url=None):
        message = discord.Embed(title=title,
                                url=url,
                                description=description,
                                color=0xebbe23)
        message.set_footer(
            text="Request an action by reacting with the relevant emojis")
        self.message = message
        self.ctx = ctx
        self.bot = bot
        self.grouped_list = None
        self.message_list = None

    def prepare(self, result_list):
        """
        Creating a new message and entry chunk for every 9 entries in a list of
        results, and adding a field to each message for every entry associated
        with that message.

        Example (this may be message 0):

        Were these the colours you were looking for?
        Entry #1
        Maroon
        Entry #2
        Shartruce
        ...
        Entry #9
        Mustard
        """
        def chunks(entry_list, size):
            """For chunking entry lists when they go over 9, due to emoji digit
            constraints."""
            for i in range(0, len(entry_list), size):
                yield entry_list[i:i + size]
        self.grouped_list = [x for x in chunks(result_list, 9)]
        self.message_list = []
        for entry_group in self.grouped_list:
            new_message = copy.copy(self.message)
            for entry in entry_group:
                # insert indexes start at 0 joke
                place = entry_group.index(entry) + 1
                new_message.add_field(name=f"Entry #{place}",
                                      value=entry,
                                      inline=False)
            self.message_list.append(new_message)

    async def launch_controls(self, message_index, timeout=None):
        """Only meant to be used in launch_special() loop"""
        current_message = self.message_list[message_index]
        current_chunk = self.grouped_list[message_index]
        discord_post = await self.ctx.send(embed=current_message)
        command_list = [f'{current_chunk.index(entry)+1}\u20e3'
                        for entry in current_chunk]
        for command in command_list:
            await discord_post.add_reaction(command)
        if message_index > 0:
            await discord_post.add_reaction('⬅')
        if message_index < len(self.message_list) - 1:
            await discord_post.add_reaction('➡')
        await discord_post.add_reaction('🇽')

        def check(reaction, user):
            """3 boolean checks for valid emoji, same user, and same post"""
            emoji_bool = reaction.emoji in ['🇽', '➡', '⬅'] \
                        or (reaction.emoji in command_list)
            user_bool = user == self.ctx.message.author
            post_bool = reaction.message.id == discord_post.id
            return emoji_bool and user_bool and post_bool
        try:
            reaction = await self.bot.wait_for('reaction_add',
                                               timeout=timeout,
                                               check=check)
        except asyncio.TimeoutError:
            await discord_post.delete()
            await self.ctx.send('Function has timed out')
        else:
            await discord_post.delete()
            return reaction[0].emoji

    async def launch_special(self):
        """Using left and right arrow emojis to navigate entry chunks. Breaks
        if close emoji. Returns entry index emoji if picked."""
        chunk_index = 0
        while True:
            launched_emoji = await self.launch_controls(chunk_index,
                                                        timeout=60.0)
            if not launched_emoji:
                break
            if launched_emoji == '⬅':
                chunk_index = int(chunk_index - 1)
            elif launched_emoji == '➡':
                chunk_index = int(chunk_index + 1)
            else:
                return chunk_index, launched_emoji

    async def launch_normal(self):
        """For user requested embeds that don't require an entry list"""
        discord_post = await self.ctx.send(embed=self.message)
        await discord_post.add_reaction('🇽')

        def check(reaction, user):
            emoji_bool = reaction.emoji == '🇽'
            user_bool = user == self.ctx.message.author
            post_bool = reaction.message.id == discord_post.id
            return emoji_bool and user_bool and post_bool
        try:
            await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await discord_post.delete()
            error = Embed("Error",
                          "Function has timed out.",
                          self.bot,
                          self.ctx)
            await error.launch_normal()
        else:
            await discord_post.delete()

    # async def launchstoregame(self, timeout=None):
