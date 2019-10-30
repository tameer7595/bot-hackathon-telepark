# TelePark 
<https://t.me/{BOT_ID}>

### Effective Parking Manager

* [Omar Burqan](https://github.com/omarburqan)
* [Liwaa Haj Yehya](https://github.com/liwaa96)
* [Tameer Ghnaim](https://github.com/tameer7595)

####TelePark is parking manager bot used for management purpose in companies that has a few parking spots and doesn’t serve everybody, employees can book parking spot for the next day depending on rank and points.

## Screenshots

![SCREESHOT DECSRIPTION](screenshots/shopping-list-bot-1.png)

## How to Run This Bot
### Prerequisites
* Python 3.7
* pipenv
* {ADD MORE DEPENDENCIES HERE - FOR EXAMPLE MONGODB OR ANYTHING ELSE}

### Setup
* Clone this repo from github
* Install dependencies: `pipenv install`
* Get a BOT ID from the [botfather](https://telegram.me/BotFather).
* Create a `secret_settings.py` file:

        BOT_TOKEN = "your-bot-token-here"

### Run
To run the bot use:

    pipenv run python bot.py

### Running tests
First make sure to install all dev dependencies:

    pipenv install --dev

To run all test  use:

    pipenv run pytest

(Or just `pytest` if running in a pipenv shell.)

## Credits and References
* [Telegram Docs](https://core.telegram.org/bots)
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
* [MongoDB and PyMongo.](https://api.mongodb.com/python/current/tutorial.html)
* [PrettyTable](http://zetcode.com/python/prettytable/)
* [datetime](https://docs.python.org/3/library/datetime.html)

