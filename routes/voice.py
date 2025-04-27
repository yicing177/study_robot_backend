from flask import Blueprint, request, jsonify, send_file
import os
import uuid
import azure.cognitiveservices.speech as speechsdk
from azure_speech_config import get_speech_config
import json
from datetime import datetime

voice_bp = Blueprint("voice", __name__)

AUDIO_FOLDER = "dir_audio"
STT_UPLOADS_FOLDER = "dir_stt_result"
TEXT_FOLDER = "dir_text"
TTS_UPLOADS_FOLDER = "dir_tts_result"

@voice_bp.route('/tests')
def tests():
    return "tests4444"


# === 語音轉文字 STT ==
@voice_bp.route("/stt", methods=["POST"])
def stt():
    try:
        filename = request.json.get("filename")  # 例如 test123.wav
        if not filename:
            return jsonify({"error": "請提供音訊檔名"}), 400

        filepath = os.path.join(AUDIO_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({"error": f"找不到檔案：{filename}"}), 404

        #自動辨識音檔為中文或英文
        speech_config = get_speech_config()
        audio_config = speechsdk.audio.AudioConfig(filename=filepath)
        auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "zh-TW"])
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            auto_detect_source_language_config=auto_detect_source_language_config,
            audio_config=audio_config)

        #辨識音檔
        result = recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            transcript = result.text

            #儲存成 json 檔至stt_result
            os.makedirs(STT_UPLOADS_FOLDER, exist_ok=True)  # 確保 stt_result 資料夾存在
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 產生時間字串
            output_filename = f"dir_stt_result/{timestamp}.json"

            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump({"transcript": transcript}, f, ensure_ascii=False, indent=4)

            return jsonify({"transcript": transcript, "file": output_filename})
        
        else:
            return jsonify({"error": "辨識失敗", "reason": str(result.reason)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === 文字轉語音 TTS ===
@voice_bp.route("/tts", methods=["POST"])
def tts():
    try:        
        filename = request.json.get("filename")  # 例如 analyzed_text_001.json
        if not filename:
            return jsonify({"error": "請提供 JSON 檔案名稱"}), 400
        
        filepath = os.path.join(TEXT_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": f"找不到檔案：{filename}"}), 404
        

        # 讀取 JSON 檔
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        text = data.get("text")
        if not text:
            return jsonify({"error": "JSON 檔內沒有 text 欄位"}), 400

        # 呼叫 Azure TTS
        speech_config = get_speech_config()
        os.makedirs(TTS_UPLOADS_FOLDER, exist_ok=True)  # 確保資料夾存在
        output_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        output_path = os.path.join(TTS_UPLOADS_FOLDER, output_filename)

        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        result = synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return jsonify({
                "message": "TTS 成功",
                "file": output_filename
            })
        else:
            return jsonify({"error": "TTS 失敗", "reason": str(result.reason)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

