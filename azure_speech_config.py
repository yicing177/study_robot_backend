# azure_speech_config.py
import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

load_dotenv()

def get_speech_config():
    key = os.getenv("AZURE_SPEECH_KEY")
    region = os.getenv("AZURE_REGION")
    if not key or not region:
        raise Exception("Azure key or region missing in .env")
    return speechsdk.SpeechConfig(subscription=key, region=region)
