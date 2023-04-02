import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler

from chat import chat_with_gpt, format_bot_text_response, build_bot_voice_response, transcribe_bot_voice, clear_history, \
    get_history_message

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
    user_id = str(update.effective_user.id)
    history = get_history_message(user_id)
    history_message = "\n".join(history)
    clear_history(user_id)
    message = "history is\n" + history_message + "clear success"
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
    clear_handler = CommandHandler('clear', clear)
    text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), process_text_message)
    audio_handler = MessageHandler(filters.VOICE, process_voice_message)

    application.add_handler(clear_handler)
    application.add_handler(text_handler)
    application.add_handler(audio_handler)

    application.run_polling()
