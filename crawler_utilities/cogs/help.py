import discord
from discord.ext import commands

from crawler_utilities.utils.embeds import ErrorEmbedWithAuthorWithoutContext
from crawler_utilities.handlers import logger
from discord.ui import Button, View
from discord import ButtonStyle, Option, slash_command

from crawler_utilities.utils.globals import HELPDB

log = logger.logger

ID = {"CommunityCrawler": "discord", "5eCrawler": "5e", "5eCrawler.Nightly": "5e", "IssueCrawler": "issue"}


async def get_help(ctx: discord.AutocompleteContext):
    identifier = ID.get(ctx.bot.user.name)
    helpCommands = await HELPDB.find({"bots": identifier, "disabled": None}).to_list(length=None)
    return [helpC['command'] for helpC in helpCommands if ctx.value.lower() in helpC['command'].lower()]


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def helpCommand(self, ctx):
        identifier = ID.get(self.bot.user.name)
        embed = ErrorEmbedWithAuthorWithoutContext(ctx.author)
        embed.title = "This help command was moved to a slash command."
        embed.description = f"Try the new slash commands through ``/help``\n" \
                            "Join the 5eCrawler Support server by clicking the button below or contact LordDusk#0001 for more info.\n\n\n"
        embed.add_field(name="Why?", value="The reason for this change can be found on the [Discord blogpost](https://support-dev.discord.com/hc/en-us/articles/4404772028055-Message-Content-Privileged-Intent-for-Verified-Bots)", inline=False)
        embed.add_field(name="TL;DR", value="Discord is stopping bots from using prefixed commands (like !help), and forcing bot developers to start using slash commands.\n" \
                                            "This change will take effect from April onwards. And to get people used to this change, I decided I would deprecate the most used commands already.\n" \
                                            "Note that this is not something for just 5eCrawler, but for most of the bots on discord.", inline=False)
        embed.add_field(name="For Server owners", value="Some servers may not have slash commands enabled for the bot yet, you can reinvite the bot with the reinvite button below", inline=False)
        serverEmoji = self.bot.get_emoji(int("<:5e:603932658820448267>".split(":")[2].replace(">", "")))
        view = View()
        view.add_item(Button(label="Support server", style=ButtonStyle.url, emoji=serverEmoji, url="https://discord.gg/HEY6BWj"))
        if identifier == "discord":
            view.add_item(Button(label="Re-invite me", style=ButtonStyle.url, emoji=serverEmoji, url="https://discordapp.com/oauth2/authorize?client_id=602774912595263490&scope=bot%20applications.commands&permissions=295010692176"))
        elif identifier == "issue":
            view.add_item(Button(label="Re-invite me", style=ButtonStyle.url, emoji=serverEmoji, url="https://discordapp.com/oauth2/authorize?client_id=602779023151595546&scope=bot%20applications.commands&permissions=295010692176"))
        elif identifier == "5e":
            view.add_item(Button(label="Re-invite me", style=ButtonStyle.url, emoji=serverEmoji, url="https://discordapp.com/oauth2/authorize?client_id=559331529378103317&scope=bot%20applications.commands&permissions=295010692176"))
        await ctx.send(embed=embed, view=view, delete_after=120)

    @slash_command(name="help")
    async def help(self, ctx, command: Option(str, "For which command do you want to see the help menu?", autocomplete=get_help)):
        """Get more information about the commands this bot has"""
        identifier = ID.get(self.bot.user.name)
        await getCommandHelp(ctx, command, identifier)


async def getCommandHelp(ctx, command, identifier):

    helpCommand = await HELPDB.find_one({"bots": identifier, "command": command})
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
        return await ctx.respond(f"I'm sorry, I couldn't find the help page for ``{command}``\nTry again later, or notify the bot developer through the support server.")


def setup(bot):
    log.info("[Cogs] Help...")
    bot.add_cog(Help(bot))
