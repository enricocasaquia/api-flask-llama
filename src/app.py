import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
    
subprocess.check_call([sys.executable, str(BASE_DIR / "setup.py")])

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from resources.user import User, UserSignon, UserLogin, UserLogout
from resources.chat import Chat, ChatDelete
from resources.metrics import Metrics
from blacklist import BLACKLIST
from config import CONFIG, FLASGGER
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = CONFIG['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = CONFIG['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['JWT_SECRET_KEY'] = CONFIG['JWT_SECRET_KEY']
app.config['JWT_BLACKLIST_ENABLED'] = CONFIG['JWT_BLACKLIST_ENABLED']
app.config['JWT_VERIFY_SUB'] = CONFIG['JWT_VERIFY_SUB']

@app.before_request
def create_database():
    app.before_request_funcs[None].remove(create_database)
    from sql_alchemy import db
    db.create_all()
    
swagger = Swagger(app, template=FLASGGER['SWAGGER_TEMPLATE'])
api = Api(app)
api.add_resource(User, '/users/<int:id>')
api.add_resource(UserSignon, '/signon')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(Chat, '/chat')
api.add_resource(ChatDelete, '/chat/delete')
api.add_resource(Metrics, '/metrics')
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_blacklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in BLACKLIST

@jwt.revoked_token_loader
def invalidate_token(jwt_header, jwt_payload):
    return jsonify({'message':'You have been disconnected.'}), 401

if __name__ == '__main__':
    from sql_alchemy import db
    db.init_app(app)
    app.run(host='0.0.0.0', port=5000, debug=CONFIG['FLASK_DEBUG'])