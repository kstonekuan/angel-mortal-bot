import logging
import player
import messages
import datetime
import collections

import config

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler

CHOOSING, ANGEL, MORTAL = range(3)


# Enable logging
logging.basicConfig(
    filename=f'logs/{datetime.datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")}.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

players = collections.defaultdict(player.Player)
player.loadPlayers(players)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    playerName = update.message.chat.username.lower()
    if players[playerName].username is None:
        update.message.reply_text(messages.NOT_REGISTERED)
        return

    players[playerName].chat_id = update.message.chat.id

    logger.info(f'{playerName} started the bot with chat_id {players[playerName].chat_id}')

    update.message.reply_text(f'Hi! {messages.HELP_TEXT}')

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(messages.HELP_TEXT)

def reload_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /reloadplayers is issued."""
    player.loadPlayers(players)

    update.message.reply_text(f'Players reloaded')

def send_command(update: Update, context: CallbackContext):
    """Start send convo when the command /send is issued."""
    playerName = update.message.chat.username.lower()

    if players[playerName].username is None:
        update.message.reply_text(messages.NOT_REGISTERED)
        return ConversationHandler.END

    if players[playerName].chat_id is None:
        update.message.reply_text(messages.ERROR_CHAT_ID)
        return ConversationHandler.END

    send_menu = [[InlineKeyboardButton(config.ANGEL_ALIAS, callback_data='angel')],
                 [InlineKeyboardButton(config.MORTAL_ALIAS, callback_data='mortal')]]
    reply_markup = InlineKeyboardMarkup(send_menu)
    update.message.reply_text(messages.SEND_COMMAND, reply_markup=reply_markup)

    return CHOOSING

def startAngel(update: Update, context: CallbackContext):
    playerName = update.callback_query.message.chat.username.lower()
    if players[playerName].angel.chat_id is None:
        update.callback_query.message.reply_text(messages.getBotNotStartedMessage(config.ANGEL_ALIAS))
        logger.info(messages.getNotRegisteredLog(config.ANGEL_ALIAS, playerName, players[playerName].angel.username))
        return ConversationHandler.END

    update.callback_query.message.reply_text(messages.getPlayerMessage(config.ANGEL_ALIAS))
    return ANGEL

def startMortal(update: Update, context: CallbackContext):
    playerName = update.callback_query.message.chat.username.lower()
    if players[playerName].mortal.chat_id is None:
        update.callback_query.message.reply_text(messages.getBotNotStartedMessage(config.MORTAL_ALIAS))
        logger.info(messages.getNotRegisteredLog(config.MORTAL_ALIAS, playerName, players[playerName].mortal.username))
        return ConversationHandler.END

    update.callback_query.message.reply_text(messages.getPlayerMessage(config.MORTAL_ALIAS))
    return MORTAL

def sendAngel(update: Update, context: CallbackContext):
    playerName = update.message.chat.username.lower()
    context.bot.send_message(
                        text = messages.getReceivedMessage(config.MORTAL_ALIAS, update.message.text),
                        chat_id = players[playerName].angel.chat_id)

    update.message.reply_text(messages.MESSAGE_SENT)

    logger.info(messages.getSentMessageLog(config.ANGEL_ALIAS, playerName, players[playerName].angel.username))

    return ConversationHandler.END

def sendMortal(update: Update, context: CallbackContext):
    playerName = update.message.chat.username.lower()
    context.bot.send_message(
                        text = messages.getReceivedMessage(config.ANGEL_ALIAS, update.message.text),
                        chat_id = players[playerName].mortal.chat_id)

    update.message.reply_text(messages.MESSAGE_SENT)

    logger.info(messages.getSentMessageLog(config.MORTAL_ALIAS, playerName, players[playerName].mortal.username))

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    logger.info(f"{update.message.chat.username} canceled the conversation.")
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
    dispatcher.add_handler(CommandHandler("reloadplayers", reload_command))

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
    try:
        main()
    finally:
        player.saveChatID(players)
        logger.info(f'Player chat ids have been saved in {config.CHAT_ID_JSON}')