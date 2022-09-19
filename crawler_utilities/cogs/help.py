import asyncio

import discord
from discord.ext import commands, tasks

from crawler_utilities.utils.embeds import ErrorEmbedWithAuthorWithoutContext
import crawler_utilities.utils.globals as GG
from discord.ui import Button, View
from discord import ButtonStyle, Option, slash_command

from crawler_utilities.utils.globals import HELPDB

log = GG.log

ID = {"CommunityCrawler": "discord", "5eCrawler": "5e", "5eCrawler.Nightly": "5e", "IssueCrawler": "issue"}


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reload_task.start()
        self.commands = []

    async def get_help(self, ctx: discord.AutocompleteContext):
        return [command['command'] for command in self.commands if ctx.value.lower() in command['command'].lower()]

    @tasks.loop(hours=1)
    async def reload_task(self):
        await self.bot.wait_until_ready()
        log.info("[IN-MEMORY] Help commands")
        identifier = ID.get(self.bot.user.name)
        self.commands = await HELPDB.find({"bots": identifier, "disabled": None}).to_list(length=None)

    @slash_command(name="help")
    async def help(self, ctx, command: Option(str, "For which command do you want to see the help menu?", autocomplete=get_help)):
        """Get more information about the commands this bot has"""
        await self.getCommandHelp(ctx, command)

    @slash_command(name="commands")
    @commands.has_permissions(administrator=True)
    async def commands(self, ctx):
        """Gets the list of all commands with the integration ID attached."""
        sB = "```\n"
        for command in self.bot.walk_application_commands():
            sB += f"{command.qualified_name}:{command.id}\n"
        sB += "```"
        await ctx.respond(sB)

    async def getCommandHelp(self, ctx, commandName):
        helpCommand = next(command for command in self.commands if command['command'] == commandName)
        prefix = '/'
        if helpCommand is not None and not helpCommand.get('disabled', False):
            description = helpCommand['description'][0]
            embed = discord.Embed(title=f"{helpCommand['command'].title()}",
                                  description=f"{description.replace('{/prefix}', prefix)}")

            if helpCommand.get('syntax', None) is not None:
                if len(helpCommand['syntax']) > 1:
                    for i in range(len(helpCommand['syntax'])):
                        embed.add_field(name=f"Syntax {i + 1}",
                                        value=f"{helpCommand['syntax'][i].replace('{/prefix}', prefix)}", inline=False)
                else:
                    embed.add_field(name=f"Syntax", value=f"{helpCommand['syntax'][0].replace('{/prefix}', prefix)}",
                                    inline=False)

            if helpCommand.get('aliasFor', None) is not None:
                aliasString = ', '.join(helpCommand['aliasFor'])
                embed.add_field(name=f"Aliases", value=f"{aliasString.replace('{/prefix}', prefix)}", inline=False)

            if helpCommand.get('options', None) is not None:
                if len(helpCommand['options']) > 1:
                    for i in range(len(helpCommand['options'])):
                        entryString = '\n'.join(helpCommand['options'][i]['entries'])
                        embed.add_field(name=f"Option: {helpCommand['options'][i]['argument']}",
                                        value=f"{entryString.replace('{/prefix}', prefix)}",
                                        inline=False)
                else:
                    entryString = '\n'.join(helpCommand['options'][0]['entries'])
                    embed.add_field(name=f"Option: {helpCommand['options'][0]['argument']}",
                                    value=f"{entryString.replace('{/prefix}', prefix)}",
                                    inline=False)

            if helpCommand.get('examples', None) is not None:
                if len(helpCommand['examples']) > 1:
                    exampleString = "\n".join(helpCommand['examples'])
                    embed.add_field(name=f"Examples",
                                    value=f"{exampleString.replace('{/prefix}', prefix)}",
                                    inline=False)
                else:
                    embed.add_field(name=f"Example", value=f"{helpCommand['examples'][0].replace('{/prefix}', prefix)}",
                                    inline=False)

            typeString = ", ".join(helpCommand['types'])
            embed.add_field(name=f"Types", value=f"{typeString}", inline=False)

            permString = "Permissions: "
            permString += ", ".join(helpCommand['permissions'])
            embed.set_footer(text=permString)
            return await ctx.respond(embed=embed)
        else:
            return await ctx.respond(f"I'm sorry, I couldn't find the help page for ``{commandName}``\nTry again later, or notify the bot developer through the support server.")


def setup(bot):
    log.info("[Cogs] Help...")
    bot.add_cog(Help(bot))
