import json
import crawler_utilities.utils.globals as GG
from os import listdir
from os.path import join, isfile
from discord.ext import commands
log = GG.log


class Localization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        for file in listdir(GG.LOCALEFOLDER):
            if isfile(join(GG.LOCALEFOLDER, file)):
                locale = file.replace('.json', '')
                jsonFile = json.loads(open(GG.LOCALEFOLDER + "/" + file, "r", encoding="UTF-8").read())
                for key in jsonFile:
                    value = jsonFile[key]
                    keySplit = key.split(".")
                    cog, command, _type = "", "", ""

                    if len(keySplit) == 3:
                        cog = keySplit[0]
                        command = keySplit[1]
                        _type = keySplit[2]

                    if len(keySplit) == 4:
                        cog = keySplit[0]
                        command = f"{keySplit[1]}.{keySplit[2]}"
                        _type = keySplit[3]

                    if GG.LOCALIZATION.get(cog, None) is not None:
                        cog = GG.LOCALIZATION.get(cog)
                        if cog.get(_type, None) is not None:
                            if cog.get(_type).get(command, None) is not None:
                                cog[_type][command][locale] = value
                            else:
                                cog[_type][command] = {
                                    f"{locale}": value
                                }
                        else:
                            cog[_type] = {
                                f"{command}": {
                                    f"{locale}": value
                                }
                            }
                    else:
                        GG.LOCALIZATION[cog] = {
                            f"{_type}": {
                                f"{command}": {
                                    f"{locale}": value
                                }
                            }
                        }


def setup(bot):
    log.info("[Cog] Localization")
    bot.add_cog(Localization(bot))


def get_default_name(cogName, command):
    return GG.LOCALIZATION[cogName]['name'][command]['en-US']


def get_default_description(cogName, command):
    return GG.LOCALIZATION[cogName]['description'][command]['en-US']


def get_localized_names(cogName, command):
    return GG.LOCALIZATION[cogName]['name'][command]


def get_localized_descriptions(cogName, command):
    return GG.LOCALIZATION[cogName]['description'][command]


def get_command_kwargs(cogName, name):
    return {
        "name": get_default_name(cogName, name),
        "description": get_default_description(cogName, name),
        "name_localizations": get_localized_names(cogName, name),
        "description_localizations": get_localized_descriptions(cogName, name)
    }


def get_parameter_kwargs(cogName, name):
    return {
        "description": get_default_description(cogName, name),
        "name_localizations": get_localized_names(cogName, name),
        "description_localizations": get_localized_descriptions(cogName, name)
    }
