import azure.cognitiveservices.speech as speechsdk
from azure_speech_config import get_speech_config

def test_tts():
    try:
        speech_config = get_speech_config()
        audio_output = speechsdk.audio.AudioOutputConfig(filename="test_output.wav")
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)

        text = "你好，Azure 語音服務測試成功！"
        print(f"合成文字：{text}")
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("✅ 成功產生語音檔：test_output.wav")
        else:
            print(f"語音合成失敗，原因：{result.reason}")

    except Exception as e:
        print(f"發生錯誤：{e}")

if __name__ == "__main__":
    test_tts()
