from datetime import datetime

import requests
import time

from discord.ext import commands

import crawler_utilities.utils.globals as GG
from crawler_utilities.utils.functions import get_uuid4_from_user_id
from crawler_utilities.utils.globals import GOOGLEANALYTICSID
from faker import Faker

log = GG.log


class CommandStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.monotonic()

    @commands.Cog.listener()
    async def on_command(self, ctx):
        bot_name = self.bot.user.name
        author = ctx.author.id
        if ctx.guild is None:
            guild = 0
        else:
            guild = ctx.guild.id
        client_id = get_uuid4_from_user_id(author)
        command = ctx.command.qualified_name
        await user_activity(bot_name, command, author, client_id)
        await guild_activity(bot_name, command, guild, client_id)
        await command_activity(bot_name, command, client_id)
        try:
            log.info(
                "cmd: chan {0.message.channel} ({0.message.channel.id}), serv {0.message.guild} ({0.message.guild.id}), "
                "auth {0.message.author} ({0.message.author.id}): {0.message.content}".format(
                    ctx))
        except AttributeError:
            log.info("Command in PM with {0.message.author} ({0.message.author.id}): {0.message.content}".format(ctx))

    @commands.Cog.listener()
    async def on_application_command(self, ctx):
        bot_name = self.bot.user.name
        author = ctx.interaction.user.id
        if ctx.interaction.guild_id is None:
            guild = 0
        else:
            guild = ctx.interaction.guild_id
        client_id = get_uuid4_from_user_id(author)
        command = ctx.command.qualified_name
        await user_activity(bot_name, command, author, client_id)
        await guild_activity(bot_name, command, guild, client_id)
        await command_activity(bot_name, command, client_id)
        try:
            log.info(
                "slash: chan {0.channel} ({0.channel_id}), serv {0.guild} ({0.guild_id}), "
                "auth {0.user} ({0.user.id}): {1}".format(
                    ctx.interaction, command))
        except AttributeError:
            log.info("Command in PM with {0.user} ({0.user.id}): {1}".format(ctx.interaction, command))


async def user_activity(bot_name, command, author, client_id):
    await track_analytics_event(bot_name, f"User", f"{command}", f"{author}", client_id)


async def guild_activity(bot_name, command, guild, client_id):
    await track_analytics_event(bot_name, f"Guild", f"{command}", f"{guild}", client_id)


async def command_activity(bot_name, command, client_id):
    await track_analytics_event(bot_name, "Command", f"{command}", "", client_id)


async def track_analytics_event(bot_name, event_category, event_action, event_label, client=None):
    """
    :param bot_name: Bot Name
    :param event_category: Event Category
    :param event_action: Event Action
    :param event_label: Event Label
    :param client: Specific Client Id for the Events
    """
    if client is None:
        faker = Faker()
        client = faker.uuid4()
    if isinstance(event_label, str):
        event_label = event_label.lower()
    await GG.STATSDB[f'{bot_name}'].insert_one({"event": event_category, "action": event_action, "label": event_label, "client": client})


async def track_analytics_event_values(event_category, event_action, event_value, client=None):
    """
    :param event_category: Event Category
    :param event_action: Event Action
    :param event_value: Event Value
    :param client: Specific Client Id for the Events
    """
    if client is None:
        client = str(datetime.now())
    if isinstance(event_value, str):
        event_value = event_value.lower()
    await GG.STATSDB['5eCrawler'].insert_one({"event": event_category, "action": event_action, "value": event_value, "client": client})



def setup(bot):
    log.info("[Cogs] Stats...")
    bot.add_cog(CommandStats(bot))
