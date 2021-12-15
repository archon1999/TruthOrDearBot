import telebot

import config
from bot.call_types import CallTypes
from bot import commands

from backend.templates import Keys
from backend.models import Lang


bot = telebot.TeleBot(
    token=config.TOKEN,
    num_threads=4,
    parse_mode='HTML',
)


message_handlers = {
    '/start': commands.start_command_handler,
    '/leave': commands.leave_message_handler,
}

key_handlers = {

}


@bot.message_handler()
def message_handler(message):
    for text, handler in message_handlers.items():
        if message.text.startswith(text):
            handler(bot, message)
            break

    for key, handler in key_handlers.items():
        if message.text in key.getall():
            handler(bot, message)
            break


callback_query_handlers = {
    CallTypes.StartGame: commands.start_game_call_handler,
}


@bot.callback_query_handler(func=lambda _: True)
def callback_query_handler(call):
    call_type = CallTypes.parse_data(call.data)
    for CallType, handler in callback_query_handlers.items():
        if CallType == call_type.__class__:
            handler(bot, call)
            break


inline_query_handlers = {
    Keys.DARE.gettext(Lang.EN): commands.dare_inline_query_handler,
    Keys.DARE.gettext(Lang.RU): commands.dare_inline_query_handler,
    Keys.TRUTH.gettext(Lang.RU): commands.truth_inline_query_handler,
    Keys.TRUTH.gettext(Lang.EN): commands.truth_inline_query_handler,
    Keys.TASK_COMPLETED.gettext(Lang.EN):
        commands.task_completed_inline_query_handler,
    Keys.TASK_COMPLETED.gettext(Lang.RU):
        commands.task_completed_inline_query_handler,
}


@bot.inline_handler(func=lambda query: query.query.endswith('.'))
def inline_handler(inline_query):
    for query, handler in inline_query_handlers.items():
        if inline_query.query.startswith(query):
            handler(bot, inline_query)
            break


if __name__ == "__main__":
    bot.polling()
    # bot.infinity_polling()
