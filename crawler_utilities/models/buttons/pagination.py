from discord.ui import View


class Pagination(View):
    def __init__(self, buttons):
        super().__init__(timeout=None)
        i = 0
        for row in buttons:
            for button in row:
                button.row = i
                self.add_item(button)
            i += 1

    async def on_timeout(self):
        pass
