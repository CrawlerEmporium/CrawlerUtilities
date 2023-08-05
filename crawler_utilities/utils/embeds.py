import random

import discord


class EmbedWithRandomColor(discord.Embed):
    def __init__(self, **kwargs):
        super(EmbedWithRandomColor, self).__init__(**kwargs)
        self.colour = random.randint(0, 0xffffff)


class ErrorEmbedWithAuthorWithoutContext(discord.Embed):
    """An embed with author image and nickname set."""

    def __init__(self, **kwargs):
        super(ErrorEmbedWithAuthorWithoutContext, self).__init__(**kwargs)
        self.colour = 0xff0000


class HomebrewEmbedWithRandomColor(EmbedWithRandomColor):
    """An embed with author image, nickname, and homebrew footer set."""

    def __init__(self, **kwargs):
        super(HomebrewEmbedWithRandomColor, self).__init__(**kwargs)
        self.set_footer(text="Homebrew content.",
                        icon_url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/241/beer-mug_1f37a.png")
