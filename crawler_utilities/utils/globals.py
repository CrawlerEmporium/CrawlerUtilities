import motor.motor_asyncio
from environs import Env

env = Env()
env.read_env()

MONGODB = env('MONGODB')

HELP = motor.motor_asyncio.AsyncIOMotorClient(MONGODB)['lookup']