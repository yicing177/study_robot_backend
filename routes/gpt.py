import uuid
import datetime

from flask import Blueprint, request, jsonify,g
from openai_api.gpt_service import (
    get_gpt_reply,
    summarize_chat,
    reset_chat_history,
    get_text_from_stt_file,
    conversation_pool,
    generate_conversation_title
)
from routes.auth_routes import login_required 
from openai_api.gpt_highlight import handle_highlight_action, generate_tts_for_text
from openai_api.firebase_utils import save_conversation_metadata

from firebase_admin import firestore
db = firestore.client()

gpt_bp = Blueprint('gpt', __name__)

@gpt_bp.route('/ask', methods=['POST'])
@login_required
def ask():
    data = request.get_json()
    user_input = data.get('message') or data.get('text')
    if not user_input:
        return jsonify({"error": "請提供 'message' 或 'text' 欄位"}), 400

    user_id = g.user_id
    conversation_id = data.get("conversation_id")  # 可選參數
    result = get_gpt_reply(user_input, user_id, conversation_id)
    return jsonify(result)


@gpt_bp.route('/ask_from_stt', methods=['POST'])  # 從 STT JSON 自動抓輸入
@login_required
def ask_from_stt():
    data = request.get_json()
    filepath = data.get('filepath')  # e.g., dir_stt_result/20240504_xx.json
    if not filepath:
        return jsonify({"error": "請提供 STT 結果的 filepath"}), 400

    user_id = g.user_id
    user_input = get_text_from_stt_file(filepath)
    if not user_input:
        return jsonify({"error": "STT 檔案中找不到 transcript"}), 400

    reply = get_gpt_reply(user_input, user_id)
    return jsonify({"reply": reply})

# 根據conversation_id做總結
@gpt_bp.route('/summarize', methods=['POST'])
@login_required
def summarize():
    user_id = g.user_id
    conversation_id = request.get_json().get("conversation_id")

    if not conversation_id:
        return jsonify({"error": "請提供 conversation_id"}), 400
    
    summary = summarize_chat(user_id, conversation_id)
    return jsonify({"summary": summary})

# 開啟新對話
@gpt_bp.route('/reset', methods=['POST'])
@login_required
def reset_chat():
    user_id = g.user_id
    reset_chat_history(user_id)
    return jsonify({"message": "新的對話已開始！"})

# 取得所有summary的清單
@gpt_bp.route('/history', methods=['GET'])
@login_required
def get_history():
    user_id = g.user_id
    conversations_ref = db.collection("Users").document(user_id).collection("Conversations")
    docs = conversations_ref.stream()

    summaries = []
    for doc in docs:
        data = doc.to_dict()
        summaries.append({
            "conversation_id": doc.id,
            "title": data.get("title", "未命名對話"),
            "summary": data.get("summary", "")
        })

    return jsonify({"summaries": summaries}), 200

@gpt_bp.route('/highlight_action', methods=['POST'])
def highlight_action():
    data = request.get_json()
    user_id = data.get("user_id", "unknown")
    text = data.get("text", "").strip()
    action = data.get("action", "read")

    if not text:
        return jsonify({"error": "缺少 text"}), 400

    # 如果是朗讀（TTS），走 TTS 流程，不用經過 handle_highlight_action
    if action == "read":
        try:
            tts_file = generate_tts_for_text(text, user_id)
            return jsonify({"tts_url": f"/dir_tts_result/{tts_file}"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # 其他 action（如翻譯、例句），才呼叫 handle_highlight_action
    try:
        reply = handle_highlight_action(text, action)
        return jsonify({"reply": reply}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 開始一個新的對話    
@gpt_bp.route('/start_conversation', methods=['POST'])
@login_required
def start_conversation():
    data = request.get_json()
    user_id = g.user_id
    initial_message = data.get("initial_message", "")

    # 建立新的對話物件
    conv = conversation_pool.get_or_create(user_id)

    if initial_message:

        # 1. 呼叫 GPT 回應（會自動 append assistant 的回覆）
        from openai_api.gpt_service import get_gpt_reply
        reply = get_gpt_reply(initial_message, user_id, conv.conversation_id)

        # 2. 自動產生標題
        title = generate_conversation_title(initial_message)
        conv.title = title
        save_conversation_metadata(user_id, conv.conversation_id, conv.title)
    else:
        # 沒提供初始訊息 → 預設用日期當標題
        date_str = datetime.datetime.now().strftime("%m/%d")
        conv.title = f"對話 {date_str}"
        save_conversation_metadata(user_id, conv.conversation_id, conv.title)  # ✅加這行

    return jsonify({
        "conversation_id": conv.conversation_id,
        "title": conv.title
    }), 200

# 印出指定用戶所有對話列表
@gpt_bp.route('/conversations', methods=['POST'])
@login_required
def list_conversations():
    user_id = g.user_id
    conversations_ref = db.collection("Users").document(user_id).collection("Conversations")

    docs = conversations_ref.stream()
    result = []
    for doc in docs:
        data = doc.to_dict()
        result.append({
            "conversation_id": doc.id,
            "title": data.get("title", "未命名對話")
        })

    return jsonify({"conversations": result}), 200

# 取得使用者指定對話的完整對話紀錄、conversation_id、標題、summary
@gpt_bp.route('/get_conversation', methods=['POST'])
@login_required
def get_conversation():
    data = request.get_json()
    user_id = g.user_id
    conversation_id = data.get("conversation_id")

    if not conversation_id:
        return jsonify({"error": "請提供 conversation_id"}), 400

    # 讀取 Messages
    messages_ref = db.collection("Users").document(user_id).collection("Conversations") \
                     .document(conversation_id).collection("Messages")
    messages = []
    for doc in messages_ref.stream():
        msg = doc.to_dict()
        messages.append({
            "role": msg.get("role"),
            "content": msg.get("content"),
            "timestamp": msg.get("timestamp")
        })

    # 按照 timestamp 排序
    messages.sort(key=lambda m: m.get("timestamp", ""))

    # 讀取 summary 與 title
    conv_ref = db.collection("Users").document(user_id).collection("Conversations").document(conversation_id)
    conv_data = conv_ref.get().to_dict() if conv_ref.get().exists else {}

    return jsonify({
        "conversation_id": conversation_id,
        "title": conv_data.get("title", "未命名對話"),
        "messages": messages,
        "summary": conv_data.get("summary", "")
    }), 200
