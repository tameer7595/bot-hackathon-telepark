import secret_settings

import pymongo
import logging
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, Updater


def user_as_string(user):
    return f"{user['user_id']} {user['name']} {user['license plate']}\n"


def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    logger.info(f"> Start chat #{chat_id}")
    db = client.get_database('parking_db')
    employees = db.get_collection('employees')
    for user in employees.find({'user_id': chat_id}):
        context.bot.send_message(chat_id=chat_id, text=f"💣 Welcome! 💣 {user['name']}")


def users(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    db = client.get_database('parking_db')
    employees = db.get_collection('employees')
    res = 'user_id - name - license plate\n'
    for user in employees.find():
        res += f"{user['user_id']} {user['name']} {user['license plate']}\n"
    context.bot.send_message(chat_id=chat_id, text=res)


def status_tomorrow(update: Update, context: CallbackContext):
    # print final list
    chat_id = update.effective_chat.id
    db = client.get_database('parking_db')
    final_list = db.get_collection('final_list')
    employees = db.get_collection('employees')
    res = ""
    for user in final_list.find():
        res += user_as_string(employees.find_one({'user_id': user['user_id']}))
    context.bot.send_message(chat_id=chat_id, text=res)


def create_users():
    liwaa_id = 1044776988
    tameer_id = 836471985
    omar_id = 574225603
    db = client.get_database('parking_db')
    employees = db.get_collection('employees')
    employees.delete_many({})
    employees.create_index([('user_id', pymongo.ASCENDING)])
    employees.replace_one({'user_id': liwaa_id},
                          {'user_id': liwaa_id, 'name': 'liwaa', 'license plate': 100},
                          upsert=True)
    employees.replace_one({'user_id': tameer_id},
                          {'user_id': tameer_id, 'name': 'tameer', 'license plate': 101},
                          upsert=True)
    employees.replace_one({'user_id': omar_id},
                          {'user_id': omar_id, 'name': 'omar', 'license plate': 102},
                          upsert=True)


def create_final_list():
    db = client.get_database('parking_db')
    employees = db.get_collection('employees')
    final_list = db.get_collection('final_list')
    final_list.create_index([('user_id', pymongo.ASCENDING)])
    final_list.delete_many({})
    for employee in employees.find():
        final_list.replace_one({'user_id': employee['user_id']}, {'user_id': employee['user_id']},
                               upsert=True)


if __name__ == '__main__':
    client = pymongo.MongoClient()
    create_users()
    create_final_list()

    logging.basicConfig(
        format='[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s',
        level=logging.INFO)

    logger = logging.getLogger(__name__)

    updater = Updater(token=secret_settings.BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start, )
    dispatcher.add_handler(start_handler)

    users_handler = CommandHandler('users', users, )
    dispatcher.add_handler(users_handler)

    users_handler = CommandHandler('status_tmrw', status_tomorrow, )
    dispatcher.add_handler(users_handler)

    logger.info("* Start polling...")
    updater.start_polling()  # Starts polling in a background thread.
    updater.idle()  # Wait until Ctrl+C is pressed
    logger.info("* Bye!")
