from flask import Blueprint, request, jsonify
from openai_api.gpt_service import (
    get_gpt_reply,
    summarize_chat,
    reset_chat_history,
    get_user_summaries,
    get_text_from_stt_file
)

gpt_bp = Blueprint('gpt', __name__)

@gpt_bp.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_input = data.get('message') or data.get('text')
    if not user_input:
        return jsonify({"error": "請提供 'message' 或 'text' 欄位"}), 400

    user_id = data.get('user_id', 'unknown')
    result = get_gpt_reply(user_input, user_id)
    return jsonify(result)


@gpt_bp.route('/ask_from_stt', methods=['POST'])  # 從 STT JSON 自動抓輸入
def ask_from_stt():
    data = request.get_json()
    filepath = data.get('filepath')  # e.g., dir_stt_result/20240504_xxx.json
    if not filepath:
        return jsonify({"error": "請提供 STT 結果的 filepath"}), 400

    user_id = data.get('user_id', 'unknown')
    user_input = get_text_from_stt_file(filepath)
    if not user_input:
        return jsonify({"error": "STT 檔案中找不到 transcript"}), 400

    reply = get_gpt_reply(user_input, user_id)
    return jsonify({"reply": reply})

@gpt_bp.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    user_id = data.get('user_id', 'unknown')
    summary = summarize_chat(user_id)
    return jsonify({"summary": summary})

@gpt_bp.route('/reset', methods=['POST'])
def reset_chat():
    reset_chat_history()
    return jsonify({"message": "新的對話已開始！"})

@gpt_bp.route('/history', methods=['POST'])
def get_history():
    data = request.get_json()
    user_id = data.get('user_id', 'unknown')
    summaries = get_user_summaries(user_id)
    return jsonify({"summaries": summaries})
