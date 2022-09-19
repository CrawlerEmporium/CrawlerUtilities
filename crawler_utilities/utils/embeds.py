import random

import discord


class EmbedWithAuthor(discord.Embed):
    """An embed with author image and nickname set."""

    def __init__(self, ctx, **kwargs):
        super(EmbedWithAuthor, self).__init__(**kwargs)
        name = ctx.author.nick if not None else ctx.author.display_name
        if ctx.author.display_avatar.url is not None:
            self.set_author(name=name, icon_url=ctx.author.display_avatar.url)
        else:
            self.set_author(name=name)
        self.colour = random.randint(0, 0xffffff)


class EmbedWithAuthorWithoutContext(discord.Embed):
    """An embed with author image and nickname set."""

    def __init__(self, author, **kwargs):
        super(EmbedWithAuthorWithoutContext, self).__init__(**kwargs)
        name = author.nick if not None else author.display_name
        if author.display_avatar.url is not None:
            self.set_author(name=name, icon_url=author.display_avatar.url)
        else:
            self.set_author(name=name)
        self.colour = random.randint(0, 0xffffff)

class ErrorEmbedWithAuthorWithoutContext(discord.Embed):
    """An embed with author image and nickname set."""

    def __init__(self, author, **kwargs):
        super(ErrorEmbedWithAuthorWithoutContext, self).__init__(**kwargs)
        if author.display_avatar.url is not None:
            self.set_author(name=author.display_name, icon_url=author.display_avatar.url)
        else:
            self.set_author(name=author.display_name)
        self.colour = 0xff0000


class HomebrewEmbedWithAuthor(EmbedWithAuthor):
    """An embed with author image, nickname, and homebrew footer set."""

    def __init__(self, ctx, **kwargs):
        super(HomebrewEmbedWithAuthor, self).__init__(ctx, **kwargs)
        self.set_footer(text="Homebrew content.", icon_url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/241/beer-mug_1f37a.png")
