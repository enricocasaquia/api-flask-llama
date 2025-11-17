from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models.chat import ChatModel
from blacklist import BLACKLIST
import ollama

client = ollama.Client()
model = 'grupocriar'

class Chat(Resource):
    @jwt_required()
    def post(self):
        """
        Sends a prompt to the LLAMA model
        ---
        tags:
          - Chat
        parameters:
          - in: body
            name: prompt
            schema:
              type: object
              properties:
                prompt:
                  type: string
        responses:
          200:
            description: {response}
          400:
            description: Error while sending prompt
        """
        data = ChatModel.parse_chat()
        prompt_post = data.get("prompt")
        try:
            response = client.generate(model=model, prompt=prompt_post)
            return {
                'prompt': prompt_post,
                'response': response["response"]
            }, 200
        except Exception as e:
            return {
                'message': f'Error while sending prompt.'
            }, 500