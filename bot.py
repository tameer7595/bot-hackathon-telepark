import secret_settings

print(secret_settings.BOT_TOKEN)

# YOUR BOT HERE


import pymongo
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, \
    Filters, Updater


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


# def respond(update: Update, context: CallbackContext):
#     chat_id = update.effective_chat.id
#     text = update.message.text
#     context.user_data['location'] = text
#     logger.info(f"= Got on chat #{chat_id}: {text!r}")
#     response = f'Please send your location to know how far you are from {text}'
#     location_keyboard = KeyboardButton(text="send_location",
#                                        request_location=True)
#     custom_keyboard = [[location_keyboard]]
#     reply_markup = ReplyKeyboardMarkup(custom_keyboard)
#     context.bot.send_message(chat_id=update.message.chat_id, text=response,
#                              reply_markup=reply_markup)


def creat_users():
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


if __name__ == '__main__':
    client = pymongo.MongoClient()
    creat_users()

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

    # echo_handler = MessageHandler(Filters.text, respond)
    # dispatcher.add_handler(echo_handler)

    logger.info("* Start polling...")
    updater.start_polling()  # Starts polling in a background thread.
    updater.idle()  # Wait until Ctrl+C is pressed
    logger.info("* Bye!")
