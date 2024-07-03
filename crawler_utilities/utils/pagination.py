import random

from discord import ButtonStyle
from itertools import zip_longest

import discord
from crawler_utilities.handlers.errors import NoSelectionElements

from discord.ext.pages import Paginator, Page, PaginatorButton

buttons = [
    PaginatorButton("first", style=ButtonStyle.primary, label="⏮"),
    PaginatorButton("prev", style=ButtonStyle.primary, label="◀"),
    PaginatorButton("page_indicator", style=ButtonStyle.gray, disabled=True),
    PaginatorButton("next", style=ButtonStyle.primary, label="▶"),
    PaginatorButton("last", style=ButtonStyle.primary, label="⏭"),
]


def paginate(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return [i for i in zip_longest(*args, fillvalue=fillvalue) if i is not None]


def createPaginator(ctx, choices, message=None, force_select=False, title="Multiple Matches Found",
                          desc="What are you looking for?\n",
                          author=False):
    if len(choices) == 0:
        raise NoSelectionElements()
    elif len(choices) == 1 and not force_select:
        return choices[0][1]

    totalPages = paginate(choices, 10)
    colour = random.randint(0, 0xffffff)
    pages = []

    for page in range(len(totalPages)):
        _choices = totalPages[page]
        names = [choice[0] for choice in _choices if choice]
        embed = discord.Embed()
        if author:
            embed.set_author(name=title)
            if ctx.author.display_avatar.url is not None:
                embed.set_author(name=title, icon_url=ctx.author.display_avatar.url)
        else:
            embed.title = title
        selectStr = desc
        for index, name in enumerate(names):
            selectStr += f"**[{index + 1 + page * 10}]** - {name}\n"
        embed.description = selectStr
        embed.colour = colour
        if message:
            embed.add_field(name="Note", value=message)
        _page = Page(embeds=[embed])
        pages.append(_page)

    return sendPaginator(pages)


def createPaginatorWithEmbeds(embeds):
    pages = []

    for embed in embeds:
        _page = Page(embeds=[embed])
        pages.append(_page)

    return sendPaginator(pages)


def sendPaginator(pages):
    paginator = Paginator(pages=pages, show_indicator=True, use_default_buttons=False, timeout=60,
                          author_check=True, custom_buttons=buttons)
    return paginator
