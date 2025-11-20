from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.chat import ChatModel
from models.history import ChatHistoryModel
from models.metrics import MetricsModel
import json
import time
import psutil
import GPUtil
import ollama

with open("./conf/config.json") as config_json:
    config = json.load(config_json)

CLIENT = ollama.Client()
MODEL_NAME = config['OLLAMA_MODEL']
CONTEXT_SIZE = config['CONTEXT_WINDOW_SIZE']

class Chat(Resource):
    @jwt_required()
    def post(self):
        """
        Sends a prompt to the LLAMA model with conversation history
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
          500:
            description: Error while sending prompt
        """
        data = ChatModel.parse_chat()
        user_prompt = data.get("prompt")
        user_id = get_jwt_identity()
        
        try:
            start = time.time()
            cpu_before = psutil.cpu_percent(interval=None)
            ram_before = psutil.virtual_memory().used / (1024 * 1024)
            
            history = ChatHistoryModel.find_history_user(user_id, CONTEXT_SIZE)
            prompts = [{'role': h.role, 'content': h.content} for h in history]
            prompts.append({'role': 'user', 'content': user_prompt})
            
            response = CLIENT.chat(model=MODEL_NAME, messages=prompts, stream=False)
            assistant_response = response["message"]["content"]
            
            end = time.time()
            cpu_after = psutil.cpu_percent(interval=None)
            ram_after = psutil.virtual_memory().used / (1024 * 1024)
            
            tokens = len(assistant_response.split())
            cpu_percent = max(cpu_after - cpu_before, 0)
            ram_mb = max(ram_after - ram_before, 0)
            
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                gpu_data = {
                    "percent": gpu.load * 100,
                    "mb": gpu.memoryUsed
                }
            else:
                gpu_data = None
            
            if response:
              user_turn = ChatHistoryModel(user_id, 'user', user_prompt)
              assistant_turn = ChatHistoryModel(user_id, 'assistant', assistant_response)
              
              user_turn.insert_history()
              assistant_turn.insert_history()
            
              MetricsModel.capture_metrics(
                  tokens=tokens,
                  inference_time=(end-start),
                  cpu_percent=cpu_percent,
                  ram_mb=ram_mb,
                  gpu_data=gpu_data,
                  status_code=200
              )
              return {
                  'prompt': user_prompt,
                  'response': assistant_response
              }, 200
              
        except Exception as e:
            return {
                'message': f'Error while sending prompt.'
            }, 500
          
class ChatDelete(Resource):
    @jwt_required()
    def post(self):
        """
        Deletes all conversation history
        ---
        tags:
          - Chat
        responses:
          200:
            message: All conversation history cleaned
          500:
            description: Error while cleaning conversation history
        """
        user_id = get_jwt_identity()
        try:
          ChatHistoryModel.delete_history_by_user(user_id)
          return {
                  'message': 'All conversation history cleaned.'
              }, 200
        except Exception as e:
            return {
              'message': 'Error deleting chat history.'
            }, 500