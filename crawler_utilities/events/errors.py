import traceback
import asyncio
import random

from aiohttp import ClientResponseError, ClientOSError
from d20 import TooManyRolls, RollSyntaxError, RollValueError

from crawler_utilities.utils.embeds import ErrorEmbedWithAuthorWithoutContext
from discord import Forbidden, HTTPException, InvalidArgument, NotFound
from discord.ext import commands
from discord.ext.commands import CommandInvokeError, ExpectedClosingQuoteError, UnexpectedQuoteError, CheckFailure
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


async def sendEmbedError(ctx, description, title=None):
    embed = ErrorEmbedWithAuthorWithoutContext(ctx.message.author)
    if title is not None:
        embed.title = title
    else:
        embed.title = f"Error in command - {ctx.message.content}"
    embed.description = description
    await ctx.send(embed=embed)


async def sendEmbedSlashError(ctx, description, title=None):
    embed = ErrorEmbedWithAuthorWithoutContext(ctx.interaction.user)
    if title is not None:
        embed.title = title
    else:
        embed.title = f"Error in command - {ctx.interaction.message.content}"
    embed.description = description
    await ctx.respond(embed=embed, ephemeral=True)


async def sendAuthorEmbedError(ctx, description):
    embed = ErrorEmbedWithAuthorWithoutContext(ctx.message.author)
    embed.title = f"Error in command - {ctx.message.content}"
    embed.description = description
    await ctx.author.send(embed=embed)


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
            return await sendEmbedError(ctx, str(error))
        tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument, commands.NoPrivateMessage, ValueError)):
            return await sendEmbedError(ctx, "" + str(error) + f"\nUse `{ctx.prefix}help " + ctx.command.qualified_name + "` for help.")
        elif isinstance(error, commands.CheckFailure):
            return await sendEmbedError(ctx, "You are not allowed to run this command.")
        elif isinstance(error, commands.CommandOnCooldown):
            return await sendEmbedError(ctx, "This command is on cooldown for {:.1f} seconds.".format(error.retry_after))
        elif isinstance(error, UnexpectedQuoteError):
            return await sendEmbedError(ctx,
                                        f"You either gave me a command that requires quotes, and you forgot one.\n"
                                        f"Or you have used the characters that are used to define what's optional and required (<> and [])\n"
                                        f"Please check the ``{ctx.prefix}help`` command for proper usage of my commands.")
        elif isinstance(error, ExpectedClosingQuoteError):
            return await sendEmbedError(ctx, f"You gave me a command that requires quotes, and you forgot one at the end.")
        elif isinstance(error, CommandInvokeError):
            original = error.original
            if isinstance(original, EvaluationError):  # PM an alias author tiny traceback
                e = original.original
                if not isinstance(e, CrawlerException):
                    tb = f"```py\nwhen parsing expression {original.expression}:\n" \
                         f"{''.join(traceback.format_exception(type(e), e, e.__traceback__, limit=0, chain=False))}\n```"
                    try:
                        await sendAuthorEmbedError(ctx, tb)
                    except Exception as e:
                        log.info(f"Error sending traceback: {e}")
            if isinstance(original, CrawlerException):
                return await sendEmbedError(ctx, str(original))
            if isinstance(original, TooManyRolls):
                return await sendEmbedError(ctx, "Too many dice rolled. Maximum is a 1000 at once.")
            if isinstance(original, RollSyntaxError):
                return await sendEmbedError(ctx, f"Your dice syntax is off, please check ``{ctx.prefix}help roll`` for the correct usage of this command.\nYou used the following syntax: ``{ctx.message.content}``")
            if isinstance(original, RollValueError):
                return await sendEmbedError(ctx, f"You tried to roll a d0, with did you expect to happen?")
            if isinstance(original, Forbidden):
                try:
                    return await sendAuthorEmbedError(ctx,
                                                      f"I am missing permissions to run this command. "
                                                      f"Please make sure I have permission to send messages to <#{ctx.channel.id}>."
                                                      )
                except:
                    try:
                        return await sendEmbedError(ctx, f"Error: I cannot send messages to this user.")
                    except:
                        return
            if isinstance(original, NotFound):
                return await sendEmbedError(ctx, "I tried to edit or delete a message that doesn't exist.")
            if isinstance(original, NoSelectionElements):
                return await sendEmbedError(ctx, "There are no choices to select from.")
            if isinstance(original, ValueError) and str(original) in ("No closing quotation", "No escaped character"):
                return await sendEmbedError(ctx, "No closing quotation.")
            if isinstance(original, (ClientResponseError, InvalidArgument, asyncio.TimeoutError, ClientOSError)):
                return await sendEmbedError(ctx, "Error originated from the Discord API. Please try again.")
            if isinstance(original, HTTPException):
                if original.response.status == 400:
                    return await sendEmbedError(ctx, "Message is too long, malformed, or empty.")
                if original.response.status == 500:
                    return await sendEmbedError(ctx, "Internal server error on Discord's end. Please try again.")
                if original.response.status == 503:
                    return await sendEmbedError(ctx, "Connecting failure on Discord's end. (Service unavailable). Please check https://status.discordapp.com for the status of the Discord Service, and try again later.")
            if isinstance(original, OverflowError):
                return await sendEmbedError(ctx, f"A number is too large for me to store.")
            if isinstance(original, SearchException):
                return await sendEmbedError(ctx, f"Search Timed out, please try the command again.")
            if isinstance(original, KeyError):
                if str(original) == "'content-type'":
                    return await sendEmbedError(ctx, f"The command errored on Discord's side. I can't do anything about this, Sorry.\nPlease check https://status.discordapp.com for the status on the Discord API, and try again later.")
            if isinstance(original, CheckFailure):
                return await ctx.respond("You do not have the required permissions to use this command.", ephemeral=True)

        error_msg = self.gen_error_message()

        await sendEmbedError(ctx,
                             f"Uh oh, that wasn't supposed to happen! "
                             f"Please join the Support Discord (``{ctx.prefix}support``) and file a bug report, with the title included in the report.", error_msg)

        embed = ErrorEmbedWithAuthorWithoutContext(ctx.message.author)
        embed.title = f"Error: {error_msg}"
        try:
            embed.description = f"Channel: **{ctx.channel}** ({ctx.channel.id})\nServer: **{ctx.guild}** ({ctx.guild.id})\nUser: **{ctx.author.mention}** ({ctx.author.id})\n\n{repr(error)}"
        except:
            embed.description = f"Error in PM with **{ctx.author}** ({ctx.author.id})\n\n{repr(error)}"
        embed.add_field(name="Command Errored", value=f"{ctx.message.content}", inline=False)
        await splitDiscordEmbedField(embed, tb, "Traceback")

        await errorChannel.send(embed=embed)
        log.error("Error caused by message: `{}`".format(ctx.message.content))

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        errorChannel = await self.bot.fetch_channel(self.bot.error)
        if isinstance(error, CrawlerException):
            return await sendEmbedSlashError(ctx, str(error))
        tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument, commands.NoPrivateMessage, ValueError)):
            return await sendEmbedSlashError(ctx, "" + str(error) + f"\nUse `/help " + ctx.command.qualified_name + "` for help.")
        elif isinstance(error, commands.CheckFailure):
            return await sendEmbedSlashError(ctx, "You are not allowed to run this command.")
        elif isinstance(error, commands.CommandOnCooldown):
            return await sendEmbedSlashError(ctx, "This command is on cooldown for {:.1f} seconds.".format(error.retry_after))
        elif isinstance(error, UnexpectedQuoteError):
            return await sendEmbedSlashError(ctx,
                                             f"You either gave me a command that requires quotes, and you forgot one.\n"
                                             f"Or you have used the characters that are used to define what's optional and required (<> and [])\n"
                                             f"Please check the ``/help`` command for proper usage of my commands.")
        elif isinstance(error, ExpectedClosingQuoteError):
            return await sendEmbedSlashError(ctx, f"You gave me a command that requires quotes, and you forgot one at the end.")
        elif isinstance(error, CommandInvokeError):
            original = error.original
            if isinstance(original, EvaluationError):  # PM an alias interaction.author tiny traceback
                e = original.original
                if not isinstance(e, CrawlerException):
                    tb = f"```py\nwhen parsing expression {original.expression}:\n" \
                         f"{''.join(traceback.format_exception(type(e), e, e.__traceback__, limit=0, chain=False))}\n```"
                    try:
                        await sendAuthorEmbedError(ctx, tb)
                    except Exception as e:
                        log.info(f"Error sending traceback: {e}")
            if isinstance(original, CrawlerException):
                return await sendEmbedSlashError(ctx, str(original))
            if isinstance(original, TooManyRolls):
                return await sendEmbedSlashError(ctx, "Too many dice rolled. Maximum is a 1000 at once.")
            if isinstance(original, RollSyntaxError):
                return await sendEmbedSlashError(ctx, f"Your dice syntax is off, please check ``/help roll`` for the correct usage of this command.\nYou used the following syntax: ``{ctx.interaction.message.content}``")
            if isinstance(original, RollValueError):
                return await sendEmbedSlashError(ctx, f"You tried to roll a d0, with did you expect to happen?")
            if isinstance(original, Forbidden):
                try:
                    return await sendAuthorEmbedError(ctx,
                                                      f"I am missing permissions to run this command. "
                                                      f"Please make sure I have permission to send messages to <#{ctx.interaction.channel.id}>."
                                                      )
                except:
                    try:
                        return await sendEmbedSlashError(ctx, f"Error: I cannot send messages to this user.")
                    except:
                        return
            if isinstance(original, NotFound):
                return await sendEmbedSlashError(ctx, "I tried to edit or delete a message that doesn't exist.")
            if isinstance(original, NoSelectionElements):
                return await sendEmbedSlashError(ctx, "There are no choices to select from.")
            if isinstance(original, ValueError) and str(original) in ("No closing quotation", "No escaped character"):
                return await sendEmbedSlashError(ctx, "No closing quotation.")
            if isinstance(original, (ClientResponseError, InvalidArgument, asyncio.TimeoutError, ClientOSError)):
                return await sendEmbedSlashError(ctx, "Error originated from the Discord API. Please try again.")
            if isinstance(original, HTTPException):
                if original.response.status == 400:
                    return await sendEmbedSlashError(ctx, "Message is too long, malformed, or empty.")
                if original.response.status == 500:
                    return await sendEmbedSlashError(ctx, "Internal server error on Discord's end. Please try again.")
                if original.response.status == 503:
                    return await sendEmbedSlashError(ctx, "Connecting failure on Discord's end. (Service unavailable). Please check https://status.discordapp.com for the status of the Discord Service, and try again later.")
            if isinstance(original, OverflowError):
                return await sendEmbedSlashError(ctx, f"A number is too large for me to store.")
            if isinstance(original, SearchException):
                return await sendEmbedSlashError(ctx, f"Search Timed out, please try the command again.")
            if isinstance(original, KeyError):
                if str(original) == "'content-type'":
                    return await sendEmbedSlashError(ctx, f"The command errored on Discord's side. I can't do anything about this, Sorry.\nPlease check https://status.discordapp.com for the status on the Discord API, and try again later.")
            if isinstance(original, CheckFailure):
                return await ctx.respond("You do not have the required permissions to use this command.", ephemeral=True)

        error_msg = self.gen_error_message()

        await sendEmbedSlashError(ctx,
                                  f"Uh oh, that wasn't supposed to happen! "
                                  f"Please join the Support Discord (``/support``) and file a bug report, with the title included in the report.", error_msg)

        embed = ErrorEmbedWithAuthorWithoutContext(ctx.message.interaction.user)
        embed.title = f"Error: {error_msg}"
        try:
            embed.description = f"Channel: **{ctx.interaction.channel}** ({ctx.channel.id})\nServer: **{ctx.interaction.guild}** ({ctx.interaction.guild.id})\nUser: **{ctx.interaction.user.mention}** ({ctx.interaction.user.id})\n\n{repr(error)}"
        except:
            embed.description = f"Error in PM with **{ctx.interaction.user}** ({ctx.interaction.user.id})\n\n{repr(error)}"
        embed.add_field(name="Command Errored", value=f"{ctx.command.qualified_name}", inline=False)
        await splitDiscordEmbedField(embed, tb, "Traceback")

        await errorChannel.send(embed=embed)
        log.error("Error caused by message: `{}`".format(ctx.interaction.message.content))

    def gen_error_message(self):
        subject = random.choice(adj)
        verb = random.choice(noun)
        return f"{subject} {verb}"


def setup(bot):
    log.info("[Event] Errors...")
    bot.add_cog(Errors(bot))
