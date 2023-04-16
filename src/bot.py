import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler

from chat import *

load_dotenv()
token = os.getenv("telegram_token")
default_voice_path = os.getenv("voice_path")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def log_chat_info(update: Update, message_type):
    chat_id = "chat:" + str(update.message.id)
    logging.info("process " + message_type + " for " + chat_id)
    logging.info("user name: " + str(update.message.chat.first_name))
    return chat_id


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_chat_info(update, "clear")
    user_id = str(update.effective_user.id)
    history = show_history_message(user_id)
    clear_history(user_id)
    message = "history is\n" + history + "clear success"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def read_aloud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_chat_info(update, "read aloud")
    message = "start read aloud "
    user_id = str(update.effective_user.id)
    change_mode(user_id, mode_read_aloud)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def normal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_chat_info(update, "normal")
    user_id = str(update.effective_user.id)
    message = "assistant mode"
    change_mode(user_id, mode_default)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def clear_read_aloud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = log_chat_info(update, "clear read aloud")
    user_id = str(update.effective_user.id)
    history = show_history_message(user_id)
    clear_history(user_id)
    message = "your  read  aloud content is \n" + history
    history = history.replace(kimi, "").replace(ai,"")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    voice_message = build_bot_voice_response(chat_id, history)
    await context.bot.send_voice(chat_id=update.effective_chat.id, voice=voice_message)


async def process_enable_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_chat_info(update, "enable_context")
    user_id = str(update.effective_user.id)
    enable_chat_context(user_id)
    message = "enable context success"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def process_disable_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_chat_info(update, "disable_context")
    user_id = str(update.effective_user.id)
    disable_chat_context(user_id)
    message = "disable context success"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def response(update: Update, chat_id, original_message, response, context):
    response_message = format_bot_text_response(chat_id, original_message, response)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)
    voice_message = build_bot_voice_response(chat_id, response)
    await context.bot.send_voice(chat_id=update.effective_chat.id, voice=voice_message)


async def text_chat(update: Update, chat_id, message, context):
    user_id = str(update.effective_user.id)
    chat_response = chat_with_gpt(user_id, chat_id, message)
    await response(update, chat_id, message, chat_response, context)


async def voice_to_text(update: Update, chat_id, context):
    file_id = update.message.voice.file_id
    new_file = await context.bot.getFile(file_id)
    original_voice_file = default_voice_path + chat_id + "-input" + ".ogg"
    voice_path = await new_file.download_to_drive(original_voice_file)
    transcript = transcribe_bot_voice(chat_id, voice_path)
    return transcript


async def process_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = log_chat_info(update, "text")
    original_message = update.message.text
    await text_chat(update, chat_id, original_message, context)


async def process_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = log_chat_info(update, "voice")
    text_message = await voice_to_text(update, chat_id, context)
    await text_chat(update, chat_id, text_message, context)


if __name__ == '__main__':
    application = ApplicationBuilder().token(token).read_timeout(20) \
        .get_updates_read_timeout(20).connect_timeout(20) \
        .pool_timeout(20).build()
    enable_context_handler = CommandHandler('enable', process_enable_context)
    disable_context_handler = CommandHandler('disable', process_disable_context)
    clear_handler = CommandHandler('clear', clear)
    read_aloud_handler = CommandHandler('read', read_aloud)
    clear_read_aloud_handler = CommandHandler('clearread', clear_read_aloud)
    normal_mode_handler = CommandHandler('normal', normal)
    text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), process_text_message)
    audio_handler = MessageHandler(filters.VOICE, process_voice_message)

    application.add_handler(clear_handler)
    application.add_handler(enable_context_handler)
    application.add_handler(disable_context_handler)
    application.add_handler(read_aloud_handler)
    application.add_handler(clear_read_aloud_handler)
    application.add_handler(normal_mode_handler)
    application.add_handler(text_handler)
    application.add_handler(audio_handler)

    application.run_polling()
