import secret_settings

import pymongo
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, \
    ParseMode
from telegram.ext import CommandHandler, CallbackContext, Updater, CallbackQueryHandler, Filters, \
    MessageHandler
import time
from random import randint
from prettytable import PrettyTable
import datetime

TOTAL_PARKING_SPOTS = 3

basic_buttons = [['users', 'help'], ['book', 'free', 'status']]


def get_bot_description():
    return """   Hello there👋. This is a company's parking lot management system🅿️,\
please note that there are parking spaces that are fixed for specific employees😊.
You can book / free parking from 8 pm to 7 am the next day.
After 7 A.m., a list is decided and a message is sent in accordance with the \
decision to anyone who has requested parking,
The decision is made according to the staff score💯'''
            Commands description:
            /help : Get bot Description
            /users :  Show info on all users
            /free_tmrw : Release parking spot that have been booked
            /book_tmrw : Ask for parking spot
            /status : Displays the current parking status
            /get_plan : get  """


# def button(update: Update, context: CallbackContext):
#     chat_id = update.effective_chat.id
#     text_command = update.callback_query.data
#     if text_command == 'book_tmrw':
#         book_tmrw(update, context)
#     elif text_command == 'free_spot':
#         free_tmrw(update, context)
#     elif text_command == 'status_tmrw':
#         status_tomorrow(update, context)

# def button(update: Update, context: CallbackContext):
#     text_command = update.callback_query.data
#     if text_command == 'book_tmrw':
#         book_tmrw(update, context)
#     elif text_command == 'free_spot':
#         free_tmrw(update, context)
#     elif text_command == 'status_tmrw':
#         status_tomorrow(update, context)


