from datetime import datetime

import requests
import time
from discord import InteractionType

from discord.ext import commands

from crawler_utilities.handlers import logger
from crawler_utilities.utils.globals import GOOGLEANALYTICSID

log = logger.logger


class CommandStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.monotonic()

    @commands.Cog.listener()
    async def on_command(self, ctx):
        bot_name = self.bot.user.name
        author = ctx.author.id
        if ctx.guild.id is None:
            guild = 0
        else:
            guild = ctx.guild.id
        client_id = str(datetime.now())
        command = ctx.command.qualified_name
        await user_activity(bot_name, command, author, client_id)
        await guild_activity(bot_name, command, guild, client_id)
        await command_activity(bot_name, command, client_id)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.type != InteractionType.application_command:
            return

        bot_name = self.bot.user.name
        author = interaction.user.id
        if interaction.guild_id is None:
            guild = 0
        else:
            guild = interaction.guild_id
        command = interaction.data.get('name')
        client_id = str(datetime.now())
        await user_activity(bot_name, command, author, client_id)
        await guild_activity(bot_name, command, guild, client_id)
        await command_activity(bot_name, command, client_id)


async def user_activity(bot_name, command, author, client_id):
    track_google_analytics_event(f"{bot_name}: User", f"{command}", f"{author}", client_id)


async def guild_activity(bot_name, command, guild, client_id):
    track_google_analytics_event(f"{bot_name}: Guild", f"{command}", f"{guild}", client_id)


async def command_activity(bot_name, command, client_id):
    track_google_analytics_event(bot_name, f"{command}", "", client_id)


def track_google_analytics_event(event_category, event_action, event_label, client=None):
    """
    Track an event to Google Analytics
    :param event_category: Event Category
    :param event_action: Event Action
    :param event_label: Event Label
    :param client: Specific Client Id for the Events
    """
    if client is None:
        client = str(datetime.now())
    url = "https://www.google-analytics.com/collect"
    data = {
        "v": "1",
        "t": "event",
        "tid": GOOGLEANALYTICSID,
        "cid": client,
        "ec": event_category,
        "ea": event_action,
        "el": event_label,
        "aip": "1"
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
        'cache-control': "no-cache"
    }
    requests.post(url, params=data, headers=headers)


def setup(bot):
    log.info("[Cogs] Stats...")
    bot.add_cog(CommandStats(bot))