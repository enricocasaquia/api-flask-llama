from flask import Flask
import ollama

app = Flask(__name__)

client = ollama.Client()
model = 'grupocriar'

@app.route('/')
def index():
    return '<h1>API de Integração com LLAMA</h1>'

@app.route('/chat/<string:prompt>')
def chat(prompt):
    response = client.generate(model=model, prompt=prompt)
    return response.response,200

if __name__ == '__main__':
    app.run(debug=True)