def basic_button(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    text_command = update.message.text
    if text_command == 'help':
        response = get_bot_description()
        context.bot.send_message(chat_id=chat_id, text=response)
    elif text_command == 'users':
        users(update, context)
    if text_command == 'book':
        book_tmrw(update, context)
    elif text_command == 'free':
        free_tmrw(update, context)
    elif text_command == 'status':
        status_tomorrow(update, context)


def generate_button(data):
    # keyboard = [
    #     [
    #         InlineKeyboardButton('Free' if data == 'free_spot' else 'Book', callback_data=data),
    #     ],
    # ]
    # reply_markup = InlineKeyboardMarkup(keyboard)
    # return reply_markup
    if data == 'free':
        basic_buttons = [['users', 'help'], ['book', 'status']]
    elif data == 'book':
        basic_buttons = [['users', 'help'], ['free', 'status']]

    return ReplyKeyboardMarkup(basic_buttons)


# bot commands #

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Start chat #{chat_id}")
    db = client.get_database('parking_db')
    employees = db.get_collection('employees')
    user = employees.find_one({'user_id': chat_id})
    if not user:
        user = {'user_id': chat_id, 'name': update.message.from_user.first_name,
                'license plate': randint(103, 200), 'rank': 2, 'points': 0}
        employees.replace_one({'user_id': chat_id}, user, upsert=True)
    reply_markup = ReplyKeyboardMarkup(basic_buttons)
    context.bot.send_message(chat_id=chat_id, text=f"🚗️ Welcome {user['name']}! 🚗️",
                             reply_markup=reply_markup)


def users(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db = client.get_database('parking_db')
    employees = db.get_collection('employees')
    res = []
    for user in employees.find():
        res.append(user['name'])
    context.bot.send_message(chat_id=chat_id, text=', '.join(res), parse_mode=ParseMode.MARKDOWN)


# def commands(update: Update, context: CallbackContext):
#     chat_id = update.effective_chat.id
#     response = 'Here a list of all commands you can do'
#     keyboard1 = [
#         [
#             InlineKeyboardButton("Book", callback_data='book_tmrw'),
#             InlineKeyboardButton("Free", callback_data='free_spot'),
#         ],
#         [
#             InlineKeyboardButton("Status", callback_data='status_tmrw'),
#
#         ]
#
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard1)
#     context.bot.send_message(chat_id=chat_id, text=response, reply_markup=reply_markup)


def status_tomorrow(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db = client.get_database('parking_db')
    final_list = db.get_collection('final_list')
    request_list = db.get_collection('request_list')
    employees = db.get_collection('employees')
    table = PrettyTable()
    table.title = 'Parking slots'
    table.field_names = ["name", "rank", "points"]
    count = 0
    for user in final_list.find():
        user = employees.find_one({'user_id': user['user_id']})
        table.add_row([user['name'], user['rank'], user['points']])
        count += 1
    for waiting_user in request_list.find().sort(
            [('points', pymongo.DESCENDING), ('time', pymongo.ASCENDING)]):
        if count == TOTAL_PARKING_SPOTS:
            break
        user = employees.find_one({'user_id': waiting_user['user_id']})
        table.add_row([user['name'], user['rank'], user['points']])
        count += 1
    for i in range(TOTAL_PARKING_SPOTS - count):
        table.add_row(['---', '---', '---'])
    text = f"""```{table.get_string()}```"""
    context.bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN)


def book_tmrw(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"= Got on chat #{chat_id}")
    db = client.get_database('parking_db')
    employees = db.get_collection('employees')
    user_info = employees.find_one({'user_id': chat_id})  # return a dictionary
    if user_info['rank'] == 1:
        seniors_spot = db.get_collection('final_list')
        seniors_spot.replace_one({"user_id": chat_id}, {"user_id": chat_id, "time": time.time()},
                                 upsert=True)
        res = "Dear senior employee,a parking spot has booked succesfuly"
    else:
        requests = db.get_collection('request_list')
        requests.replace_one({"user_id": chat_id}, {"user_id": chat_id, "time": time.time()},
                             upsert=True)
        res = 'we received your request, we will reply to you soon'

    context.bot.send_message(chat_id=chat_id, text=res, reply_markup=generate_button('book'))
    status_tomorrow(update, context)


def free_tmrw(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db = client.get_database('parking_db')
    employees = db.get_collection('employees')
    user_info = employees.find_one({'user_id': chat_id})  # return a dictionary
    if user_info['rank'] == 1:
        seniors_spot = db.get_collection('final_list')
        seniors_spot.delete_one({'user_id': chat_id})
    else:
        juniors_spot = db.get_collection('request_list')
        juniors_spot.delete_one({'user_id': chat_id})
    res = "thank you for releasing the spot for another great worker tmrw."
    context.bot.send_message(chat_id=chat_id, text=res, reply_markup=generate_button('free'))


def send_plan(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db = client.get_database('parking_db')
    final_list = db.get_collection('final_list')
    if final_list.find_one({'user_id': chat_id}):
        context.bot.send_message(chat_id=chat_id,
                                 text="your request has been accepted, you can park tmrw")
    else:
        context.bot.send_message(chat_id=chat_id,
                                 text="your request has been rejected, no parking for you!")


# helper methods #

def user_as_string(user):
    return f"{user['user_id']} {user['name']} {user['license plate']} " \
           f"{user['rank']} {user['points']}\n"


def update_final_list(context: CallbackContext):
    db = client.get_database('parking_db')
    final_list = db.get_collection('final_list')
    empty_spots = TOTAL_PARKING_SPOTS - final_list.count()
    request_list = db.get_collection('request_list')
    accept_text = 'your request has been accepted, you can park tmrw'
    reject_text = 'your request has been rejected, no parking for you!'
    for waiting_user in request_list.find().sort(
            [('points', pymongo.DESCENDING), ('time', pymongo.ASCENDING)]):
        if not empty_spots:  # empty == 0
            context.bot.send_message(chat_id=waiting_user['user_id'], text=reject_text)
        else:
            final_list.replace_one({'user_id': waiting_user['user_id']},
                                   {'user_id': waiting_user['user_id']}, upsert=True)
            context.bot.send_message(chat_id=waiting_user['user_id'], text=accept_text)
            empty_spots -= 1


# db #

def create_request_list():
    db = client.get_database('parking_db')
    requests = db.get_collection('request_list')
    requests.delete_many({})
    requests.create_index([('user_id', pymongo.ASCENDING)])


def creat_users():
    liwaa_id = 1044776988
    tameer_id = 836471985
    omar_id = 574225603
    db = client.get_database('parking_db')
    employees = db.get_collection('employees')
    employees.delete_many({})
    employees.create_index([('user_id', pymongo.ASCENDING)])
    employees.replace_one({'user_id': liwaa_id},
                          {'user_id': liwaa_id, 'name': 'liwaa', 'license plate': 100, 'rank': 1,
                           'points': 0},
                          upsert=True)
    employees.replace_one({'user_id': tameer_id},
                          {'user_id': tameer_id, 'name': 'tameer', 'license plate': 101, 'rank': 1,
                           'points': 0},
                          upsert=True)
    # employees.replace_one({'user_id': omar_id},
    #                       {'user_id': omar_id, 'name': 'omar', 'license plate': 102, 'rank': 1,
    #                        'points': 0},
    #                       upsert=True)


def create_final_list():
    db = client.get_database('parking_db')
    employees = db.get_collection('employees')
    final_list = db.get_collection('final_list')
    final_list.create_index([('user_id', pymongo.ASCENDING)])
    final_list.delete_many({})
    for employee in employees.find():
        if employee['rank'] == 1:
            final_list.replace_one({'user_id': employee['user_id']},
                                   {'user_id': employee['user_id']},
                                   upsert=True)


if __name__ == '__main__':
    client = pymongo.MongoClient()

    creat_users()
    create_request_list()
    create_final_list()

    logging.basicConfig(
        format='[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s',
        level=logging.INFO)

    logger = logging.getLogger(__name__)

    updater = Updater(token=secret_settings.BOT_TOKEN, use_context=True)

    dispatcher = updater.dispatcher
    # updater.dispatcher.add_handler(CallbackQueryHandler(button))

    jobs = updater.job_queue
    jobs.run_daily(update_final_list, datetime.datetime(datetime.datetime.now().year,
                                                        datetime.datetime.now().month,
                                                        datetime.datetime.now().day, 22, 59, 0))

    echo_handler = MessageHandler(Filters.text, basic_button)
    dispatcher.add_handler(echo_handler)

    start_handler = CommandHandler('start', start, )
    dispatcher.add_handler(start_handler)

    users_handler = CommandHandler('users', users, )
    dispatcher.add_handler(users_handler)

    # cmds_handler = CommandHandler('commands', commands, )
    # dispatcher.add_handler(cmds_handler)

    free_handler = CommandHandler('free_tmrw', free_tmrw, )
    dispatcher.add_handler(free_handler)

    book_tomorrow_handler = CommandHandler('book_tmrw', book_tmrw, )
    dispatcher.add_handler(book_tomorrow_handler)

    users_handler = CommandHandler('status_tmrw', status_tomorrow, )
    dispatcher.add_handler(users_handler)

    send_plan_handler = CommandHandler('send_plan', send_plan, )
    dispatcher.add_handler(send_plan_handler)

    logger.info("* Start polling...")
    updater.start_polling()  # Starts polling in a background thread.
    updater.idle()  # Wait until Ctrl+C is pressed
    logger.info("* Bye!")
