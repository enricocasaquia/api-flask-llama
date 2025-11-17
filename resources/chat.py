from flask_restful import Resource
from flask_jwt_extended import jwt_required
from models.chat import ChatModel
from models.metrics import MetricsModel
import json
import time
import psutil
import GPUtil
import ollama

with open("./conf/config.json") as config_json:
    config = json.load(config_json)

client = ollama.Client()
model = config['OLLAMA_MODEL']

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
            start = time.time()
            cpu_before = psutil.cpu_percent(interval=None)
            ram_before = psutil.virtual_memory().used / (1024 * 1024)
            
            response = client.generate(model=model, prompt=prompt_post)
            
            end = time.time()
            cpu_after = psutil.cpu_percent(interval=None)
            ram_after = psutil.virtual_memory().used / (1024 * 1024)
            
            tokens = len(response["response"].split())
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
              MetricsModel.capture_metrics(
                  tokens=tokens,
                  inference_time=(end-start),
                  cpu_percent=cpu_percent,
                  ram_mb=ram_mb,
                  gpu_data=gpu_data,
                  status_code=200
              )
              return {
                  'prompt': prompt_post,
                  'response': response["response"]
              }, 200
        except Exception as e:
            return {
                'message': f'Error while sending prompt.'
            }, 500