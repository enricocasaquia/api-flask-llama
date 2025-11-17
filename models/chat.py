from flask_restful import reqparse

class ChatModel:
    @staticmethod
    def parse_chat():
        parameters = reqparse.RequestParser()
        parameters.add_argument('prompt', type=str, required=True, help='The field prompt cannot be null.')
        return parameters.parse_args()