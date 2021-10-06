import heroku3
from pyrogram import filters
from bot import app, OWNER_ID, bot

from functools import wraps
from bot import HEROKU_API_KEY, HEROKU_APP_NAME
from bot.helper.telegram_helper.bot_commands import BotCommands

heroku_client = heroku3.from_key(HEROKU_API_KEY) if HEROKU_API_KEY else None

def check_heroku(func):
    @wraps(func)
    async def heroku_cli(client, message):
        heroku_app = None
        if not heroku_client:
            await message.reply_text("`Please add HEROKU_API_KEY for this function to work!`", parse_mode="markdown")
        elif not HEROKU_APP_NAME:
            await message.reply_text("`Please add HEROKU_APP_NAME for this function to work!`", parse_mode="markdown")
        if HEROKU_APP_NAME and heroku_client:
            try:
                heroku_app = heroku_client.app(HEROKU_APP_NAME)
            except:
                await message.reply_text(message, "`Heroku API Key & App Name Don't Match!`", parse_mode="markdown")
            if heroku_app:
                await func(client, message, heroku_app)

    return heroku_cli

# Implemented By https://github.com/jusidama18
# Based on https://github.com/DevsExpo/FridayUserbot/blob/master/plugins/heroku_helpers.py

@app.on_message(filters.command([BotCommands.RebootCommand, f'{BotCommands.RebootCommand}@{bot.username}']) & filters.user(OWNER_ID))
@check_heroku
async def restart(client, message, hap):
    msg_ = await message.reply_text("**[HEROKU] - Restarting**\n\n**NOTE: Use the /ping command in a minute to check it's status.**")
    hap.restart()

@app.on_message(filters.command([BotCommands.ShutDownCommand, f'{BotCommands.ShutDownCommand}@{bot.username}']) & filters.user(OWNER_ID))
@check_heroku
async def shutdown(client, message, app_):
    msg_ = await message.reply_text("**[HEROKU] - Shutdown**\n\n**NOTE: You'll have to manually scale the dyno to use the bot again.**")
    app_.process_formation()["web"].scale(0)