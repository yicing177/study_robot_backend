from firebase_config import db
from datetime import datetime
from models.calendar import Calendar
import uuid

def create_calendar(data):
    calendar_id =str(uuid.uuid4())
    data["calendar_id"] = calendar_id
    calendar = Calendar.from_dict(data) #建python class 
    db.collection("calendars").document(calendar_id).set(calendar.to_dict())#python class 轉成 dict
    return calendar

def get_calendars_by_user(user_id):
    docs=db.collection("calendars").where("user_id","==",user_id).stream()
    return [Calendar.from_dict(doc.to_dict()) for doc in docs]

def delete_calendar(calendar_id):
    db.collection("calendars").document(calendar_id).delete()

def update_calendar(calendar_id, data):
    doc_ref = db.collection("calendars").document(calendar_id)
    doc_ref.update(data)
    