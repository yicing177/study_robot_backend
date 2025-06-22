from flask import Blueprint, request, jsonify
from openai_api.gpt_quiz_service import generate_quiz_from_chat_history
from openai_api.gpt_service import all_chat_history
from openai_api.gpt_quiz_service import generate_quiz_from_material_text

from routes.auth_routes import login_required

quiz_bp = Blueprint("quiz", __name__)

# 根據對話產生題目
@quiz_bp.route("/generate_quiz", methods=["POST"])
@login_required
def generate_quiz():
    try:
        data = request.get_json()
        num_questions = data.get("num_questions", 3)
        difficulty = data.get("difficulty", "medium")
        quiz = generate_quiz_from_chat_history(all_chat_history, num_questions)
        return jsonify({"quiz": quiz}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 提交答案
@quiz_bp.route("/submit", methods=["POST"])
@login_required
def submit_quiz():
    try:
        data = request.get_json()
        questions = data.get("questions", [])
        answers = data.get("answers", [])  # 使用者提交的答案陣列

        if not questions or not answers or len(questions) != len(answers):
            return jsonify({"error": "題目與答案數量不符"}), 400

        results = []
        score = 0
        for q, user_ans in zip(questions, answers):
            correct = q.get("answer") == user_ans
            if correct:
                score += 1
            results.append({
                "question": q.get("question"),
                "user_answer": user_ans,
                "correct_answer": q.get("answer"),
                "explanation": q.get("explanation"),
                "correct": correct
            })

        return jsonify({
            "score": score,
            "total": len(questions),
            "details": results
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# 根據教材出題
@quiz_bp.route("/generate_quiz_from_material", methods=["POST"])
def generate_quiz_from_material():
    try:
        data = request.get_json()
        material_text = data.get("text", "")
        num_questions = int(data.get("num_questions", 3))
        difficulty = data.get("difficulty", "medium")

        quiz = generate_quiz_from_material_text(material_text, num_questions, difficulty)
        return jsonify({"quiz": quiz}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
