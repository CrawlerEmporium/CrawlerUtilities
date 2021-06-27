import traceback

import asyncio
import random

from aiohttp import ClientResponseError, ClientOSError
from crawler_utilities.utils.embeds import ErrorEmbedWithAuthorWithoutContext
from discord import Forbidden, HTTPException, InvalidArgument, NotFound
from discord.ext import commands
from discord.ext.commands import CommandInvokeError, ExpectedClosingQuoteError, UnexpectedQuoteError
from crawler_utilities.handlers.errors import CrawlerException, InvalidArgument, EvaluationError, NoSelectionElements
from crawler_utilities.handlers import logger
from crawler_utilities.utils.functions import splitDiscordEmbedField

log = logger.logger

adj = ['Lonely', 'Unceasing', 'Overused', 'Blue', 'Orange', 'Tiny', 'Giant', 'Deadly', 'Hopeless', 'Unknown',
       'Defeated', 'Deafening', 'Tenacious', 'Evasive', 'Omniscient', 'Wild', 'Toxic', 'Spotless', 'Impossible',
       'Faded', 'Hemorrhaging', 'Godless', 'Judicious', 'Despondent', 'Fatal', 'Serene', 'Blistering', 'Last', 'Dull',
       'Gruesome', 'Azure', 'Blighted', 'Pink', 'Languid', 'Outlawed', 'Penultimate', 'Sundered', 'Hollow', 'Violent',
       'Divine', 'Pious', 'Shattered', 'Shrouded', 'Decaying', 'Defeated', 'Callous', 'Inferior', 'Superior', 'Clear',
       'Veiled', 'Weeping', 'Swift', 'Unceasing', 'Vengeful', 'Lone', 'Cold', 'Hot', 'Purple', 'Brutal', 'Flying',
       'Driving', 'Blind', 'Demon', 'Enduring', 'Defiant', 'Lost', 'Dying', 'Falling', 'Soaring', 'Twisted', 'Glass',
       'Bleeding', 'Broken', 'Silent', 'Red', 'Black', 'Dark', 'Fallen', 'Patient', 'Burning', 'Final', 'Lazy',
       'Morbid', 'Crimson', 'Cursed', 'Frozen', 'Bloody', 'Banished', 'First', 'Severed', 'Empty', 'Spectral', 'Sacred',
       'Stone', 'Shattered', 'Hidden', 'Rotting', 'Devil\'s', 'Forgotten', 'Blinding', 'Fading', 'Crystal', 'Secret',
       'Cryptic', 'Smoking', 'Heaving', 'Steaming', 'Righteous', 'Purple', 'Amber', 'Wailing', 'Cosmic', 'Foolish',
       'Brooding', 'Failing', 'Gasping', 'Starving', 'Sinking', 'Holy', 'Unholy', 'Potent', 'Haunting', 'Pungent',
       'Golden', 'Iron', 'Shackled', 'Laughing', 'Damned', 'Poisoned', 'Half-eaten', 'Summoned', 'Gilded', 'Manic',
       'Precious', 'Outer', 'Little', 'Choking', 'Half-dead', 'Steely', 'Massive', 'Dismal', 'Rebel', 'Dread',
       'Sleeping', 'Magic', 'Dripping', 'Faceless', 'Shambling', 'Furious', 'Dead Man\'s', 'Perilous', 'Heavy',
       'Ancient', 'Jagged', 'Northern', 'Earthly', 'Hellish', 'Hellborn', 'Blessed', 'Buried', 'Senseless',
       'Blood-Soaked', 'Sweaty', 'Drunken', 'Scattered']
