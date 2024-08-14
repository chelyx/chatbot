import telebot
from api import *
from es import ES
from en import EN
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv
import os

load_dotenv()

JIRA_API_URL = os.getenv('JIRA_API_URL')
TOKEN = os.getenv('TOKEN')
EMAIL = os.getenv('EMAIL')
PROJECT_KEY = os.getenv('PROJECT_KEY')
USER_ID = os.getenv('USER_ID')
JIRA_BOARD = os.getenv('JIRA_BOARD')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


user_data = {}
bot = telebot.TeleBot(TELEGRAM_TOKEN)
LANG_EN = "English"
LANG_ES = "Español"
SELECTED_LANG = ES


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, SELECTED_LANG['WELCOME_MESSAGE'])


@bot.message_handler(commands=['lang'])
def change_language(message):
    board = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    board.add(
        KeyboardButton(LANG_EN),
        KeyboardButton(LANG_ES),
    )
    bot.send_message(message.chat.id, SELECTED_LANG['CHOOSE_OPTION'], reply_markup=board)
    bot.register_next_step_handler(message, handle_change_language)


def handle_change_language(message):
    global SELECTED_LANG
    if message.text.lower() == LANG_EN.lower():
        SELECTED_LANG = EN
    elif message.text.lower() == LANG_ES.lower():
        SELECTED_LANG = ES
    bot.send_message(message.chat.id, SELECTED_LANG['LANG_CHANGED'], reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=['help'])
def send_help(message):
    board = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    board.add(
        KeyboardButton(SELECTED_LANG['CREATE_TICKET']),
        KeyboardButton(SELECTED_LANG['EDIT_TICKET']),
        KeyboardButton(SELECTED_LANG['STATUS_TICKET'])
    )
    bot.send_message(message.chat.id, SELECTED_LANG['CHOOSE_OPTION'], reply_markup=board)
    bot.register_next_step_handler(message, handle_board_answer)


def handle_board_answer(message):
    if message.text.lower() == SELECTED_LANG['CREATE_TICKET'].lower():
        bot.send_message(message.chat.id, SELECTED_LANG['TICKET_SUMMARY'], reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, handle_create_issue_get_title)
    elif message.text.lower() == SELECTED_LANG['EDIT_TICKET'].lower():
        bot.send_message(message.chat.id, SELECTED_LANG['TICKET_KEY'], reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, handle_get_issue_edit)
    elif message.text.lower() == SELECTED_LANG['STATUS_TICKET'].lower():
        bot.send_message(message.chat.id, SELECTED_LANG['TICKET_KEY'], reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, handle_get_issue_status)


def validate_issue_exists(chat_id, issue):
    if 'errorMessages' in issue:
        bot.send_message(chat_id, issue['errorMessages'][0])
        del user_data[chat_id]
        return False
    return True


def handle_get_issue_status(message):
    chat_id = message.chat.id
    key = message.text
    user_data[chat_id] = {'issue_key': key}
    issue = get_issue(key)
    if validate_issue_exists(chat_id, issue):
        bot.send_message(chat_id, issue['fields']['status']['description'])


def handle_create_issue_get_title(message):
    chat_id = message.chat.id
    title = message.text
    user_data[chat_id] = {'title': title}
    bot.send_message(chat_id, SELECTED_LANG['TICKET_DESC'])
    bot.register_next_step_handler(message, handle_create_issue_get_description)


def handle_create_issue_get_description(message):
    chat_id = message.chat.id
    description = message.text
    user_data[chat_id]['description'] = description
    bot.send_message(chat_id, SELECTED_LANG['PICTURE'])
    bot.register_next_step_handler(message, handle_create_issue_get_photo)


def handle_create_issue_get_photo(message):
    chat_id = message.chat.id
    if message.content_type == 'photo':
        photo = message.photo[-1].file_id
        user_data[chat_id]['photo'] = photo
        bot.send_message(chat_id, SELECTED_LANG['RECEIVED_PIC'] + SELECTED_LANG['CREATING_TICKET'])
    elif message.text.lower() == 'no':
        user_data[chat_id]['photo'] = None
        bot.send_message(chat_id, SELECTED_LANG['NO_PIC'] + SELECTED_LANG['CREATING_TICKET'])
    else:
        bot.send_message(chat_id, SELECTED_LANG['INVALID_PIC'])
        bot.register_next_step_handler(message, handle_create_issue_get_photo)
        return

    issue = create_issue(user_data[chat_id]['title'], user_data[chat_id]['description'])

    if user_data[chat_id]['photo']:
        photo_file_path = download_photo(user_data[chat_id]['photo'])
        if photo_file_path:
            upload_attachment(issue['key'], photo_file_path)

    bot.send_message(chat_id, SELECTED_LANG['TICKET_CREATED'] + JIRA_BOARD + issue['key'])
    del user_data[chat_id]


def handle_get_issue_edit(message):
    chat_id = message.chat.id
    key = message.text
    issue = get_issue(key)
    if validate_issue_exists(chat_id, issue):
        user_data[chat_id] = {'issue_key': key}
        bot.send_message(chat_id, SELECTED_LANG['PICTURE'])
        bot.register_next_step_handler(message, handle_upload_attachment)


def handle_upload_attachment(message):
    chat_id = message.chat.id
    if message.content_type == 'photo':
        photo = message.photo[-1].file_id
        bot.send_message(message.chat.id, SELECTED_LANG['RECEIVED_PIC'] + SELECTED_LANG['EDITING_TICKET'])
        photo_file_path = download_photo(photo)
        if photo_file_path:
            upload_attachment(user_data[chat_id]['issue_key'], photo_file_path)
    if message.content_type == 'text':
        bot.send_message(message.chat.id, SELECTED_LANG['NO_PIC'] + SELECTED_LANG['CANCEL_EDIT'])
        del user_data[chat_id]
        return
    bot.send_message(chat_id, SELECTED_LANG['TICKET_EDITED'] + JIRA_BOARD + user_data[chat_id]['issue_key'])
    del user_data[chat_id]


bot.polling()
