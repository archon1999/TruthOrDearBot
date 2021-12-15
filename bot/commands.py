import random

from telebot import TeleBot, types

from backend.models import (BotUser, Chat, Game, GameParticipant,
                            Lang, Task)
from backend.templates import Keys, Messages

from bot import config, utils
from bot.call_types import CallTypes


def make_game_keyboard(chat):
    join_url = f'http://t.me/{config.BOT_USERNAME}?start={chat.chat_id}'
    join_button = types.InlineKeyboardButton(
        text=Keys.JOIN.gettext(chat.lang),
        url=join_url,
    )
    start_game_button = utils.make_inline_button(
        text=utils.filter_html(Keys.START_GAME.gettext(chat.lang)),
        CallType=CallTypes.StartGame,
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(join_button)
    keyboard.add(start_game_button)
    return keyboard


def get_or_create_user(from_user):
    chat_id = from_user.id
    first_name = from_user.first_name
    last_name = from_user.last_name
    username = from_user.username
    if BotUser.users.filter(chat_id=chat_id).exists():
        user = BotUser.users.get(chat_id=chat_id)
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.save()
    else:
        user = BotUser.users.create(
            chat_id=chat_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            lang=Lang.RU,
        )
    return user


def join_handler(bot: TeleBot, message):
    chat_id = message.text.split()[1].removeprefix('join')
    user = get_or_create_user(message.from_user)
    chat = Chat.chats.get(chat_id=chat_id)
    game = chat.game
    if bot.get_chat_member(chat_id, user.chat_id) is None:
        return

    _, created = GameParticipant.participants.get_or_create(
        game=game,
        user=user,
    )
    if created:
        return_to_chat_text = Messages.JOINED_PRIVATE.gettext(user.lang)
        first_name = f'<a href="tg://user?id={user.chat_id}">{user.first_name}</a>'
        text = Messages.JOINED.gettext(chat.lang).format(
            first_name=first_name,
            participants_count=game.participants.count(),
        )
        keyboard = make_game_keyboard(chat)
        bot.send_message(chat_id, utils.filter_html(text),
                         reply_markup=keyboard)
    else:
        return_to_chat_text = Messages.JOINED_ALREADY_PRIVATE.gettext(
            user.lang
        )

    bot.send_message(user.chat_id, utils.filter_html(return_to_chat_text))


def leave_message_handler(bot: TeleBot, message):
    chat_id = message.chat.id
    user = get_or_create_user(message.from_user)
    chat = Chat.chats.get(chat_id=chat_id)
    game = chat.game
    if bot.get_chat_member(chat_id, user.chat_id) is None:
        return

    participant, created = GameParticipant.participants.get_or_create(
        game=game,
        user=user,
    )
    participant.delete()
    if not created:
        first_name = f'<a href="tg://user?id={user.chat_id}">{user.first_name}</a>'
        text = Messages.LEAVE.gettext(chat.lang).format(
            first_name=first_name,
            participants_count=game.participants.count(),
        )
        keyboard = make_game_keyboard(chat)
        bot.send_message(chat_id, utils.filter_html(text),
                         reply_markup=keyboard)


def start_command_handler_private(bot: TeleBot, message):
    user = get_or_create_user(message.from_user)
    chat_id = message.chat.id
    text = Messages.START_COMMAND_PRIVATE.gettext(user.lang)
    add_to_chat_url = f'http://t.me/{config.BOT_USERNAME}?startgroup=true'
    add_to_chat_button = types.InlineKeyboardButton(
        text=utils.filter_html(Keys.ADD_TO_CHAT.gettext(user.lang)),
        url=add_to_chat_url,
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(add_to_chat_button)
    bot.send_message(chat_id, utils.filter_html(text),
                     reply_markup=keyboard)


def start_command_handler_chat(bot: TeleBot, message):
    chat_id = message.chat.id
    title = message.chat.title
    if Chat.chats.filter(chat_id=chat_id).exists():
        chat = Chat.chats.get(chat_id=chat_id)
        chat.title = title
        chat.save()
    else:
        chat = Chat.chats.create(
            chat_id=chat_id,
            title=title,
            lang=Lang.RU,
        )
        Game.games.create(chat=chat)

    text = Messages.START_COMMAND_CHAT.gettext(chat.lang)
    keyboard = make_game_keyboard(chat)
    bot.send_message(chat_id, utils.filter_html(text),
                     reply_markup=keyboard)


def start_command_handler(bot: TeleBot, message):
    args = message.text.split()[1:]
    if message.chat.type == 'private':
        if args:
            join_handler(bot, message)
        else:
            start_command_handler_private(bot, message)
    else:
        start_command_handler_chat(bot, message)


def start_game(bot: TeleBot, game: Game):
    chat = game.chat
    chat_id = chat.chat_id
    if game.current_player:
        return

    if game.players.count() == game.participants.count():
        game.players.all().delete()

    for participant in game.participants.all():
        if not game.players.filter(user=participant.user).exists():
            player = game.players.create(user=participant.user)
            user = player.user
            game.current_player = user
            game.save()
            break

    query = f'{Keys.TRUTH.gettext(chat.lang)} {chat.chat_id}.'
    truth_button = types.InlineKeyboardButton(
        text=Keys.TRUTH.gettext(chat.lang),
        switch_inline_query_current_chat=query,
    )
    query = f'{Keys.DARE.gettext(chat.lang)} {chat.chat_id}.'
    dare_button = types.InlineKeyboardButton(
        text=Keys.DARE.gettext(chat.lang),
        switch_inline_query_current_chat=query,
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(truth_button)
    keyboard.add(dare_button)
    first_name = f'<a href="tg://user?id={user.chat_id}">{user.first_name}</a>'
    text = Messages.TRUTH_OR_DARE.gettext(chat.lang).format(
        first_name=first_name,
    )
    message = bot.send_message(chat_id, utils.filter_html(text),
                               reply_markup=keyboard)
    game.message_id = message.id
    game.save()


def start_game_call_handler(bot: TeleBot, call):
    chat_id = call.message.chat.id
    chat = Chat.chats.get(chat_id=chat_id)
    game = chat.game
    start_game(bot, game)


def truth_inline_query_handler(bot: TeleBot, inline_query):
    chat_id = inline_query.query.split()[-1].removesuffix('.')
    chat = Chat.chats.get(chat_id=chat_id)
    game = chat.game
    current_player = game.current_player
    user = get_or_create_user(inline_query.from_user)
    if current_player != user:
        return

    player = game.players.get(user=user)
    if player.task:
        return

    player.task = random.choice(Task.tasks.filter(type=Task.Type.TRUTH))
    player.save()

    query = f'{Keys.TASK_COMPLETED.gettext(chat.lang)} {chat.chat_id}.'
    task_completed_button = types.InlineKeyboardButton(
        text=Keys.TASK_COMPLETED.gettext(chat.lang),
        switch_inline_query_current_chat=query,
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(task_completed_button)
    first_name = f'<a href="tg://user?id={user.chat_id}">{user.first_name}</a>'
    text = Messages.TASK_TRUTH.gettext(chat.lang).format(
        first_name=first_name,
        task_body=player.task.get_body(chat.lang),
    )
    try:
        bot.edit_message_text(
            text=utils.filter_html(text),
            chat_id=chat_id,
            message_id=game.message_id,
            reply_markup=keyboard,
            parse_mode='HTML',
        )
    except Exception:
        bot.send_message(chat_id, utils.filter_html(text),
                         reply_markup=keyboard)


def dare_inline_query_handler(bot: TeleBot, inline_query):
    chat_id = inline_query.query.split()[-1].removesuffix('.')
    chat = Chat.chats.get(chat_id=chat_id)
    game = chat.game
    current_player = game.current_player
    user = get_or_create_user(inline_query.from_user)
    if current_player != user:
        return

    player = game.players.get(user=user)
    if player.task:
        return

    player.task = random.choice(Task.tasks.filter(type=Task.Type.DARE))
    player.save()

    query = f'{Keys.TASK_COMPLETED.gettext(chat.lang)} {chat.chat_id}.'
    task_completed_button = types.InlineKeyboardButton(
        text=Keys.TASK_COMPLETED.gettext(chat.lang),
        switch_inline_query_current_chat=query,
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(task_completed_button)
    first_name = f'<a href="tg://user?id={user.chat_id}">{user.first_name}</a>'
    text = Messages.TASK_DARE.gettext(chat.lang).format(
        first_name=first_name,
        task_body=player.task.get_body(chat.lang),
    )
    try:
        bot.edit_message_text(
            text=utils.filter_html(text),
            chat_id=chat_id,
            message_id=game.message_id,
            reply_markup=keyboard,
            parse_mode='HTML',
        )
    except Exception:
        bot.send_message(chat_id, utils.filter_html(text),
                         reply_markup=keyboard)


def task_completed_inline_query_handler(bot: TeleBot, inline_query):
    chat_id = inline_query.query.split()[-1].removesuffix('.')
    chat = Chat.chats.get(chat_id=chat_id)
    user = get_or_create_user(inline_query.from_user)
    game = chat.game
    if user == game.current_player:
        return

    bot.edit_message_reply_markup(chat_id=chat_id,
                                  message_id=game.message_id,
                                  reply_markup=types.InlineKeyboardMarkup())
    game.current_player = None
    game.message_id = None
    game.save()
    start_game(bot, game)
