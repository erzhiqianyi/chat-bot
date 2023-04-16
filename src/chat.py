import logging
from ai import build_property, send_chat, send_transcribe
from voice import text_to_speech_azure

from pydub import AudioSegment

import os
from dotenv import load_dotenv

load_dotenv()
default_voice_path = os.getenv("voice_path")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

mode_default = "Assistant"
mode_customize = "Customize"
mode_read_aloud = "ReadAloud"

messages = {}
context = {}
mode = {}
start_sequence = "\nHuman: "
end_sequence = "\nAI: "
kimi = "君:"
ai = "AI:"
def repeat_chat(user_id, chat_id, text_message):
    add_history(user_id, text_message, None)
    logging.info(user_id + " end chat" + chat_id + " repeat \n")
    return text_message


def gpt_chat(user_id, chat_id, text_message):
    history = get_chat_history(user_id)
    chat_property, max_tokens = build_property(chat_id, text_message, history)
    chat_response = send_chat(chat_id, chat_property, max_tokens=max_tokens)
    add_history(user_id, text_message, chat_response)
    logging.info(user_id + " end chat" + chat_id + " with  response \n" + chat_response)
    return chat_response


mode_processor = {
    mode_default: gpt_chat,
    mode_read_aloud: repeat_chat
}


def enable_chat_context(user_id):
    context[user_id] = True


def disable_chat_context(user_id):
    context[user_id] = False
    clear_history(user_id)


def add_message(user_id, message):
    user_message = messages.get(user_id, [])
    user_message.append(message)
    messages[user_id] = user_message


def add_start_message(user_id, message):
    logging.info("start add new start message ")
    start_message = start_sequence + message
    add_message(user_id, start_message)
    logging.info("end add new start message ")


def add_end_message(user_id, message):
    logging.info("start add new response message ")
    if message:
        end_message = end_sequence + message
        add_message(user_id, end_message)
    logging.info("end add new response message ")


def show_history_message(user_id):
    history_message = get_history_message(user_id)
    history_message = "\n".join(history_message)
    history_message = history_message.replace(start_sequence,kimi).replace(end_sequence,ai)
    return history_message


def get_history_message(user_id):
    user_message = messages.get(user_id, [])
    return user_message


def clear_history(user_id):
    messages[user_id] = []


def get_context(user_id):
    return context.get(user_id, False)


def get_mode(user_id):
    return mode.get(user_id, mode_default)


def change_mode(user_id, mode_name=mode_default):
    mode[user_id] = mode_name


def get_chat_history(user_id):
    is_context_enable = get_context(user_id)
    logging.info(user_id + " context status " + str(is_context_enable))
    history = get_history_message(user_id) if is_context_enable else []
    return history


def add_history(user_id, text_message, chat_response):
    add_start_message(user_id, text_message)
    add_end_message(user_id, chat_response)


def chat_with_gpt(user_id, chat_id, text_message):
    mode = get_mode(user_id)
    logging.info(user_id + " start chat  " + chat_id + " in " + mode)
    processor = mode_processor.get(mode)
    chat_response = processor(user_id, chat_id, text_message)
    return chat_response


def format_bot_text_response(chat_id, original_message, response_message):
    logging.info(chat_id + " start format bot text response ")
    bot_message = "君:" + original_message + "\n\n" + response_message
    logging.info(chat_id + "end format bot text response \n" + bot_message)
    return bot_message


def transcribe_bot_voice(chat_id, voice_path):
    logging.info(chat_id + " start transcribe voice message")
    logging.info(chat_id + " start converter ogg to mp3")
    audio = AudioSegment.from_file(voice_path, format="ogg")
    transcribe_file = default_voice_path + chat_id + "-input.mp3"
    audio.export(transcribe_file, format="mp3")
    logging.info(chat_id + " end converter ogg to mp3")
    transcript = send_transcribe(chat_id, transcribe_file)
    logging.info(chat_id + " end transcribe voice message \n" + transcript)
    return transcript


def build_bot_voice_response(chat_id, response_message):
    logging.info(chat_id + " start build bot voice response ")
    voice_path = text_to_speech_azure(chat_id, response_message)
    voice_file = open(voice_path, "rb")
    logging.info(chat_id + " end build bot voice response ")
    return voice_file


if __name__ == '__main__':
    chat_message_id = "chat:" + str(1)
    message = "こんにちは"
    chat_message = chat_with_gpt("user:01", chat_message_id, message)
    logging.info("message is " + chat_message)