noun = ['Nightmare', 'Shark', 'Song', 'Soul', 'Harbinger', 'Rule', 'Lightning', 'Cavern', 'Chill', 'Dread', 'Ace',
        'Prophet', 'Seer', 'Armor', 'Failure', 'King', 'Rose', 'Kingdom', 'Circle', 'Autumn', 'Winter', 'Mercenary',
        'Devil', 'Hope', 'Carrier', 'Plague', 'Retribution', 'Ocean', 'Dagger', 'Spear', 'Peak', 'Trial', 'Redundancy',
        'Flicker', 'Speck', 'Meditation', 'Elegy', 'Graveyard', 'Righteousness', 'Bridge', 'Steam', 'Epidemic',
        'Infestation', 'Infection', 'Court', 'Scourge', 'Pommel', 'Sweater', 'Pestilence', 'Teardrop', 'Pandemic',
        'Corner', 'Emperor', 'Fool', 'Monk', 'Warrior', 'Hammer', 'Shelter', 'Chant', 'Guard', 'Sentiment', 'Straggler',
        'Bulwark', 'Defense', 'Corpse', 'Buffoon', 'Cadaver', 'Bastard', 'Skeleton', 'Concubine', 'Palace', 'Precipice',
        'Typhoon', 'Hurricaine', 'Quake', 'Death', 'Engine', 'Chant', 'Heart', 'Justice', 'Law', 'Thunder', 'Moon',
        'Heat', 'Fear', 'Star', 'Apollo', 'Prophet', 'Hero', 'Hydra', 'Serpent', 'Crown', 'Thorn', 'Empire', 'Summer',
        'Druid', 'God', 'Savior', 'Stallion', 'Hawk', 'Vengeance', 'Calm', 'Knife', 'Sword', 'Dream', 'Sleep', 'Stroke',
        'Flame', 'Spark', 'Fist', 'Dirge', 'Grave', 'Shroud', 'Breath', 'Smoke', 'Giant', 'Whisper', 'Night', 'Throne',
        'Pipe', 'Blade', 'Daze', 'Pyre', 'Tears', 'Mother', 'Crone', 'King', 'Father', 'Priest', 'Dawn', 'Hammer',
        'Shield', 'Hymn', 'Vanguard', 'Sentinel', 'Stranger', 'Bell', 'Mist', 'Fog', 'Jester', 'Scepter', 'Ring',
        'Skull', 'Paramour', 'Palace', 'Mountain', 'Rain', 'Gaze', 'Future', 'Gift', 'Grin', 'Omen', 'Tome', 'Wail',
        'Shriek', 'Glove', 'Gears', 'Slumber', 'Beast', 'Wolf', 'Widow', 'Witch', 'Prince', 'Skies', 'Dance', 'Spear',
        'Key', 'Fog', 'Feast', 'Cry', 'Claw', 'Peak', 'Valley', 'Shadow', 'Rhyme', 'Moan', 'Wheel', 'Doom', 'Mask',
        'Rose', 'Gods', 'Whale', 'Saga', 'Sky', 'Chalice', 'Agony', 'Misery', 'Tears', 'Rage', 'Anger', 'Laughter',
        'Terror', 'Gasp', 'Tongue', 'Cobra', 'Snake', 'Cavern', 'Corpse', 'Prophecy', 'Vagabond', 'Altar', 'Death',
        'Reckoning', 'Dragon', 'Doom', 'Shadow', 'Night', 'Witch', 'Steel', 'Fire', 'Blood', 'God', 'Demon', 'War',
        'Hammer', 'Star', 'Iron', 'Spider', 'Ice', 'Knife', 'Mountain', 'Death', 'Diamond', 'Frost', 'Moon', 'Swamp',
        'Ghost', 'Sky', 'Dawn', 'Storm', 'Tomb', 'Crypt', 'Bone', 'Hell', 'Winter', 'Wolf', 'Fall', 'Fist', 'Storm',
        'Blade', 'Star', 'Hammer', 'Witch', 'Dragon', 'Fire', 'Wheel', 'Tooth', 'Hound', 'Hand', 'Hawk', 'God',
        'Father', 'Mother', 'Knife', 'Giant', 'Steed', 'Strike', 'Slap', 'Killer', 'Mask', 'Walk', 'Fort', 'Tower',
        'Face', 'Tomb', 'Valley', 'Claw', 'King', 'Queen', 'Beast', 'Saga', 'Song', 'Chalice', 'Walker', 'Breaker',
        'Wagon', 'Shield', 'Shadow', 'Dance', 'Hole', 'Stank', 'Shriek', 'Child', 'Prince', 'Slayer', 'Briar', 'Castle']


