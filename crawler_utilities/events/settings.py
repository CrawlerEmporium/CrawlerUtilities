import discord.ui.view
from discord import ButtonStyle, Interaction
from discord.ui import Button

from crawler_utilities.utils.embeds import EmbedWithAuthorWithoutContext
from discord.ext import commands
from crawler_utilities.handlers import logger
from crawler_utilities.utils.functions import get_positivity

log = logger.logger

active = "(<:active:851743586583052329> Active)"
inactive = "(<:inactive:851743586654748672> Inactive)"

fivee = 559331529378103317
debug = 500280860965077012
issue = 602779023151595546

settingsTrue = ['-allow_selfClose True', '-allow_milestoneAdding True', '-req_dm_monster True', '-pm_dm True', '-pm_result True', '-rem_commands True', '-rem_rolls True', '-ping_rolls True']
settingsFalse = ['-allow_selfClose False', '-allow_milestoneAdding False', '-req_dm_monster False', '-pm_dm False', '-pm_result False', '-rem_commands False', '-rem_rolls False', '-ping_rolls False']


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, res: Interaction):
        member = await res.guild.fetch_member(res.user.id)
        if member is not None and (res.data['custom_id'] in settingsTrue or res.data['custom_id'] in settingsFalse):
            if member.guild_permissions.administrator:
                guild_settings = await self.bot.settings.find_one({"server": res.guild.id})
                if guild_settings is None:
                    guild_settings = {}

                splitCustomId = res.data['custom_id'].split(" ")
                splitArg = (splitCustomId[0], splitCustomId[1])

                if res.message.author.id == fivee or res.message.author.id == debug:
                    loopedSettings = loopThrough5eSettings(guild_settings, splitArg)
                elif res.message.author.id == issue:
                    loopedSettings = loopThroughIssueSettings(guild_settings, splitArg)

                await self.bot.settings.update_one({"server": str(res.guild.id)}, {"$set": loopedSettings}, upsert=True)
                guild_settings = await self.bot.settings.find_one({"server": str(res.guild.id)})

                if res.message.author.id == fivee or res.message.author.id == debug:
                    embed = get5eSettingsEmbed(guild_settings, res.message.author)
                    buttons = get5eSettingsButtons(guild_settings)
                elif res.message.author.id == issue:
                    embed = getIssueSettingsEmbed(guild_settings, res.message.author)
                    buttons = getIssueSettingsButtons(guild_settings)
                await res.message.edit(embed=embed, view=buttons)
                await res.response.defer()
            else:
                await res.response.send_message(content="You need 'Administrator' permissions to change settings on this server.")


def getIssueSettingsEmbed(settings, author):
    embed = EmbedWithAuthorWithoutContext(author)
    embed.title = "IssueCrawler settings for this server."

    selfClose = active if settings.get('allow_selfClose', False) else inactive
    milestoneAdding = active if settings.get('allow_milestoneAdding', False) else inactive

    reportString = '🔒 Allow people to close their own requests/bugs: {}\n'.format(str(selfClose))
    milestoneString = '🐛 Allow people to add requests/bugs directly to milestones: {}\n'.format(str(milestoneAdding))

    embed.add_field(name="Report Settings", value=reportString, inline=False)
    embed.add_field(name="Milestone Settings", value=milestoneString, inline=False)

    embed.set_footer(text="Click the buttons below to change the status from active to inactive, or vice versa")

    return embed


def get5eSettingsEmbed(settings, author):
    embed = EmbedWithAuthorWithoutContext(author)
    embed.title = "5eCrawler settings for this server."

    monster = active if settings.get('req_dm_monster', True) else inactive
    dm = active if settings.get('pm_dm', False) else inactive
    result = active if settings.get('pm_result', False) else inactive
    commands = active if settings.get('rem_commands', False) else inactive
    rolls = active if settings.get('rem_rolls', True) else inactive
    pingsRolls = active if settings.get('ping_rolls', True) else inactive

    lookupString = '👺 Requires a Game Master role to show a full monster stat block: {}\n\n'.format(monster)
    lookupString += '✉️ Direct Messages a Game Master the full monster stat block instead of outputting to chat, if the setting above is Active: {}\n\n'.format(str(dm))
    lookupString += '📥 Direct Messages the result of the all lookup commands to reduce spam: {}\n\n'.format(str(result))

    commandString = '❌ Removes the commands from chat. (Except roll commands): {}\n\n'.format(str(commands))
    commandString += '🎲 Removes the roll commands from chat: {}\n\n'.format(str(rolls))
    commandString += '🔔 Pings the user on the response after the rolling commands.: {}\n\n'.format(str(pingsRolls))

    embed.add_field(name="Lookup Settings", value=f"{lookupString}\n", inline=False)
    embed.add_field(name="Command Settings", value=commandString, inline=False)

    embed.set_footer(text="Click the buttons below to change the status from active to inactive, or vice versa")

    return embed


