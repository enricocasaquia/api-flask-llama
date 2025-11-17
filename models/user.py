from flask_restful import reqparse
from sql_alchemy import db
import bcrypt
from datetime import datetime
import json

with open("./conf/config.json") as config_json:
    config = json.load(config_json)

class UserModel(db.Model):
    __tablename__ = 'TB_USER'
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(50), nullable = False, unique = True)
    password = db.Column(db.String(255), nullable = False)
    active = db.Column(db.Boolean, nullable = False, default=True)
    create_date = db.Column(db.DateTime, nullable = False, default=datetime.now())
    modify_date = db.Column(db.DateTime, nullable = True, onupdate=datetime.now())
    
    def __init__(self, login, password, active):
        self.login = login
        self.password = self.set_password(password)
        self.active = active
    
    @staticmethod
    def parse_user():
        parameters = reqparse.RequestParser()
        parameters.add_argument('login', type=str, required=True, help='The field login cannot be null.')
        parameters.add_argument('password', type=str, required=True, help='The field password cannot be null.')
        parameters.add_argument('active', type=bool, help='The field active must be boolean.')
        data = parameters.parse_args()
        return data
    
    def json(self):
        return {
            'id': self.id,
            'login': self.login,
            'active': self.active,
            'create_date': self.convert_datetime_json(self.create_date),
            'modify_date': self.convert_datetime_json(self.modify_date)
        }
        
    def set_password(self,password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
    @classmethod
    def check_password(cls,password_api,password_db):
        return bcrypt.checkpw(password_api.encode('utf-8'), password_db.encode('utf-8'))
        
    def convert_datetime_json(self,datetime):
        if datetime is not None:
            return datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        return datetime

    @classmethod
    def find_user_id(cls,id):
        user = cls.query.filter_by(id=id).first()
        if user:
            return user
        return None
    
    @classmethod
    def find_user_login(cls,login):
        user = cls.query.filter_by(login=login).first()
        if user:
            return user
        return None
        
    def insert_user(self):
        db.session.add(self)
        db.session.commit()
        
    def update_user(self,login,password,active=None):
        self.login = login
        self.password = self.set_password(password)
        if active is not None:
            self.active = active
        db.session.add(self)
        db.session.commit()
        
    def delete_user(self):
        db.session.delete(self)
        db.session.commit()