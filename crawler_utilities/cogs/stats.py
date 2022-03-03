from datetime import datetime

import requests
import time

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
        name = self.bot.user.name
        await user_activity(ctx, name)
        await guild_activity(ctx, name)
        await command_activity(ctx, name)


async def user_activity(ctx, name):
    track_google_analytics_event(f"{name}: User", f"{ctx.command.qualified_name}", f"{ctx.author.id}")


async def guild_activity(ctx, name):
    if ctx.guild is None:
        guild_id = 0
    else:
        guild_id = ctx.guild.id
    track_google_analytics_event(f"{name}: Guild", f"{ctx.command.qualified_name}", f"{guild_id}")


async def command_activity(ctx, name):
    track_google_analytics_event(name, f"{ctx.command.qualified_name}", "")


def track_google_analytics_event(event_category, event_action, event_label):
    url = "https://www.google-analytics.com/collect"
    data = {
        "v": "1",
        "t": "event",
        "tid": GOOGLEANALYTICSID,
        "cid": str(datetime.now()),
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