def getIssueSettingsButtons(settings):
    close = Button(style=ButtonStyle.success, custom_id="-allow_selfClose False", row=0) if settings.get('allow_selfClose', True) else Button(style=ButtonStyle.danger, custom_id="-allow_selfClose True", row=0)
    milestone = Button(style=ButtonStyle.success, custom_id="-allow_milestoneAdding False", row=1) if settings.get('allow_milestoneAdding', False) else Button(style=ButtonStyle.danger, custom_id="-allow_milestoneAdding True", row=1)

    close.label = "Self Close"
    close.emoji = "🔒"

    milestone.label = "Add to Milestone"
    milestone.emoji = "🐛"

    view = discord.ui.view.View()
    for x in [close, milestone]:
        view.add_item(x)

    return view


def get5eSettingsButtons(settings):
    monster = Button(style=ButtonStyle.success, custom_id="-req_dm_monster False", row=0) if settings.get('req_dm_monster', True) else Button(style=ButtonStyle.danger, custom_id="-req_dm_monster True", row=0)
    dm = Button(style=ButtonStyle.success, custom_id="-pm_dm False", row=0) if settings.get('pm_dm', False) else Button(style=ButtonStyle.danger, custom_id="-pm_dm True", row=0)
    result = Button(style=ButtonStyle.success, custom_id="-pm_result False", row=0) if settings.get('pm_result', False) else Button(style=ButtonStyle.danger, custom_id="-pm_result True", row=0)
    commands = Button(style=ButtonStyle.success, custom_id="-rem_commands False", row=1) if settings.get('rem_commands', False) else Button(style=ButtonStyle.danger, custom_id="-rem_commands True", row=1)
    rolls = Button(style=ButtonStyle.success, custom_id="-rem_rolls False", row=1) if settings.get('rem_rolls', True) else Button(style=ButtonStyle.danger, custom_id="-rem_rolls True", row=1)
    pingsRolls = Button(style=ButtonStyle.success, custom_id="-ping_rolls False", row=1) if settings.get('ping_rolls', True) else Button(style=ButtonStyle.danger, custom_id="-ping_rolls True", row=1)

    monster.label = "Monster Block"
    monster.emoji = "👺"

    dm.label = "PM DM Results"
    dm.emoji = "✉️"

    result.label = "PM Result"
    result.emoji = "📥"

    commands.label = "Remove Commands"
    commands.emoji = "✖️"

    rolls.label = "Remove Rolls"
    rolls.emoji = "🎲"

    pingsRolls.label = "Ping Rolls"
    pingsRolls.emoji = "🔔"

    view = discord.ui.view.View()
    for x in [monster, dm, result, commands, rolls, pingsRolls]:
        view.add_item(x)

    return view


def loopThroughIssueSettings(guild_settings, args):
    if '-allow_selfClose' in args:
        try:
            setting = args[args.index('-allow_selfClose') + 1]
        except IndexError:
            setting = 'True'
        setting = get_positivity(setting)
        guild_settings['allow_selfClose'] = setting if setting is not None else True
    if '-allow_milestoneAdding' in args:
        try:
            setting = args[args.index('-allow_milestoneAdding') + 1]
        except IndexError:
            setting = 'True'
        setting = get_positivity(setting)
        guild_settings['allow_milestoneAdding'] = setting if setting is not None else True
    return guild_settings


def loopThrough5eSettings(guild_settings, args):
    if '-req_dm_monster' in args:
        try:
            setting = args[args.index('-req_dm_monster') + 1]
        except IndexError:
            setting = 'True'
        setting = get_positivity(setting)
        guild_settings['req_dm_monster'] = setting if setting is not None else True
    if '-pm_dm' in args:
        try:
            setting = args[args.index('-pm_dm') + 1]
        except IndexError:
            setting = 'True'
        setting = get_positivity(setting)
        guild_settings['pm_dm'] = setting if setting is not None else True
    if '-pm_result' in args:
        try:
            setting = args[args.index('-pm_result') + 1]
        except IndexError:
            setting = 'False'
        setting = get_positivity(setting)
        guild_settings['pm_result'] = setting if setting is not None else False
    if '-rem_commands' in args:
        try:
            setting = args[args.index('-rem_commands') + 1]
        except IndexError:
            setting = 'False'
        setting = get_positivity(setting)
        guild_settings['rem_commands'] = setting if setting is not None else False
    if '-rem_rolls' in args:
        try:
            setting = args[args.index('-rem_rolls') + 1]
        except IndexError:
            setting = 'False'
        setting = get_positivity(setting)
        guild_settings['rem_rolls'] = setting if setting is not None else True
    if '-ping_rolls' in args:
        try:
            setting = args[args.index('-ping_rolls') + 1]
        except IndexError:
            setting = 'False'
        setting = get_positivity(setting)
        guild_settings['ping_rolls'] = setting if setting is not None else True
    return guild_settings


def setup(bot):
    log.info("[Event] Settings...")
    bot.add_cog(Settings(bot))
