from aiohttp import web
from discord.ext import commands, tasks
from crawler_utilities.handlers import logger

log = logger.logger


class Flare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.web_server.start()
        self.app = web.Application()
        self.routes = web.RouteTableDef()

        @self.routes.get("/")
        async def welcome(request):
            return web.Response(text=f"{self.bot.user.name} is Online!!")

        self.app.add_routes(self.routes)

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host=None, port=self.bot.port)
        await site.start()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()


def setup(bot):
    log.info("[Cogs] Flare...")
    bot.add_cog(Flare(bot))
