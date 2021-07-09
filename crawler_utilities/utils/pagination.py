import discord
import asyncio
from discord.ext import commands
from copy import deepcopy
from typing import List

from discord_components import Button, ButtonStyle, Interaction

from .abc import Dialog


def chunkValidIntoPages(lst, amount):
    for i in range(0, len(lst), amount):
        yield lst[i:i + amount]


def getNumberedButtons(numbers):
    pages = list(chunkValidIntoPages(numbers, 5))
    page1 = []
    page2 = []
    for x in pages[0]:
        page1.append(Button(style=ButtonStyle.blue, custom_id=f"choice {x}", label=x))
    if len(pages) > 1:
        for x in pages[1]:
            page2.append(Button(style=ButtonStyle.blue, custom_id=f"choice {x}", label=x))
        return [page1, page2]
    return [page1]


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
        self.control_labels = ("First Page", "Previous Page", "Next Page", "Last Page", "Stop")

    @property
    def formatted_pages(self):
        pages = deepcopy(self.pages)  # copy by value not reference
        for page in pages:
            if page.footer.text == discord.Embed.Empty:
                page.set_footer(text=f"Page {pages.index(page) + 1}/{len(pages)}")
            else:
                if page.footer.icon_url == discord.Embed.Empty:
                    page.set_footer(text=f"{page.footer.text} - Page {pages.index(page) + 1}/{len(pages)}")
                else:
                    page.set_footer(icon_url=page.footer.icon_url, text=f"{page.footer.text} - Page {pages.index(page) + 1}/{len(pages)}")
        return pages

    def getPaginationButtons(self, first=False, second=False, fourth=False, fifth=False):
        return [Button(style=ButtonStyle.blue, custom_id=self.control_labels[0], emoji=self.control_emojis[0], disabled=first),
                Button(style=ButtonStyle.blue, custom_id=self.control_labels[1], emoji=self.control_emojis[1], disabled=second),
                Button(style=ButtonStyle.red, custom_id=self.control_labels[4], emoji=self.control_emojis[4]),
                Button(style=ButtonStyle.blue, custom_id=self.control_labels[2], emoji=self.control_emojis[2], disabled=fourth),
                Button(style=ButtonStyle.blue, custom_id=self.control_labels[3], emoji=self.control_emojis[3], disabled=fifth)]

    async def run(self, users: List[discord.User], channel: discord.TextChannel = None, valid = None):
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

        if len(valid) > 0:
            numberedInPages = list(chunkValidIntoPages(valid, 10))
            if len(self.pages) == 1:
                buttons = getNumberedButtons(numberedInPages[0])
                buttons.append([Button(style=ButtonStyle.red, custom_id=self.control_labels[4], emoji=self.control_emojis[4])])
            else:
                buttons = getNumberedButtons(numberedInPages[0])
                buttons.append(self.getPaginationButtons(True, True, False, False))
        else:
            if len(self.pages) == 1:
                buttons = [Button(style=ButtonStyle.red, custom_id=self.control_labels[4], emoji=self.control_emojis[4])]
            else:
                buttons = [self.getPaginationButtons(True, True, False, False)]

        self.message = await channel.send(embed=self.formatted_pages[0], components=buttons)
        current_page_index = 0

        def checkB(i: Interaction):
            res = (i.message.id == self.message.id) and (i.custom_id in self.control_labels or i.custom_id.split(" ")[1] in valid)

            if len(users) > 0:
                res = res and i.user.id in [u1.id for u1 in users]

            return res

        def checkM(msg: discord.Message):
            if len(users) > 0:
                res = msg.author.id in [u1.id for u1 in users] and msg.content.lower() in valid

            return res

        click = self._client.wait_for('button_click', check=checkB, timeout=60)
        msg = self._client.wait_for('message', check=checkM, timeout=60)

        tasks = [click, msg]
        while tasks:
            try:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for x in done:
                    result = x.result()
                    if result:
                        if isinstance(result, Interaction):
                            id = result.custom_id
                            max_index = len(self.pages) - 1  # index for the last page

                            if len(valid) > 0:
                                if id == self.control_labels[0]:
                                    load_page_index = 0
                                    buttons = getNumberedButtons(numberedInPages[load_page_index])
                                    buttons.append(self.getPaginationButtons(True, True, False, False))

                                elif id == self.control_labels[1]:
                                    load_page_index = current_page_index - 1 if current_page_index > 0 else current_page_index
                                    buttons = getNumberedButtons(numberedInPages[load_page_index])
                                    if load_page_index == 0:
                                        buttons.append(self.getPaginationButtons(True, True, False, False))
                                    else:
                                        buttons.append(self.getPaginationButtons(False, False, False, False))

                                elif id == self.control_labels[2]:
                                    load_page_index = current_page_index + 1 if current_page_index < max_index else current_page_index
                                    buttons = getNumberedButtons(numberedInPages[load_page_index])
                                    if load_page_index == max_index:
                                        buttons.append(self.getPaginationButtons(False, False, True, True))
                                    else:
                                        buttons.append(self.getPaginationButtons(False, False, False, False))

                                elif id == self.control_labels[3]:
                                    load_page_index = max_index
                                    buttons = getNumberedButtons(numberedInPages[load_page_index])
                                    buttons.append(self.getPaginationButtons(False, False, True, True))

                                elif id == self.control_labels[4]:
                                    await self.message.delete()
                                    return

                                else:
                                    await self.message.delete()
                                    return id.split(" ")[1]
                            else:
                                if id == self.control_labels[0]:
                                    load_page_index = 0
                                    buttons = [self.getPaginationButtons(True, True, False, False)]

                                elif id == self.control_labels[1]:
                                    load_page_index = current_page_index - 1 if current_page_index > 0 else current_page_index
                                    if load_page_index == 0:
                                        buttons = [self.getPaginationButtons(True, True, False, False)]
                                    else:
                                        buttons = [self.getPaginationButtons(False, False, False, False)]

                                elif id == self.control_labels[2]:
                                    load_page_index = current_page_index + 1 if current_page_index < max_index else current_page_index
                                    if load_page_index == max_index:
                                        buttons = [self.getPaginationButtons(False, False, True, True)]
                                    else:
                                        buttons = [self.getPaginationButtons(False, False, False, False)]

                                elif id == self.control_labels[3]:
                                    load_page_index = max_index
                                    buttons = [self.getPaginationButtons(False, False, True, True)]

                                elif id == self.control_labels[4]:
                                    await self.message.delete()
                                    return

                                else:
                                    await self.message.delete()
                                    return id.split(" ")[1]

                            await result.respond(type=7, embed=self.formatted_pages[load_page_index], components=buttons)

                            current_page_index = load_page_index

                            for future in pending:
                                future.cancel()

                            click = self._client.wait_for('button_click', check=checkB, timeout=60)
                            msg = self._client.wait_for('message', check=checkM, timeout=60)

                            tasks = [msg, click]
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
