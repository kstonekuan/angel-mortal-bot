import logging
import config
import player

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler

CHOOSING, ANGEL, MORTAL = range(3)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

players = player.initPlayers()

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    players[update.message.chat.username].chat_id = update.message.chat.id
    update.message.reply_text('Hi! Use /send to send a message to your angel or mortal and /cancel to cancel message')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Use /send to send a message to your angel or mortal and /cancel to cancel message')

def send_command(update: Update, context: CallbackContext):
    """Send a message when the command /send is issued."""
    send_menu = [[InlineKeyboardButton('Angel', callback_data='angel')],
                 [InlineKeyboardButton('Mortal', callback_data='mortal')]]
    reply_markup = InlineKeyboardMarkup(send_menu)
    update.message.reply_text('Who do you want to send your message to:', reply_markup=reply_markup)

    return CHOOSING

def startAngel(update: Update, context: CallbackContext):
    chat_id = players[update.callback_query.message.chat.username].angel.chat_id
    if chat_id is None:
        update.callback_query.message.reply_text('Sorry your angel has not started this bot')
        return ConversationHandler.END

    update.callback_query.message.reply_text('Please type your message to your angel')
    return ANGEL

def startMortal(update: Update, context: CallbackContext):
    chat_id = players[update.callback_query.message.chat.username].mortal.chat_id
    if chat_id is None:
        update.callback_query.message.reply_text('Sorry your mortal has not started this bot')
        return ConversationHandler.END

    update.callback_query.message.reply_text('Please type your message to your mortal')
    return MORTAL

def sendAngel(update: Update, context: CallbackContext):
    reply = f"Message from your Mortal:\n\n{update.message.text}"
    chat_id = players[update.message.chat.username].angel.chat_id
    context.bot.send_message(
                        text = reply,
                        chat_id = chat_id)

    update.message.reply_text('Message sent!')

    return ConversationHandler.END

def sendMortal(update: Update, context: CallbackContext):
    reply = f"Message from your Angel:\n\n{update.message.text}"
    chat_id = players[update.message.chat.username].mortal.chat_id
    context.bot.send_message(
                        text = reply,
                        chat_id = chat_id)

    update.message.reply_text('Message sent!')

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    player = update.message.from_player
    logger.info("Player %s canceled the conversation.", player.first_name)
    update.message.reply_text(
        'Sending message cancelled.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(config.ANGEL_BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('send', send_command)],
        states={
            CHOOSING: [CallbackQueryHandler(startAngel, pattern='angel'), CallbackQueryHandler(startMortal, pattern='mortal')],
            ANGEL: [MessageHandler(Filters.text & ~Filters.command, sendAngel)],
            MORTAL: [MessageHandler(Filters.text & ~Filters.command, sendMortal)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()