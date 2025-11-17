# API Flask + LLama (api-flask-llama)

Projeto: API REST em Flask que integra um modelo LLama (ou Ollama) para chat. Inclui autenticação JWT, banco SQLite via SQLAlchemy e endpoints para usuários e chat.

## Pré-requisitos (Windows)
- Python 3.10+ (recomendado)
- Ollama instalado: [https://ollama.com/](https://ollama.com/)
- Git instalado: [https://git-scm.com/install/](https://git-scm.com/install/)
- Espaço em disco suficiente se carregar modelos grandes localmente

## Setup (PowerShell)
1. Clonar / abrir pasta do projeto. Por exemplo:
   ```
   cd C:\Python\api-flask-llama
   ```

2. Criar e ativar virtualenv:
   ```
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Instalar dependências:
   ```
   pip install -r requirements.txt
   ```

4. Criar modelo do ollama dentro da pasta `conf`:
   ```
   C:\Python\api-flask-llama\conf>ollama create grupocriar -f ./Modelfile
   ```

## Arquivos de configuração
- conf/config.json — configurações da aplicação (exemplo mínimo):
  ```json
  {
    "SQLALCHEMY_DATABASE_URI": "sqlite:///nome_do_banco_de_dados.db",
    "SQLALCHEMY_TRACK_MODIFICATIONS": false,
    "JWT_SECRET_KEY": "troque_esta_chave_para_producao",
    "JWT_BLACKLIST_ENABLED": true,
    "JWT_VERIFY_SUB": false
  }
  ```
- conf/Modelfile — configurações do comportamento do modelo (já incluído no repo).
- conf/flasgger.json — template para documentação Swagger.

Ajuste os valores adequadamente antes de executar em produção.

## Executar a aplicação (desenvolvimento)
1. Certifique-se que o virtualenv está ativado.
2. Rodar:
   ```
   python app.py
   ```
3. A API ficará disponível em:
   - http://127.0.0.1:5000/

4. Documentação e interface para testes ficará disponível pelo Flasgger em:
   - http://127.0.0.1:5000/apidocs/

## Endpoints principais
- GET `/` — Página inicial
- POST `/signon` — Criar usuário (ver resources.user)
- POST `/login` — Login (retorna token JWT)
- POST `/logout` — Logout (blacklist)
- POST `/chat` — Endpoint de chat (resources.chat) — ver formato esperado nas rotas

Consulte os arquivos em `resources/` para payloads e exemplos.

## Testes e DB
- O projeto cria o banco via `sql_alchemy.db.create_all()` no primeiro request.
- Para resetar DB exclua `data.db` (ou a URI configurada).

## Estrutura do projeto
- app.py — aplicação Flask principal
- resources/ — endpoints REST (user, chat)
- models/ — modelos ORM
- sql_alchemy.py — instancia do SQLAlchemy
- conf/ — configurações (config.json, flasgger.json, Modelfile)
- requirements.txt — dependências