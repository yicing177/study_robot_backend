from flask import Blueprint, request, jsonify, send_file
import os
import uuid
import azure.cognitiveservices.speech as speechsdk
from azure_speech_config import get_speech_config

voice_bp = Blueprint("routes", __name__)

STATIC_FOLDER = "static"
UPLOADS_FOLDER = "uploads"


@voice_bp.route('tests')
def tests():
    return "tests"


# === 語音轉文字 STT ==
@voice_bp.route("/stt_from_static", methods=["POST"])
def stt_from_static():
    try:
        filename = request.json.get("filename")  # 例如 test123.wav
        if not filename:
            return jsonify({"error": "請提供音訊檔名"}), 400

        filepath = os.path.join(STATIC_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({"error": f"找不到檔案：{filename}"}), 404

        speech_config = get_speech_config()
        audio_config = speechsdk.audio.AudioConfig(filename=filepath)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        result = recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return jsonify({"transcript": result.text})
        else:
            return jsonify({"error": "辨識失敗", "reason": str(result.reason)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === 文字轉語音 TTS ===
@voice_bp.route("/tts_from_text", methods=["POST"])
def tts_from_text():
    try:
        text = request.json.get("text")
        if not text:
            return jsonify({"error": "請提供文字內容"}), 400

        speech_config = get_speech_config()
        filename = f"{uuid.uuid4()}.wav"
        output_path = os.path.join(UPLOADS_FOLDER, filename)

        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return jsonify({"file": filename})
        else:
            return jsonify({"error": "TTS 失敗", "reason": str(result.reason)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
