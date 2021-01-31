import logging
import player

from config import ANGEL_ALIAS, MORTAL_ALIAS, ANGEL_BOT_TOKEN

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler

CHOOSING, ANGEL, MORTAL = range(3)

helpText = f'Use /send to send a message to your {ANGEL_ALIAS} or {MORTAL_ALIAS} and /cancel to cancel message'

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

players = player.loadPlayers()

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    playerName = update.message.chat.username.lower()
    players[playerName].chat_id = update.message.chat.id

    logger.info(f'{playerName} started the bot with chat_id {players[playerName].chat_id}')
    
    update.message.reply_text(f'Hi! {helpText}')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(helpText)

def send_command(update: Update, context: CallbackContext):
    """Send a message when the command /send is issued."""
    if players[update.message.chat.username.lower()].chat_id is None:
        update.message.reply_text('Sorry an error occured please type /start again')
        return ConversationHandler.END

    send_menu = [[InlineKeyboardButton(ANGEL_ALIAS, callback_data='angel')],
                 [InlineKeyboardButton(MORTAL_ALIAS, callback_data='mortal')]]
    reply_markup = InlineKeyboardMarkup(send_menu)
    update.message.reply_text('Send my message to my:', reply_markup=reply_markup)

    return CHOOSING

def startAngel(update: Update, context: CallbackContext):
    if players[update.callback_query.message.chat.username.lower()].angel.chat_id is None:
        update.callback_query.message.reply_text(f'Sorry your {ANGEL_ALIAS} has not started this bot')
        return ConversationHandler.END

    update.callback_query.message.reply_text(f'Please type your message to your {ANGEL_ALIAS}')
    return ANGEL

def startMortal(update: Update, context: CallbackContext):
    if players[update.callback_query.message.chat.username.lower()].mortal.chat_id is None:
        update.callback_query.message.reply_text(f'Sorry your {MORTAL_ALIAS} has not started this bot')
        return ConversationHandler.END

    update.callback_query.message.reply_text(f'Please type your message to your {MORTAL_ALIAS}')
    return MORTAL

def sendAngel(update: Update, context: CallbackContext):
    playerName = update.message.chat.username.lower()
    context.bot.send_message(
                        text = f"Message from your {MORTAL_ALIAS}:\n\n{update.message.text}",
                        chat_id = players[playerName].angel.chat_id)

    update.message.reply_text('Message sent!')

    logger.info(f'{playerName} sent a message to their {ANGEL_ALIAS} {players[playerName].angel.username}')

    return ConversationHandler.END

def sendMortal(update: Update, context: CallbackContext):
    playerName = update.message.chat.username.lower()
    context.bot.send_message(
                        text = f"Message from your {ANGEL_ALIAS}:\n\n{update.message.text}",
                        chat_id = players[playerName].mortal.chat_id)

    update.message.reply_text('Message sent!')

    logger.info(f'{playerName} sent a message to their {MORTAL_ALIAS} {players[playerName].mortal.username}')

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    player = update.message.from_user
    logger.info(f"Player {player.first_name} canceled the conversation.")
    update.message.reply_text(
        'Sending message cancelled.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(ANGEL_BOT_TOKEN, use_context=True)

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