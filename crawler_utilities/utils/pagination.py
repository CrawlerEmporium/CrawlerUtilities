from discord.ext import pages
from itertools import zip_longest

import discord
import asyncio

from discord.ext import commands
from copy import deepcopy
from typing import List

from discord.interactions import Interaction
from discord import ButtonStyle
from discord.ui import Button

from .abc import Dialog
from ..handlers.errors import NoSelectionElements
import random


def chunkValidIntoPages(lst, amount):
    for i in range(0, len(lst), amount):
        yield lst[i:i + amount]


def getNumberedButtons(numbers):
    view = discord.ui.View()
    pages = list(chunkValidIntoPages(numbers, 5))
    for x in pages[0]:
        view.add_item(Button(style=ButtonStyle.primary, custom_id=f"choice {x}", label=x, row=0))
    if len(pages) > 1:
        for x in pages[1]:
            view.add_item(Button(style=ButtonStyle.primary, custom_id=f"choice {x}", label=x, row=1))
        return view, 1
    return view, 0


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

    def getPaginationButtons(self, view, row, first=False, second=False, fourth=False, fifth=False):
        view.add_item(Button(style=ButtonStyle.primary, custom_id=self.control_labels[0], emoji=self.control_emojis[0], disabled=first, row=row))
        view.add_item(Button(style=ButtonStyle.primary, custom_id=self.control_labels[1], emoji=self.control_emojis[1], disabled=second, row=row))
        view.add_item(Button(style=ButtonStyle.danger, custom_id=self.control_labels[4], emoji=self.control_emojis[4], row=row))
        view.add_item(Button(style=ButtonStyle.primary, custom_id=self.control_labels[2], emoji=self.control_emojis[2], disabled=fourth, row=row))
        view.add_item(Button(style=ButtonStyle.primary, custom_id=self.control_labels[3], emoji=self.control_emojis[3], disabled=fifth, row=row))
        return view

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

        if len(valid) > 0:
            numberedInPages = list(chunkValidIntoPages(valid, 10))
            if len(self.pages) == 1:
                view, row = getNumberedButtons(numberedInPages[0])
                row += 1
                view.add_item(Button(style=ButtonStyle.danger, custom_id=self.control_labels[4], emoji=self.control_emojis[4], row=row))
            else:
                view, row = getNumberedButtons(numberedInPages[0])
                row += 1
                view = self.getPaginationButtons(view, row, True, True, False, False)
        else:
            if len(self.pages) == 1:
                view = discord.ui.View()
                view.add_item(Button(style=ButtonStyle.danger, custom_id=self.control_labels[4], emoji=self.control_emojis[4], row=0))
            else:
                view = discord.ui.View()
                view = self.getPaginationButtons(view, 0, True, True, False, False)

        self.message = await channel.send(embed=self.formatted_pages[0], view=view)
        current_page_index = 0

        def checkB(i: Interaction):
            interactionId = i.message.id
            messageId = self.message.id
            userId = i.user.id
            res = (interactionId == messageId) and (i.data['custom_id'] in self.control_labels or i.data['custom_id'].split(" ")[1] in valid)

            if len(users) > 0:
                res = res and userId in [u1.id for u1 in users]

            return res

        def checkM(msg: discord.Message):
            if len(users) > 0:
                res = msg.author.id in [u1.id for u1 in users] and msg.content.lower() in valid

            return res

        click = self._client.wait_for('interaction', check=checkB, timeout=60)
        msg = self._client.wait_for('message', check=checkM, timeout=60)

        tasks = [click, msg]
        while tasks:
            try:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for x in done:
                    result = x.result()
                    if result:
                        if isinstance(result, Interaction):
                            id = result.data['custom_id']
                            max_index = len(self.pages) - 1  # index for the last page

                            if len(valid) > 0:
                                if id == self.control_labels[0]:
                                    load_page_index = 0
                                    view, row = getNumberedButtons(numberedInPages[load_page_index])
                                    row += 1
                                    view = self.getPaginationButtons(view, row, True, True, False, False)

                                elif id == self.control_labels[1]:
                                    load_page_index = current_page_index - 1 if current_page_index > 0 else current_page_index
                                    view, row = getNumberedButtons(numberedInPages[load_page_index])
                                    row += 1
                                    if load_page_index == 0:
                                        view = self.getPaginationButtons(view, row, True, True, False, False)
                                    else:
                                        view = self.getPaginationButtons(view, row, False, False, False, False)

                                elif id == self.control_labels[2]:
                                    load_page_index = current_page_index + 1 if current_page_index < max_index else current_page_index
                                    view, row = getNumberedButtons(numberedInPages[load_page_index])
                                    row += 1
                                    if load_page_index == max_index:
                                        view = self.getPaginationButtons(view, row, False, False, True, True)
                                    else:
                                        view = self.getPaginationButtons(view, row, False, False, False, False)

                                elif id == self.control_labels[3]:
                                    load_page_index = max_index
                                    view, row = getNumberedButtons(numberedInPages[load_page_index])
                                    row += 1
                                    view = self.getPaginationButtons(view, row, False, False, True, True)

                                elif id == self.control_labels[4]:
                                    await self.message.delete()
                                    return

                                else:
                                    await self.message.delete()
                                    return id.split(" ")[1]
                            else:
                                view = discord.ui.View()
                                if id == self.control_labels[0]:
                                    load_page_index = 0
                                    view = self.getPaginationButtons(view, 0, True, True, False, False)

                                elif id == self.control_labels[1]:
                                    load_page_index = current_page_index - 1 if current_page_index > 0 else current_page_index
                                    if load_page_index == 0:
                                        view = self.getPaginationButtons(view, 0, True, True, False, False)
                                    else:
                                        view = self.getPaginationButtons(view, 0, False, False, False, False)

                                elif id == self.control_labels[2]:
                                    load_page_index = current_page_index + 1 if current_page_index < max_index else current_page_index
                                    if load_page_index == max_index:
                                        view = self.getPaginationButtons(view, 0, False, False, True, True)
                                    else:
                                        view = self.getPaginationButtons(view, 0, False, False, False, False)

                                elif id == self.control_labels[3]:
                                    load_page_index = max_index
                                    view = self.getPaginationButtons(view, 0, False, False, True, True)

                                elif id == self.control_labels[4]:
                                    await self.message.delete()
                                    return

                                else:
                                    await self.message.delete()
                                    return id.split(" ")[1]

                            await result.response.pong()
                            await result.edit_original_message(embed=self.formatted_pages[load_page_index], view=view)

                            current_page_index = load_page_index

                            for future in pending:
                                future.cancel()

                            click = self._client.wait_for('interaction', check=checkB, timeout=60)
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


