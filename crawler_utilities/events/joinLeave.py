import asyncio

import discord
from discord import Colour
from discord.ext import commands
from crawler_utilities.handlers import logger

log = logger.logger

class JoinLeave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        tracker = await self.bot.fetch_channel(self.bot.tracking)
        embed = discord.Embed(color=Colour.green())
        embed.title = f"Joined Server"
        embed.description = f"{guild}"
        if self.bot.user.id != 559331529378103317:
            bots = sum(1 for m in guild.members if m.bot)
            members = len(guild.members)
            embed.add_field(name="Members", value=f"{members - bots}")
            embed.add_field(name="Bots", value=f"{bots}")
            embed.add_field(name="** **", value="** **")
        embed.add_field(name="Owner", value=f"{guild.owner}")
        embed.add_field(name="Mention", value=f"{guild.owner.mention}")
        embed.add_field(name="Id", value=f"{guild.owner.id}")
        embed.set_footer(text=f"{guild.id}")
        await tracker.send(embed=embed)
        await self.bot.change_presence(activity=discord.Game(f"with {len(self.bot.guilds)} servers | {self.bot.defaultPrefix}help | v{self.bot.version}"), afk=True)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        tracker = await self.bot.fetch_channel(self.bot.tracking)
        embed = discord.Embed(color=Colour.red())
        embed.title = f"Left Server"
        embed.description = f"{guild}"
        if self.bot.user.id != 559331529378103317:
            bots = sum(1 for m in guild.members if m.bot)
            members = len(guild.members)
            embed.add_field(name="Members", value=f"{members - bots}")
            embed.add_field(name="Bots", value=f"{bots}")
            embed.add_field(name="** **", value="** **")
        embed.add_field(name="Owner", value=f"{guild.owner}")
        embed.add_field(name="Mention", value=f"{guild.owner.mention}")
        embed.add_field(name="Id", value=f"{guild.owner.id}")
        embed.set_footer(text=f"{guild.id}")
        await tracker.send(embed=embed)
        await self.bot.change_presence(activity=discord.Game(f"with {len(self.bot.guilds)} servers | {self.bot.defaultPrefix}help | v{self.bot.version}"), afk=True)


def setup(bot):
    log.info("[Event] Join and Leave Logging...")
    bot.add_cog(JoinLeave(bot))
