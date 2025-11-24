# API Flask + LLama (api-flask-llama)

Projeto: API REST em Flask que integra um modelo LLama (ou Ollama) para chat. Inclui autenticação JWT, banco SQLite via SQLAlchemy e endpoints para usuários e chat.

## Pré-requisitos
- Python 3.10+ (recomendado)
- Ollama instalado: [https://ollama.com/](https://ollama.com/)
- Git instalado: [https://git-scm.com/install/](https://git-scm.com/install/)
- Espaço em disco suficiente se carregar modelos grandes localmente

## Setup (PowerShell)
1. Clonar / abrir pasta do projeto. Por exemplo:
   ```
   cd C:\Python\

   C:\Python git clone https://github.com/enricocasaquia/api-flask-llama.git`
   ```

2. Configuração da virtualenv e dependências:
   ```
   python setup.py
   ```

   Ou pode executar diretamente o:

   ```
   python app.py
   ```

## Arquivos de configuração
- conf/config.json — configurações da aplicação (exemplo mínimo):
  ```json
  {
    "FLASK_DEBUG": false,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///nome_do_banco_de_dados.db",
    "SQLALCHEMY_TRACK_MODIFICATIONS": false,
    "JWT_SECRET_KEY": "troque_esta_chave_para_producao",
    "JWT_BLACKLIST_ENABLED": true,
    "JWT_VERIFY_SUB": false,
    "OLLAMA_MODEL": "nome_modelo_ollama",
    "CONTEXT_WINDOW_SIZE": 10
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

3. Documentação e interface para testes ficará disponível pelo Flasgger em:
   - http://127.0.0.1:5000/apidocs/

4. A execução também pode ser feita via interação do terminal ao rodar:
   ```
   python cli.py
   ```

## Endpoints principais
- POST `/signon` — Criar usuário (ver resources.user)
- POST `/login` — Login (retorna token JWT)
- POST `/logout` — Logout (blacklist)
- POST `/chat` — Endpoint de chat (resources.chat) — ver formato esperado nas rotas
- POST `/chat/delete` — Endpoint de fim de chat (resources.chat)
- GET `/metrics` — Endpoint para buscar as métricas de execução (resources.metrics)

Consulte os arquivos em `resources/` para payloads e exemplos.

## Testes e DB
- O projeto cria o banco via `sql_alchemy.db.create_all()` no primeiro request.
- Para resetar DB exclua `data.db` (ou a URI configurada).

## Estrutura do projeto
- app.py — aplicação Flask principal
- setup.py — preparação do ambiente
- cli.py — execução local do programa via terminal
- resources/ — endpoints REST (user, chat, metrics)
- models/ — modelos ORM
- sql_alchemy.py — instancia do SQLAlchemy
- conf/ — configurações (config.json, flasgger.json, Modelfile)
- requirements.txt — dependências

## Melhorias e ideias futuras
Infraestrutura e Produção
- Containerização com Docker: Criar um Dockerfile e docker-compose.yml para facilitar a implantação, garantindo que o ambiente de execução (incluindo o Ollama) seja consistente.
- WSGI para Produção: Substituir a execução nativa do Flask (app.run) por um WSGI Server de produção como Gunicorn ou Waitress, aumentando a estabilidade e a capacidade de lidar com múltiplas requisições simultâneas.
- Configuração de GPU: Embora o setup do Ollama já suporte GPU, garantir que as imagens Docker ou o ambiente de produção tenham acesso direto aos drivers e recursos de placas NVIDIA (via NVIDIA Container Toolkit) ou AMD.

Performance e Escalabilidade
- Cache com Redis: Implementar um serviço de cache Redis para armazenar respostas recentes do LLM. Isso reduziria a latência e o uso de recursos de GPU/CPU para perguntas repetidas, melhorando a performance e reduzindo custos.
- Persistência de Métricas: Atualmente, as métricas são armazenadas em memória na classe MetricsModel. Para análise histórica e visualização em dashboards, seria ideal armazenar estas informações no banco de dados.