import locale

import logging

import aiogram
from aiogram.utils.markdown import text, bold, italic
import discord

from .config import Config
from .discord_client import Client
from secret_key import *

logging.basicConfig(level=logging.DEBUG)

try:
    locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")
except locale.Error:
    pass

config = Config()
bot = aiogram.Bot(secret_key)
disp = aiogram.Dispatcher(bot)


async def on_message(message):
    await bot.send_message(
        chat_id, text(
            bold(config["target nick"]),
            " | ",
            message.guild.name,
            italic("#" + message.channel.name),
            " | 🕐 ",
            message.created_at.strftime("%H:%M, %d %b %Y"),
            "\n\n",
            message.content
        ),
        parse_mode=aiogram.types.ParseMode.MARKDOWN
    )


client = Client(config, on_message)


@disp.message_handler(commands=["start"])
async def start(message):
    global chat_id
    chat_id = message.chat.id

    ready = True

    if "token" not in config:
        await bot.send_message(
            message.chat.id,
            f"""Программе необходим ваш т. н. \"токен\" для работы.
            
  1. Откройте Discord на ПК.
  2. Выполните вход, если еще не выполнили.
  3. Нажмите Ctrl+Shift+I.
  4. Перейдите на вкладку {italic('Network')} и нажмите F5. Discord перезагрузится.
  5. Введите в поле {italic('Filter')} запрос "/api/v6". Найдите строку {italic('messages')} и нажмите на неё.
  6. В разделе {italic('Request headers')} найдите поле {bold('authorization')}. 
     Скопируйте последовательность символов после {bold('authorization: ')}.
  7. Отправьте сюда сообщение вида "/token {italic('скопированное')}".""",
            parse_mode=aiogram.types.ParseMode.MARKDOWN
        )
        ready = False
    if "target nick" not in config:
        await bot.send_message(
            message.chat.id,
            f"Пожалуйста, укажите имя отслеживаемого пользователя командой \"/target {italic('имя')}\".",
            parse_mode=aiogram.types.ParseMode.MARKDOWN
        )
        ready = False

    if not ready:
        await bot.send_message(message.chat.id, "После настройки отправьте /start для запуска.")
        return

    try:
        await bot.send_message(message.chat.id, "\U0001F7E2 Наблюдение начато.")
        await client.start(config["token"], bot=False)
    except RuntimeError:
        await bot.send_message(message.chat.id, "\u2139 Наблюдение уже ведется.")
    except discord.LoginFailure:
        await bot.send_message(
            message.chat.id,
            "\u26A0 Был передан неверный токен. Пожалуйста, попробуйте указать его командой /token ещё раз."
        )
        del config["token"]
    except discord.GatewayNotFound:
        await bot.send_message(
            message.chat.id,
            "\u26A0 Не удалось подключиться к API Discord. Возможно, у них проблемы с серверами.\n"
            "Попробуйте отправить /start ещё раз через некоторое время.\n\n"
            "https://status.discordapp.com/ - посмотреть статус серверов Discord"
        )


@disp.message_handler(commands=["stop"])
async def stop(message):
    await client.close()
    await bot.send_message(message.chat.id, "\U0001F534 Наблюдение остановлено.")


@disp.message_handler(commands=["token"])
async def token_handler(message):
    config["token"] = message.text.split()[1]
    await bot.send_message(message.chat.id, "\u2705 Токен установлен.")


@disp.message_handler(commands=["target"])
async def nickname_handler(message):
    config["target nick"] = ' '.join(message.text.split()[1:]).strip()
    await bot.send_message(message.chat.id, "\u2705 Имя отслеживаемого установлено.")


@disp.message_handler(commands=["status"])
async def status(message):
    if client.running:
        await bot.send_message(
            message.chat.id,
            f"\U0001F7E2 Наблюдение {bold('ведется')}.",
            parse_mode=aiogram.types.ParseMode.MARKDOWN)
    else:
        await bot.send_message(
            message.chat.id,
            f"\U0001F534 Наблюдение {bold('не ведется')}.",
            parse_mode=aiogram.types.ParseMode.MARKDOWN
        )


@disp.message_handler(commands=["showconfig"])
async def show_config(message):
    await bot.send_message(
        message.chat.id,
        bold('Токен: ') + (config.get("token", bold('не задан'))) + "\n"
        + bold('Отслеживаемый пользователь: ') + (config.get("target nick", bold('не задан'))),
        parse_mode=aiogram.types.ParseMode.MARKDOWN
    )


@disp.message_handler(commands=["help"])
async def bot_help(message):
    await bot.send_message(
        message.chat.id,
        f"""Команды:
/start: начать наблюдение
/stop: остановить наблюдение
/status: проверить, идет ли наблюдение
/token {italic('токен')}: задать токен
/target {italic('имя')}: задать отслеживаемого пользователя
/showconfig: показать текущие настройки""",
        parse_mode=aiogram.types.ParseMode.MARKDOWN
    )


aiogram.executor.start_polling(disp)