class SearchException(Exception):
    pass


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        errorChannel = await self.bot.fetch_channel(self.bot.error)
        if isinstance(error, commands.CommandNotFound):
            return
        log.debug("Error caused by message: `{}`".format(ctx.message.content))
        log.debug('\n'.join(traceback.format_exception(type(error), error, error.__traceback__)))
        if isinstance(error, CrawlerException):
            return await ctx.send(str(error))
        tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        if isinstance(error,
                      (commands.MissingRequiredArgument, commands.BadArgument, commands.NoPrivateMessage, ValueError)):
            return await ctx.send("Error: " + str(
                error) + f"\nUse `{ctx.prefix}help " + ctx.command.qualified_name + "` for help.")
        elif isinstance(error, commands.CheckFailure):
            return await ctx.send("Error: You are not allowed to run this command.")
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send("This command is on cooldown for {:.1f} seconds.".format(error.retry_after))
        elif isinstance(error, UnexpectedQuoteError):
            return await ctx.send(
                f"Error: You either gave me a command that requires quotes, and you forgot one.\n"
                f"Or you have used the characters that are used to define what's optional and required (<> and [])\n"
                f"Please check the ``{ctx.prefix}help`` command for proper usage of my commands.")
        elif isinstance(error, ExpectedClosingQuoteError):
            return await ctx.send(
                f"Error: You gave me a command that requires quotes, and you forgot one at the end.")
        elif isinstance(error, CommandInvokeError):
            original = error.original
            if isinstance(original, EvaluationError):  # PM an alias author tiny traceback
                e = original.original
                if not isinstance(e, CrawlerException):
                    tb = f"```py\nError when parsing expression {original.expression}:\n" \
                         f"{''.join(traceback.format_exception(type(e), e, e.__traceback__, limit=0, chain=False))}\n```"
                    try:
                        await ctx.author.send(tb)
                    except Exception as e:
                        log.info(f"Error sending traceback: {e}")
            if isinstance(original, CrawlerException):
                return await ctx.send(str(original))
            if isinstance(original, Forbidden):
                try:
                    return await ctx.author.send(
                        f"Error: I am missing permissions to run this command. "
                        f"Please make sure I have permission to send messages to <#{ctx.channel.id}>."
                    )
                except:
                    try:
                        return await ctx.send(f"Error: I cannot send messages to this user.")
                    except:
                        return
            if isinstance(original, NotFound):
                return await ctx.send("Error: I tried to edit or delete a message that no longer exists.")
            if isinstance(original, NoSelectionElements):
                return await ctx.send("Error: There are no choices to select from.")
            if isinstance(original, ValueError) and str(original) in ("No closing quotation", "No escaped character"):
                return await ctx.send("Error: No closing quotation.")
            if isinstance(original, (ClientResponseError, InvalidArgument, asyncio.TimeoutError, ClientOSError)):
                return await ctx.send("Error in Discord API. Please try again.")
            if isinstance(original, HTTPException):
                if original.response.status == 400:
                    return await ctx.send("Error: Message is too long, malformed, or empty.")
                if original.response.status == 500:
                    return await ctx.send("Error: Internal server error on Discord's end. Please try again.")
                if original.response.status == 503:
                    return await ctx.send("Error: Connecting failure on Discord's end. (Service unavailable). Please check https://status.discordapp.com for the status of the Discord Service, and try again later.")
            if isinstance(original, OverflowError):
                return await ctx.send(f"Error: A number is too large for me to store.")
            if isinstance(original, SearchException):
                return await ctx.send(f"Search Timed out, please try the command again.")
            if isinstance(original, KeyError):
                if str(original) == "'content-type'":
                    return await ctx.send(
                        f"The command errored on Discord's side. I can't do anything about this, Sorry.\nPlease check https://status.discordapp.com for the status on the Discord API, and try again later.")

        error_msg = self.gen_error_message()

        await ctx.send(
            f"Error: {str(error)}\nUh oh, that wasn't supposed to happen! "
            f"Please join the Support Discord ({ctx.prefix}support) and tell the developer that: **{error_msg}!**")

        embed = ErrorEmbedWithAuthorWithoutContext(ctx.message.author)
        embed.title = f"Error: {error_msg}"
        try:
            embed.description = f"Error in channel: **{ctx.channel}** ({ctx.channel.id})\nserver: **{ctx.guild}** ({ctx.guild.id})\n\n{repr(error)}"
        except:
            embed.description = f"Error in PM with **{ctx.author}** ({ctx.author.id})\n\n{repr(error)}"
        embed.add_field(name="Command Errored", value=f"{ctx.message.content}", inline=False)
        await splitDiscordEmbedField(embed, tb, "Traceback")

        await errorChannel.send(embed=embed)
        log.error("Error caused by message: `{}`".format(ctx.message.content))

    def gen_error_message(self):
        subject = random.choice(adj)
        verb = random.choice(noun)
        return f"{subject} {verb}"


def setup(bot):
    log.info("[Event] Errors...")
    bot.add_cog(Errors(bot))