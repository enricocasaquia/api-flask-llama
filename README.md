# API Flask + LLama (api-flask-llama)

API REST em Flask que integra um modelo Ollama para chat. Inclui autenticação JWT, banco SQLite via SQLAlchemy e endpoints para usuários e chat. Roda em dois containers Docker: a API e o Ollama.

## Pré-requisitos
- Docker e Docker Compose
- Espaço em disco suficiente para os modelos do Ollama (alguns GB por modelo)

## Subindo o projeto

```bash
git clone https://github.com/enricocasaquia/api-flask-llama.git
cd api-flask-llama
docker compose up -d --build
```

Isso sobe dois serviços:
- **ollama** — servidor Ollama, expõe `11434`, mantém modelos em volume nomeado (`ollama_models`)
- **api** — a aplicação Flask, expõe `5000`, cria/atualiza automaticamente o modelo customizado definido em `conf/Modelfile` na inicialização

Acompanhe os logs do setup:
```bash
docker compose logs -f api
```

## Arquivos de configuração

- `src/conf/config.json` — configurações da aplicação:
```json
  {
    "FLASK_DEBUG": false,
    "SQLALCHEMY_TRACK_MODIFICATIONS": false,
    "JWT_SECRET_KEY": "troque_esta_chave_para_producao",
    "JWT_BLACKLIST_ENABLED": true,
    "JWT_VERIFY_SUB": false,
    "OLLAMA_MODEL": "nome_modelo_ollama",
    "CONTEXT_WINDOW_SIZE": 10
  }
```
  A URI do banco (SQLite) é resolvida automaticamente em `src/config.py`, relativa a `src/instance/` — não precisa (nem deve) ser definida aqui.

- `src/conf/Modelfile` — define o modelo Ollama customizado (base, parâmetros, system prompt). Usa sintaxe padrão de Modelfile do Ollama (`FROM`, `PARAMETER`, `SYSTEM`).
- `src/conf/flasgger.json` — template do Swagger.

Variável de ambiente `OLLAMA_HOST` (já configurada no `docker-compose.yaml`) aponta a API pro serviço `ollama` da rede interna.

## Documentação da API

Com os containers de pé:
- http://127.0.0.1:5000/apidocs/

## Endpoints principais
- POST `/signon` — criar usuário
- POST `/login` — login (retorna token JWT)
- POST `/logout` — logout (blacklist)
- POST `/chat` — envia prompt ao modelo, mantém histórico por usuário
- POST `/chat/delete` — limpa histórico de conversa do usuário
- GET `/metrics` — métricas de execução (tokens, tempo de inferência, CPU/GPU)

Consulte `src/resources/` para os payloads esperados de cada rota.

## CLI

O projeto tem uma CLI pra gerenciar usuários e conversar pelo terminal, sem passar pela API HTTP:

```bash
docker compose exec api python cli.py create-user
docker compose exec api python cli.py list-users
docker compose exec api python cli.py delete-user <login>
docker compose exec api python cli.py chat
```

## Banco de dados

SQLite, persistido no volume `sqlite_data` (montado em `src/instance/` dentro do container `api`). Sobrevive a `docker compose down`; só é apagado com `docker compose down -v`.

## Estrutura do projeto
```bash
src/
├── app.py # aplicação Flask principal
├── config.py # carrega config.json e flasgger.json, resolve paths absolutos
├── setup.py # cria/atualiza o modelo Ollama a partir do Modelfile, roda antes da API subir
├── cli.py # CLI de gerenciamento e chat via terminal
├── resources/ # endpoints REST (user, chat, metrics)
├── models/ # modelos ORM
├── sql_alchemy.py # instância do SQLAlchemy
└── conf/ # config.json, flasgger.json, Modelfile
Dockerfile
docker-compose.yaml
requirements.txt
```

## Melhorias futuras
- **WSGI de produção**: substituir `app.run()` por Gunicorn ou Waitress.
- **GPU**: configurar o `docker-compose.yaml` com `nvidia` runtime para o serviço `ollama` acessar GPU.
- **Cache com Redis**: reduzir latência/custo em prompts repetidos.
- **Persistência de métricas**: hoje `MetricsModel` vive em memória (perdido a cada restart); mover para o banco.