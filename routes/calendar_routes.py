from flask import Blueprint,jsonify,request
from services.calendar_service import create_calendar, get_calendars_by_user

calendar_bp = Blueprint("calendar",__name__)

@calendar_bp.route("/calendar", methods=["POST"])

def create():
    data = request.json
    if not data:
        return jsonify({"error": "沒有收到 JSON 資料"}), 400
    try:
        calendar = create_calendar(data)
        print("✅ 成功建立 calendar：", calendar.to_dict()) 
        return jsonify({"message" : "上傳成功", "calendar" : calendar.to_dict()}) , 201
    except Exception as e:
        print("⚠️ 錯誤原因：", e)
        return jsonify({"error" : str(e)}), 400
    
@calendar_bp.route("/calendar", methods=["GET"])

def get_by_user():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error" : "沒有user_id"}) ,400
    try:
        calendars = get_calendars_by_user(user_id)
        return jsonify([c.to_dict() for c in calendars])
    except Exception as e :
        return({"error" : str(e)}) ,400


 
    