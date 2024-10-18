import random

from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
from get_db import add_user, get_user_cid, get_target_translate_other, get_user_id, delete_word_user_db, add_word_user_db, get_words_list

print('Start telegram bot...')

state_storage = StateMemoryStorage()
token_bot = ''
bot = TeleBot(token_bot, state_storage=state_storage)

known_users = []
userStep = {}
buttons = []


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = message.chat.id
    if cid != get_user_cid(cid): # Проверяем наличие такого пользователя в БД
        add_user(cid) # Добавляем его в БД
    if cid not in known_users:
        known_users.append(cid)
        userStep[cid] = 0
        bot.send_message(cid, "Здравствуй! Проверим твои знания английского...")
    else:
        bot.send_message(cid, "Давай еще раз проверим твои знания английского...")
    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    data_words = get_target_translate_other(get_user_id(cid))
    target_word = data_words[0]   # из БД
    translate = data_words[1]     #  из БД
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    others = data_words[2]       # из БД
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word_user(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        delete_word = data['target_word']
        cid = message.chat.id
        chat_id = message.chat.id
        if get_target_translate_other(get_user_id(cid))[3] < 6:
            bot.send_message(chat_id, f'Слово удалить нельзя: слова для удаления закончились.Выбери следующее действие')

        else:
            delete_word_user_db(get_user_id(cid),delete_word)
            bot.send_message(chat_id, f'Слово {delete_word} удалено.Выбери следующее действие')


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word_user(message):
    cid = message.chat.id
    chat_id = message.chat.id
    userStep[cid] = 1
    bot.send_message(chat_id, "Введи через пробел новое слово по-английски и по-русски")
    bot.register_next_step_handler(message, input_word)


def input_word(message):
    cid = message.chat.id
    chat_id = message.chat.id
    new_word = message.text.split()
    if new_word[0] in get_words_list(): # Проверяем наличие такого слова в БД
        bot.send_message(chat_id, f'Слово {new_word[0]} уже было.')
        create_cards(message)
    if len(new_word) != 2: # Проверяем корректность ввода слов
        bot.send_message(chat_id, 'Не верно введены слова.')
        create_cards(message)
    else:
        add_word_user_db(get_user_id(cid),new_word)
        bot.send_message(chat_id, f'Слово {new_word[0]} добавлено.')
        create_cards(message)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            buttons.extend([next_btn, add_word_btn, delete_word_btn])
            hint = show_hint(*hint_text)
            bot.send_message(message.chat.id, hint, reply_markup=markup)
            bot.send_message(message.chat.id, "Выбери следующее действие")
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")
            markup.add(*buttons)
            bot.send_message(message.chat.id, hint, reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)