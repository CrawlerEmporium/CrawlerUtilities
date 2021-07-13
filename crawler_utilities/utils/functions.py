import re
import discord


async def try_delete(message):
    try:
        await message.delete()
    except discord.HTTPException:
        pass


def make_ordinal(n):
    '''
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'
    '''
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix


def a_or_an(string, upper=False):
    if string.startswith('^') or string.endswith('^'):
        return string.strip('^')
    if re.match('[AEIOUaeiou].*', string):
        return 'an {0}'.format(string) if not upper else f'An {string}'
    return 'a {0}'.format(string) if not upper else f'A {string}'


def camel_to_title(string):
    return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', string).title()


def discord_trim(string):
    result = []
    trimLen = 0
    lastLen = 0
    while trimLen <= len(string):
        trimLen += 1999
        result.append(string[lastLen:trimLen])
        lastLen += 1999
    return result


def fakeField(embed):
    embed.add_field(name="** **", value="** **")


def get_positivity(string):
    if isinstance(string, bool):  # oi!
        return string
    lowered = string.lower()
    if lowered in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
        return True
    elif lowered in ('no', 'n', 'false', 'f', '0', 'disable', 'off'):
        return False
    else:
        return None


async def splitDiscordEmbedField(embed, input, embed_field_name):
    texts = []
    amount = 1024
    while len(input) > 1024:
        next_text = input[:amount]
        if next_text.rfind("**\n```") != -1:
            tableCheck = next_text.rindex("**\n```")
            last_space = next_text.rfind("\n```\n", tableCheck)
            input = input[last_space + 1:]
            next_text = next_text[:last_space]
            texts.append(next_text)
        else:
            last_space = next_text.rfind(" ")
            input = "…" + input[last_space + 1:]
            next_text = next_text[:last_space] + "…"
            texts.append(next_text)
    texts.append(input)
    embed.add_field(name=embed_field_name, value=texts[0], inline=False)
    for piece in texts[1:]:
        embed.add_field(name="** **", value=piece, inline=False)


async def safeEmbed(embed_queue, title, desc, color):
    if len(desc) < 1024:
        embed_queue[-1].add_field(name=title, value=desc, inline=False)
    elif len(desc) < 4096:
        embed = discord.Embed(colour=color, title=title)
        await splitDiscordEmbedField(embed, desc, title)
        embed_queue.append(embed)
    else:
        embed_queue.append(discord.Embed(colour=color, title=title))
        texts = []
        while len(desc) > 2040:
            next_text = desc[:2040]
            last_space = next_text.rfind(" ")
            desc = "…" + desc[last_space + 1:]
            next_text = next_text[:last_space] + "…"
            texts.append(next_text)
        texts.append(desc)
        embed_queue[-1].description = texts[0]
        for t in texts[1:]:
            embed = discord.Embed(colour=color)
            await splitDiscordEmbedField(embed, t, "** **")
            embed_queue.append(embed)


def cutStringInPieces(input):
    n = 900
    output = [input[i:i + n] for i in range(0, len(input), n)]
    return output


def cutListInPieces(input):
    n = 30
    output = [input[i:i + n] for i in range(0, len(input), n)]
    return output


def countChannels(channels):
    channelCount = 0
    voiceCount = 0
    for x in channels:
        if type(x) is discord.TextChannel:
            channelCount += 1
        elif type(x) is discord.VoiceChannel:
            voiceCount += 1
        else:
            pass
    return channelCount, voiceCount


def get_server_prefix(self, msg):
    return self.get_prefix(self, msg)[-1]


async def get_next_num(properties, keyName):
    reportNum = await properties.find_one({'key': keyName})
    num = reportNum['amount'] + 1
    reportNum['amount'] += 1
    await properties.replace_one({"key": keyName}, reportNum)
    return f"{num}"
