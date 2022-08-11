import motor.motor_asyncio
from environs import Env

from crawler_utilities.handlers.logger import Logger

log = Logger("logs", "CrawlerUtilities", "CrawlerUtilities").logger
errors = Logger("logs", "ErrorCommands", "ErrorCommands").logger

env = Env()
env.read_env()

MONGODB = env('MONGODB')
GOOGLEANALYTICSID = env('GOOGLEANALYTICSID')

HELPDB = motor.motor_asyncio.AsyncIOMotorClient(MONGODB)['lookup'].help

LOCALEFOLDER = env('LOCALEFOLDER')
LOCALIZATION = {}