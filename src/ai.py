import logging
import os
from dotenv import load_dotenv
import openai

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()
openai.api_key = os.getenv("open_ai_key")
default_whisper_model = os.getenv("whisper_model")
default_text_model = os.getenv("text_model")
default_max_tokens = int(os.getenv("max_tokens"))
max_able_tokens = 1500


def send_transcribe(chat_id, file, model=default_whisper_model):
    logging.info(chat_id + " start transcribe: " + file)
    audio_file = open(file, "rb")
    transcript = openai.Audio.transcribe(model, audio_file,
                                         api_key=None,
                                         api_base=None,
                                         api_type=None,
                                         api_version=None,
                                         organization=None,
                                         prompt="Audio Langauge is Japanese,transcribe is Japanese",
                                         response_format='json')
    transcript_value = transcript.to_dict().get('text')
    logging.info(chat_id + " end transcribe: " + file + " text is: " + transcript_value)
    return transcript_value


def send_chat(chat_id, prompt, text_model=default_text_model, max_tokens=default_max_tokens):
    logging.info(chat_id + " start chat message is:")
    logging.info(chat_id + ": " + prompt)
    response = openai.Completion.create(
        model=text_model,
        prompt=prompt,
        temperature=0.9,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )
    ai_response = response.get('choices')[0].get('text')
    logging.info(chat_id + " end chat,response is\n " + ai_response)
    return ai_response


def calculate_token(history):
    max_tokens = (len(history) + 1) * default_max_tokens
    max_tokens = 1000 if max_tokens > max_able_tokens else max_tokens
    return max_tokens


def build_property(chat_id, human, history=[]):
    format_prompt = """AI assistant's response translate to Japanese."""
    prompt = """The following is a conversation with an AI assistant.
    The assistant is helpful, creative, clever,  very friendly and a little humor. """
    restart_sequence = "\nHuman: "
    start_sequence = "\nAI:"
    history = history[-30:]
    history_message = " ".join(history)
    prompt = prompt + format_prompt + history_message + restart_sequence + human + start_sequence
    max_tokens = calculate_token(history)
    logging.info(chat_id + " prompt is:" + prompt)
    return prompt, max_tokens


if __name__ == '__main__':
    chat_message_id = "chat:001"
    chat_text = "僕は誰ですか"
    logging.info("voice to text is " + chat_text)
    chat_history = [
        "\nHuman：こんにちは, 私はリンクです",
        "\nAI:はい、私はあなたがリンクさんだと理解しています。"
    ]
    chat_prompt, max_tokens = build_property(chat_message_id, chat_text, chat_history)
    logging.info("chat prompt is " + chat_prompt)
    chat_response = send_chat(chat_message_id, chat_prompt, max_tokens=max_tokens)
    logging.info("chat response is " + chat_response)
