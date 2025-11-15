from flask import Flask
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)
model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0"

model = AutoModelForCausalLM.from_pretrained(model_id,dtype=torch.float16,device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_id)

llm_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_length=10000
)

terminators = [
    llm_pipeline.tokenizer.eos_token_id,
    llm_pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

@app.route('/')
def index():
    return '<h1>API de Integração com LLAMA</h1>'

@app.route('/chat/<string:message>')
def chat(message):
    messages = [
        {"role": "system", "content": "Você é um chatbot que consegue conversar com os usuários para tirar dúvidas sobre desenvolvimento de sistemas e você foi desenvolvido pelo Grupo Criar. Independente do que o usuário te questionar, você deve sempre responder em português do Brasil. Você não deve fugir dos assuntos relacionados a sistemas."},
        {"role": "user", "content": f"{message}"}
    ]
    prompt = llm_pipeline.tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    outputs = llm_pipeline(
        prompt,
        max_new_tokens=256,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )
    
    return outputs[0]['generated_text']

if __name__ == '__main__':
    app.run(debug=True)