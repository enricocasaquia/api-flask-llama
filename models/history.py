from sql_alchemy import db
from datetime import datetime

class ChatHistoryModel(db.Model):
    __tablename__ = 'TB_CHAT_HISTORY'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('TB_USER.id'), nullable = False)
    role = db.Column(db.String(20), nullable = False)
    content = db.Column(db.Text, nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default=datetime.now())

    def __init__(self, user_id, role, content):
        self.user_id = user_id
        self.role = role
        self.content = content

    @classmethod
    def find_history_user(cls, user_id, limit=10):
        return cls.query.filter_by(user_id=user_id)\
                        .order_by(cls.timestamp.asc())\
                        .limit(limit).all()

    def insert_history(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def delete_history_by_user(cls, user_id):
        cls.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return True