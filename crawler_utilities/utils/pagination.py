import discord
import asyncio
from discord.ext import commands
from copy import deepcopy
from typing import List
from .abc import Dialog


class EmbedPaginator(Dialog):
    """ Represents an interactive menu containing multiple embeds. """

    def __init__(self, client: discord.Client, pages: [discord.Embed], message: discord.Message = None):
        """
        Initialize a new EmbedPaginator.

        :param client: The :class:`discord.Client` to use.
        :param pages: A list of :class:`discord.Embed` to paginate through.
        :param message: An optional :class:`discord.Message` to edit. Otherwise a new message will be sent.
        """
        super().__init__()

        self._client = client
        self.pages = pages
        self.message = message

        self.control_emojis = ("⏮", "◀", "▶", "⏭", "⏹")

    @property
    def formatted_pages(self):
        pages = deepcopy(self.pages)  # copy by value not reference
        for page in pages:
            if page.footer.text == discord.Embed.Empty:
                page.set_footer(text=f"({pages.index(page) + 1}/{len(pages)})")
            else:
                if page.footer.icon_url == discord.Embed.Empty:
                    page.set_footer(text=f"{page.footer.text} - ({pages.index(page) + 1}/{len(pages)})")
                else:
                    page.set_footer(icon_url=page.footer.icon_url, text=f"{page.footer.text} - ({pages.index(page) + 1}/{len(pages)})")
        return pages

    async def run(self, users: List[discord.User], channel: discord.TextChannel = None, valid=None):
        """
        Runs the paginator.

        :type users: List[discord.User]
        :param users:
            A list of :class:`discord.User` that can control the pagination.
            Passing an empty list will grant access to all users. (Not recommended.)

        :type channel: Optional[discord.TextChannel]
        :param channel:
            The text channel to send the embed to.
            Must only be specified if `self.message` is `None`.

        :return: None
        """
        if channel is None and self.message is not None:
            channel = self.message.channel
        elif channel is None:
            raise TypeError("Missing argument. You need to specify a target channel.")

        self._embed = self.pages[0]
        self.message = await channel.send(embed=self.formatted_pages[0])
        current_page_index = 0

        if len(self.pages) == 1:  # no pagination needed in this case
            await self.message.add_reaction(self.control_emojis[4])
        else:
            for emoji in self.control_emojis:
                await self.message.add_reaction(emoji)

        def checkR(r: discord.Reaction, u: discord.User):
            res = (r.message.id == self.message.id) and (r.emoji in self.control_emojis)

            if len(users) > 0:
                res = res and u.id in [u1.id for u1 in users]

            return res

        def checkM(msg: discord.Message):
            if len(users) > 0:
                res = msg.author.id in [u1.id for u1 in users] and msg.content.lower() in valid

            return res

        def task_complete(t):
            t.cancel()

        reaction = self._client.wait_for('reaction_add', check=checkR, timeout=60)
        msg = self._client.wait_for('message', check=checkM, timeout=60)

        tasks = [reaction, msg]
        while tasks:
            try:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for x in done:
                    result = x.result()
                    if result:
                        if isinstance(result, tuple):
                            emoji = result[0].emoji
                            user = result[1]
                            max_index = len(self.pages) - 1  # index for the last page

                            if emoji == self.control_emojis[0]:
                                load_page_index = 0

                            elif emoji == self.control_emojis[1]:
                                load_page_index = current_page_index - 1 if current_page_index > 0 else current_page_index

                            elif emoji == self.control_emojis[2]:
                                load_page_index = current_page_index + 1 if current_page_index < max_index else current_page_index

                            elif emoji == self.control_emojis[3]:
                                load_page_index = max_index

                            else:
                                await self.message.delete()
                                return

                            await self.message.edit(embed=self.formatted_pages[load_page_index])
                            if not isinstance(channel, discord.channel.DMChannel) and not isinstance(channel,
                                                                                                     discord.channel.GroupChannel):
                                await self.message.remove_reaction(emoji, user)

                            current_page_index = load_page_index

                            for future in pending:
                                future.cancel()
                            reaction = self._client.wait_for('reaction_add', check=checkR, timeout=60)
                            msg = self._client.wait_for('message', check=checkM, timeout=60)

                            tasks = [msg, reaction]
                        elif isinstance(result, discord.message.Message):
                            await self.message.delete()
                            try:
                                await result.delete()
                            except:
                                pass
                            for future in pending:
                                future.cancel()
                            return result.content
            except asyncio.TimeoutError:
                if not isinstance(channel, discord.channel.DMChannel) and not isinstance(channel,
                                                                                         discord.channel.GroupChannel):
                    await self.message.clear_reactions()
                    await self.message.delete()
                else:
                    await self.message.delete()
                return

    @staticmethod
    def generate_sub_lists(l: list) -> [list]:
        if len(l) > 25:
            sub_lists = []

            while len(l) > 20:
                sub_lists.append(l[:20])
                del l[:20]

            sub_lists.append(l)

        else:
            sub_lists = [l]

        return sub_lists


class BotEmbedPaginator(EmbedPaginator):
    def __init__(self, ctx: commands.Context, pages: [discord.Embed], message: discord.Message = None):
        """
        Initialize a new EmbedPaginator.

        :param ctx: The :class:`discord.ext.commands.Context` to use.
        :param pages: A list of :class:`discord.Embed` to paginate through.
        :param message: An optional :class:`discord.Message` to edit. Otherwise a new message will be sent.
        """
        self._ctx = ctx

        super(BotEmbedPaginator, self).__init__(ctx.bot, pages, message)

    async def run(self, channel: discord.TextChannel = None, users: List[discord.User] = None, valid=None):
        """
        Runs the paginator.

        :type channel: Optional[discord.TextChannel]
        :param channel:
            The text channel to send the embed to.
            Default is the context channel.

        :type users: Optional[List[discord.User]]
        :param users:
            A list of :class:`discord.User` that can control the pagination.
            Default is the context author.
            Passing an empty list will grant access to all users. (Not recommended.)

        :return: None
        """

        if users is None:
            users = [self._ctx.author]

        if self.message is None and channel is None:
            channel = self._ctx.channel

        if valid is None:
            valid = []

        m = await super().run(users, channel, valid)
        return m
