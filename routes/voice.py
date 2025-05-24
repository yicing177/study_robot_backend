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

# 儲存 endpoint
@voice_bp.route("/upload_audio", methods=["POST"])
def upload_audio():
    try:
        file = request.files["file"]
        filename = file.filename
        save_path = os.path.join(AUDIO_FOLDER, filename)
        file.save(save_path)
        return jsonify({"message": "上傳成功", "filename": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        # 支援直接傳文字（優先處理）
        text = request.json.get("text")

        if not text:
            # 如果沒傳文字，則檢查 filename → 讀檔案取得文字
            filename = request.json.get("filename")
            if not filename:
                return jsonify({"error": "請提供 'text' 或 'filename'"}), 400

            filepath = os.path.join(TEXT_FOLDER, filename)
            if not os.path.exists(filepath):
                return jsonify({"error": f"找不到檔案：{filename}"}), 404

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                text = data.get("text")

            if not text:
                return jsonify({"error": "JSON 檔內沒有 'text' 欄位"}), 400

        # 呼叫 Azure TTS
        speech_config = get_speech_config()
        os.makedirs(TTS_UPLOADS_FOLDER, exist_ok=True)

        output_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        output_path = os.path.join(TTS_UPLOADS_FOLDER, output_filename)

        # 設定語音樣式（可自定義）
        speech_config.speech_synthesis_voice_name = "zh-CN-XiaoshuangNeural"
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



from datetime import datetime

def insert_breaks(text):
    replacements = {
        "。": "。<break time='500ms' strength='strong'/>",
        ".": ".<break time='500ms' strength='strong'/>",
        "，": "，<break time='300ms' strength='medium'/>",
        ",": ",<break time='300ms' strength='medium'/>",
        "：": "：<break time='200ms' strength='medium'/>",
        ":": ":<break time='200ms' strength='medium'/>",
        "、": "、<break time='200ms' strength='weak'/>",
        "？": "？<break time='500ms' strength='strong'/>",
        "?": "?<break time='500ms' strength='strong'/>",
        "！": "！<break time='500ms' strength='strong'/>",
        "!": "!<break time='500ms' strength='strong'/>"
    }
    for mark, pause in replacements.items():
        text = text.replace(mark, pause)
    return text

@voice_bp.route("/tts_ssml", methods=["POST"])
def tts_ssml():
    try:
        req = request.json
        filename = req.get("filename")
        voice = "zh-CN-XiaoxiaoNeural"
        pitch = "+0%"
        volume = "soft"
        xml_lang = voice[:5]  # 自動設定語言

        if not filename or not voice:
            return jsonify({"error": "缺少必要參數 filename 或 voice"}), 400

        # 讀取 JSON 檔案
        filepath = os.path.join(TEXT_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({"error": f"找不到檔案：{filename}"}), 404

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        text = data.get("text")
        style = data.get("emotion")
        styledegree = str(data.get("style_degree", "1.0"))
        rate_val = data.get("rate", "+0%")
        rate = f"{rate_val}%" if isinstance(rate_val, int) else rate_val

        if not text:
            return jsonify({"error": "JSON 檔內沒有 text 欄位"}), 400

        # 插入 break 停頓標記
        text = insert_breaks(text)

        # 初始化語音設定
        speech_config = get_speech_config()
        speech_config.speech_synthesis_voice_name = voice

        # 檔名
        func_name = f"tts_{style}_{styledegree}_{rate}".replace('+', 'p').replace('%', '').replace(' ', '')
        output_filename = f"{func_name}.wav"
        output_path = os.path.join(TTS_UPLOADS_FOLDER, output_filename)
        os.makedirs(TTS_UPLOADS_FOLDER, exist_ok=True)

        # 建立 SSML
        if style:
            ssml = f"""
            <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'
                   xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='{xml_lang}'>
              <voice name='{voice}'>
                <mstts:express-as style='{style}' styledegree='{styledegree}'>
                  <prosody rate='{rate}' pitch='{pitch}' volume='{volume}'>
                    {text}
                  </prosody>
                </mstts:express-as>
              </voice>
            </speak>
            """
        else:
            ssml = f"""
            <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{xml_lang}'>
              <voice name='{voice}'>
                <prosody rate='{rate}' pitch='{pitch}' volume='{volume}'>
                  {text}
                </prosody>
              </voice>
            </speak>
            """

        # 執行轉換
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_ssml_async(ssml).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return jsonify({"message": "TTS SSML 成功", "file": output_filename})
        else:
            return jsonify({"error": "TTS 失敗", "reason": str(result.reason)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

