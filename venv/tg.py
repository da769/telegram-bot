#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [["Boy", "Girl", "Other"]]

    await update.message.reply_text(
        "Hi! My name is Professor Bot. I will hold a conversation with you. "
        "Send /cancel to stop talking to me.\n\n"
        "Are you a boy or a girl?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl?"
        ),
    )

    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "I see! Please send me a photo of yourself, "
        "so I know what you look like, or send /skip if you don't want to.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("user_photo.jpg")
    logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
    await update.message.reply_text(
        "Gorgeous! Now, send me your location please, or send /skip if you don't want to."
    )

    return LOCATION


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    await update.message.reply_text(
        "I bet you look great! Now, send me your location please, or send /skip."
    )

    return LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    await update.message.reply_text(
        "Maybe I can visit you sometime! At last, tell me something about yourself."
    )

    return BIO


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    await update.message.reply_text(
        "You seem a bit paranoid! At last, tell me something about yourself."
    )

    return BIO


async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text("Thank you! I hope we can talk again some day.")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6841932123:AAGhy9Htjjus8WHrtcs_pZ1301ONohUi170").build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],
            PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
            LOCATION: [
                MessageHandler(filters.LOCATION, location),
                CommandHandler("skip", skip_location),
            ],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()



# from telegram import Update
# from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, Filters, Updater

# import random

# def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     update.message.reply_text('Hello!  What can I do for you?')

# def bye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     update.message.reply_text('See you later! ')

# def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     update.message.reply_text(
#         'Available commands:\n'
#         '/start - Start the bot\n'
#         '/bye - End the conversation\n'
#         '/help - Get help information\n'
#         '/joke - Get a random joke\n'
#         '/quote - Get a random quote\n'
#         '/weather [city] - Get weather information for a city'
#     )

# def joke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     jokes = [
#         "What do you call a fish with no eyes? Fsh!",
#         "Why did the scarecrow win an award? Because he was outstanding in his field!",
#         "What do you call a lazy kangaroo? Pouch potato!"
#     ]
#     update.message.reply_text(random.choice(jokes))

# def quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     quotes = [
#         "The only way to do great work is to love what you do. - Steve Jobs",
#         "The best way to predict the future is to create it. - Peter Drucker",
#         "Life is what happens to you while you're busy making other plans. - John Lennon"
#     ]
#     update.message.reply_text(random.choice(quotes))

# def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     reply_text = "I don't understand yet, but I'm learning! "
#     if update.message.text == "Hi" or update.message.text == "Hello":
#         reply_text = "Hi there!  How can I help you today?"
#     update.message.reply_text(reply_text)

# # Weather API integration and NLP for more advanced features...

# app = ApplicationBuilder().token("6841932123:AAGhy9Htjjus8WHrtcs_pZ1301ONohUi170").build()

# app.add_handler(CommandHandler("start", start))
# app.add_handler(CommandHandler("bye", bye))
# app.add_handler(CommandHandler("help", help))
# app.add_handler(CommandHandler("joke", joke))
# app.add_handler(CommandHandler("quote", quote))
# app.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

# app.run_polling()




# from telegram import Update
# from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


# async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     await update.message.reply_text(f'Hello {update.effective_user.first_name}')


# app = ApplicationBuilder().token("6841932123:AAGhy9Htjjus8WHrtcs_pZ1301ONohUi170").build()

# app.add_handler(CommandHandler("hello", hello))

# app.run_polling()



# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# def start(update, context):
#     update.message.reply_text('Hello! What can I do for you?')

# def echo(update, context):
#     update.message.reply_text(update.message.text)

# updater = Updater(token='6841932123:AAGhy9Htjjus8WHrtcs_pZ1301ONohUi170')
# dispatcher = updater.dispatcher

# # Example using alternative filtering approach:
# dispatcher.add_handler(MessageHandler(Filters.text, echo))
# dispatcher.add_handler(MessageHandler(Filters.command, start))

# updater.start_polling()
# updater.idle()




# # from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# # def start(update, context):
# #     update.message.reply_text('Hello! What can I do for you?')

# # def echo(update, context):
# #     update.message.reply_text(update.message.text)

# # updater = Updater(token='6841932123:AAGhy9Htjjus8WHrtcs_pZ1301ONohUi170')
# # dispatcher = updater.dispatcher

# # dispatcher.add_handler(CommandHandler('start', start))
# # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

# # updater.start_polling()
# # updater.idle()
