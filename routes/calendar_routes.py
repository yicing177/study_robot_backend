from flask import Blueprint,jsonify,request,g
from services.calendar_service import create_calendar, get_calendars_by_user, delete_calendar, update_calendar
from routes.auth_routes import login_required
calendar_bp = Blueprint("calendar",__name__)


@calendar_bp.route("/calendar", methods=["POST"])
@login_required
def create():
    
    user_id = g.user_id #知道誰上傳的

    data = request.json
    if not data:
        return jsonify({"error": "沒有收到 JSON 資料"}), 400

    try:
        calendar = create_calendar(data)
        print(" 成功建立 calendar：", calendar.to_dict()) 
        return jsonify({
            "message" : f"{user_id}上傳成功", 
            "calendar" : calendar.to_dict()
        }) , 201
    except Exception as e:
        print(" 錯誤原因：", e)
        return jsonify({"error" : str(e)}), 400
    
@calendar_bp.route("/calendar", methods=["GET"])
@login_required
def get_by_user():
    user_id = g.user_id
    if not user_id:
        return jsonify({"error" : "沒有user_id"}) ,400
    try:
        calendars = get_calendars_by_user(user_id)
        return jsonify([c.to_dict() for c in calendars]), 200
    except Exception as e :
        return jsonify({"error" : str(e)}) ,400

@calendar_bp.route("/calendar/<calendar_id>", methods=["DELETE"])
@login_required
def delete(calendar_id):
    if not calendar_id:# calendar_id 直接作為參數傳遞 從url提取
        return jsonify({"error":"沒有這個行事曆"}), 
    try:
        delete_calendar(calendar_id, g.user_id)
        return jsonify({"message" : "成功刪除calendar"}), 201
    except Exception as e :
        return jsonify({"error" : str(e)}), 400


@calendar_bp.route("/calendar", methods = ["PATCH"])

def update():
    user_id = request.args.get("user_id")# 確認 user_id 和 calendar_id 是否存在
    calendar_id = request.args.get("calendar_id")
    if not user_id or not calendar_id:
        return jsonify({"error" : "empty"}) , 400

    data = request.json
    
    if not data:
        return jsonify({"error" : "missing update data"})
    try:
        update_calendar(user_id, calendar_id, data)
        return jsonify({"message":"update success",}), 200
    except Exception as e:
        return jsonify({"error" : str(e)}),400

    