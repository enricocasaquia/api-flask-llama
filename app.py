from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from resources.user import User, UserSignon, UserLogin, UserLogout
from resources.chat import Chat, ChatDelete
from resources.metrics import Metrics
from blacklist import BLACKLIST
import json

with open("./conf/config.json") as config_json:
    config = json.load(config_json)

with open("./conf/flasgger.json") as flasgger_json:
    flasgger = json.load(flasgger_json)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config['SQLALCHEMY_TRACK_MODIFICATIONS']
app.config['JWT_SECRET_KEY'] = config['JWT_SECRET_KEY']
app.config['JWT_BLACKLIST_ENABLED'] = config['JWT_BLACKLIST_ENABLED']
app.config['JWT_VERIFY_SUB'] = config['JWT_VERIFY_SUB']

@app.route('/')
def index():
    return '<h1>API de Integração com OLLAMA</h1>'

@app.before_request
def create_database():
    app.before_request_funcs[None].remove(create_database)
    from sql_alchemy import db
    db.create_all()
    
swagger = Swagger(app, template=flasgger['SWAGGER_TEMPLATE'])
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
def check_blacklist(self,token):
    return token['jti'] in BLACKLIST

@jwt.revoked_token_loader
def invalidate_token(jwt_header, jwt_payload):
    return jsonify({'message':'You have been disconnected.'}), 401

if __name__ == '__main__':
    from sql_alchemy import db
    db.init_app(app)
    app.run(debug=True)