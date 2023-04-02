import logging
import os
from dotenv import load_dotenv

import azure.cognitiveservices.speech as speechsdk

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()
speech_key = os.getenv("speech_key")
service_region = os.getenv("service_region")
default_voice_name = os.getenv("voice_name")
default_voice_path = os.getenv("voice_path")


def text_to_speech_azure(chat_id, text, voice_name=default_voice_name):
    logging.info(chat_id + " start speech: " + text)
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = voice_name
    voice_file = default_voice_path + chat_id + "-output" + ".mp3"
    audio_config = speechsdk.audio.AudioOutputConfig(filename=voice_file)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    speech_synthesizer.speak_text_async(text).get()
    logging.info(chat_id + " end speech to " + voice_file)
    return voice_file

def speech_to_text():
    pass

if __name__ == '__main__':
    text = "コンバンワ！ 今日のことをどう思いますか"
    message_id = "1"
    logging.info("service region: " + service_region)
    logging.info("default voice name: " + default_voice_name)
    voice_result = text_to_speech_azure(message_id, text)
