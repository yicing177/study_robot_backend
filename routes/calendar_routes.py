from flask import Blueprint,jsonify,request
from services.calendar_service import create_calendar, get_calendars_by_user

calendar_bp=Blueprint("calendar",__name__)

@calendar_bp.route("/calendar", methods=["POST"])

def create():
    data = request.json
    try:
        calendar = create_calendar(data)
        return jsonify({"messenge" : "上傳成功", "calendar" : calendar.to_dicit()}) , 201
    except Exception as e:
        return jsonify({"error" : str("")}), 404
    
@calendar_bp.route("/calendar", methods=["GET"])

def get_by_user():
    user_id = request.args.get(user_id)
    if not user_id:
        return jsonify({"error" : "沒有user_id"}) ,400
    try:
        calendars = get_calendars_by_user(user_id)
        return jsonify([c.to_dict() for c in calendars])
    except Exception as e :
        return({"error" : str(e)}) ,400


 
    