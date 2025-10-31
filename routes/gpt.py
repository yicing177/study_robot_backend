import uuid
from datetime import datetime 
from flask_cors import cross_origin

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
from openai_api.firebase_utils import save_conversation_metadata,save_message_to_firestore
from models.chatmessage import Chatmessage
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
    print("使用者傳來的 conversation_id：", conversation_id)
    # # ✅ 儲存使用者訊息
    # save_message_to_firestore(user_id, conversation_id, {
    #     "role": "user",
    #     "content": user_input,
    #     "timestamp": datetime.utcnow().isoformat()
    # })

    # ✅ 呼叫 GPT 並拿到 assistant 回覆
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
    

    conversation_id = data.get("conversation_id")
    user_msg = Chatmessage (
        conversation_id = conversation_id,
        role = "user",
        content = user_input,
        timestamp = datetime.now().isoformat(),
    )
    reply = get_gpt_reply(user_input, user_id, conversation_id)

    bot_msg = Chatmessage (
        conversation_id = data.get("conversation_id"),
        role = "bot",
        content = reply.get("reply"),
        timestamp = datetime.now().isoformat(),
    )
    return jsonify({"reply": reply})

# 根據conversation_id做總結
@gpt_bp.route('/summarize', methods=['POST'])
@cross_origin(
    origins="http://localhost:5173",
    methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=True,
)
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
    new_conv = reset_chat_history(user_id)  # 改為「拿到新 conv 物件」
    return jsonify({
        "message": "新的對話已開始！",
        "conversation_id": new_conv.conversation_id,
        "title": new_conv.title
    }), 200


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
    print("📥 使用者初始訊息：", initial_message)

    # 建立新的對話物件
    conv = conversation_pool.get_or_create(user_id)

    if initial_message:

        # 1. 呼叫 GPT 回應（會自動 append assistant 的回覆）
        from openai_api.gpt_service import get_gpt_reply
        reply = get_gpt_reply(initial_message, user_id, conv.conversation_id)

        # 2. 自動產生標題
        title = generate_conversation_title(initial_message)
        print("⭐️ 產生的標題：", title)
        conv.title = title

        save_conversation_metadata(user_id, conv.conversation_id,conv.title, conv.create_at)
        print("✅ 使用 initial_message 產生 GPT 回覆與標題")
    else:
        # 沒提供初始訊息 → 預設用日期當標題
        date_str = datetime.datetime.now().strftime("%m/%d")
        conv.title = f"對話 {date_str}"
        #save_conversation_metadata(user_id, conv.conversation_id, conv.title)  # ✅加這行
        print("✅ 已儲存標題到 Firestore")
        print("📅 沒有訊息，使用預設日期標題")
    return jsonify({
        "conversation_id": conv.conversation_id,
        "title": conv.title,
        "reply": reply.get("reply")  # ← 把 GPT 回覆也傳回去
    }), 200

# 印出指定用戶所有對話列表
@gpt_bp.route('/conversations', methods=['GET'])
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
        if not msg.get("timestamp"):
            continue
        messages.append({
            "role": msg.get("role"),
            "content": msg.get("content"),
            "timestamp": msg.get("timestamp")
        })


    # 按照 timestamp 排序（過濾掉無 timestamp 的訊息）
    valid_messages = [m for m in messages if m.get("timestamp")]
    valid_messages.sort(key=lambda m: m["timestamp"])

    # 讀取 summary 與 title
    conv_ref = db.collection("Users").document(user_id).collection("Conversations").document(conversation_id)
    conv_data = conv_ref.get().to_dict() if conv_ref.get().exists else {}

    return jsonify({
        "conversation_id": conversation_id,
        "title": conv_data.get("title", "未命名對話"),
        "messages": valid_messages,
        "summary": conv_data.get("summary", "")
    }), 200

@gpt_bp.route('/update_title', methods=['POST', 'OPTIONS'])
@login_required
def update_title():
    data = request.get_json()
    user_id = g.user_id
    conversation_id = data.get("conversation_id")
    new_title = data.get("title")

    conv_ref = db.collection("Users").document(user_id).collection("Conversations") \
                     .document(conversation_id)
    
    conv_ref.update({"title":new_title})

    return jsonify({"ok": True, "title": new_title, "conversation_id": conversation_id}), 200

