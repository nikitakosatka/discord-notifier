import discord


class Client(discord.Client):
    def __init__(self, config, message_handler):
        super().__init__()
        self._config = config
        self._handler = message_handler
        self.running = False

    async def start(self, *args, **kwargs):
        self.running = True
        await super().start(*args, **kwargs)

    async def close(self):
        self.running = False
        await super().close()

    async def on_message(self, message):
        if message.author.name == self._config["target nick"]:
            await self._handler(message)
