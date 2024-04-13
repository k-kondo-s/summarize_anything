import logging
import os
import sys

import discord
from dotenv import load_dotenv

from executor import ExecutorBuilder


# https://github.com/Rapptz/discord.py/discussions/9726#discussioncomment-8416217
class GatewayEventFilter(logging.Filter):
    def __init__(self) -> None:
        super().__init__("discord.gateway")

    def filter(self, record: logging.LogRecord) -> bool:
        if record.exc_info is not None and isinstance(
            record.exc_info[1], discord.ConnectionClosed
        ):
            return False
        return True


logging.getLogger("discord.gateway").addFilter(GatewayEventFilter())
logging.basicConfig(level=logging.INFO, stream=sys.stdout)  # ログを標準出力に出す
logger = logging.getLogger(__name__)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

DISCORD_ALLOWED_CHANNEL_ID_LIST: list[int] = [
    int(i) for i in os.getenv("DISCORD_ALLOWED_CHANNEL_ID_LIST").split(",")
]
print(DISCORD_ALLOWED_CHANNEL_ID_LIST)
DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN")

executor = ExecutorBuilder.build()
simple_executor = ExecutorBuilder.build_simple()


@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    logger.info(f"Received message: {message.clean_content}")

    # メンションされたらOKを返す
    if client.user in message.mentions:
        try:
            result_text = simple_executor.execute(message.clean_content)
            logger.info(f"SimpleExecutor result text: {result_text}")
            if result_text:
                await message.reply(result_text)
        except discord.errors.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            await message.reply(f"Error occurred. Details:\n{e.args}")

    # 投稿を勝手に拾う
    elif message.channel.id in DISCORD_ALLOWED_CHANNEL_ID_LIST:
        try:
            result_text = executor.execute(message.clean_content)
            logger.info(f"Executor result text: {result_text}")
            if result_text:
                await message.reply(result_text)
        except discord.errors.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            await message.reply(f"Error occurred. Details:\n{e.args}")


client.run(DISCORD_BOT_TOKEN)
