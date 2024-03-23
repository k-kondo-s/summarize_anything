import logging
import os
import sys

import discord
from dotenv import load_dotenv

from executor import ExecutorBuilder

# https://github.com/Rapptz/discord.py/discussions/9726#discussioncomment-8416217
# class GatewayEventFilter(logging.Filter):
#     def __init__(self) -> None:
#         super().__init__("discord.gateway")

#     def filter(self, record: logging.LogRecord) -> bool:
#         if record.exc_info is not None and isinstance(record.exc_info[1], discord.ConnectionClosed):
#             return False
#         return True


# logging.getLogger("discord.gateway").addFilter(GatewayEventFilter())
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

DISCORD_ALLOWED_CHANNEL_ID: int = int(os.getenv("DISCORD_ALLOWED_CHANNEL_ID"))
DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN")

executor = ExecutorBuilder.build()


@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id == DISCORD_ALLOWED_CHANNEL_ID:
        logger.info(f"Received message: {message.clean_content}")
        executor_result = executor.execute(message.clean_content)
        logger.info(f"Executor result: {executor_result}")
        if executor_result:
            await message.reply(executor_result)


client.run(DISCORD_BOT_TOKEN)