def paginate(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return [i for i in zip_longest(*args, fillvalue=fillvalue) if i is not None]


async def get_selection(ctx,
                        choices,
                        message=None,
                        force_select=False,
                        title="Multiple Matches Found",
                        desc="Which one were you looking for? (Type the number or press ⏹ to cancel)\n",
                        author=False):
    """Returns the selected choice, or None. Choices should be a list of two-tuples of (name, choice).
    If delete is True, will delete the selection message and the response.
    If length of choices is 1, will return the only choice.
    :raises NoSelectionElements if len(choices) is 0.
    :raises SelectionCancelled if selection is cancelled."""
    if len(choices) == 0:
        raise NoSelectionElements()
    elif len(choices) == 1 and not force_select:
        return choices[0][1]

    page = 0
    pages = paginate(choices, 10)
    m = None
    selectMsg = None
    colour = random.randint(0, 0xffffff)
    embeds = []

    for x in range(len(pages)):
        _choices = pages[x]
        names = [o[0] for o in _choices if o]
        embed = discord.Embed()
        if author:
            if ctx.author.display_avatar.url is not None:
                embed.set_author(name=title, icon_url=ctx.author.display_avatar.url)
            else:
                embed.set_author(name=title)
        else:
            embed.title = title
        selectStr = desc
        for i, r in enumerate(names):
            selectStr += f"**[{i + 1 + x * 10}]** - {r}\n"
        embed.description = selectStr
        embed.colour = colour
        if message:
            embed.add_field(name="Note", value=message)
        embeds.append(embed)

    if selectMsg:
        try:
            await selectMsg.delete()
        except:
            pass

    valid = [str(v) for v in range(1, len(choices) + 1)]

    paginator = BotEmbedPaginator(ctx, embeds)
    m = await paginator.run(valid=valid)

    if m is not None:
        return choices[int(m) - 1][1]
    else:
        return None
