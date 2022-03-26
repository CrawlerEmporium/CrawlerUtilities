import motor.motor_asyncio
from environs import Env

env = Env()
env.read_env()

MONGODB = env('MONGODB')
GOOGLEANALYTICSID = env('GOOGLEANALYTICSID')

HELPDB = motor.motor_asyncio.AsyncIOMotorClient(MONGODB)['lookup'].help

LOCALEFOLDER = env('LOCALEFOLDER')
LOCALIZATION = {}