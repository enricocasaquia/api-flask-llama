import os
import re
from pathlib import Path
from config import CONFIG
import ollama

def print_header(msg):
    print(f"\n{'='*40}")
    print(f"\033[36m{msg}\033[0m")
    print(f"{'='*40}")

def print_step(step, msg):
    print(f"\n\033[33m[{step}]\033[0m {msg}")

def print_success(msg):
    print(f"\033[32m✓ {msg}\033[0m")

def print_error(msg):
    print(f"\033[31m✗ {msg}\033[0m")
    

def load_config():
    print_step("1/2", "Lendo configuração...")
    
    model_name = CONFIG.get("OLLAMA_MODEL", "MODELO_LLM")
    print(f"\033[36mModelo: {model_name}\033[0m")
    
    return model_name

def parse_modelfile(path):
    print_step("2/3", "Lendo arquivo de modelo Ollama...")
    with open(path, encoding="utf-8") as f:
        content = f.read()

    from_match = re.search(r'^FROM\s+(\S+)', content, re.MULTILINE)
    base_model = from_match.group(1) if from_match else None

    parameters = {}
    for key, value in re.findall(r'^PARAMETER\s+(\S+)\s+(.+)$', content, re.MULTILINE):
        value = value.strip()
        for cast in (int, float):
            try:
                value = cast(value)
                break
            except ValueError:
                continue
        parameters[key] = value

    system_match = re.search(r'SYSTEM\s*"""(.*?)"""', content, re.DOTALL)
    system_prompt = system_match.group(1).strip() if system_match else None

    return base_model, parameters, system_prompt

def create_ollama_model(model_name):
    if not model_name:
        return
    print_step("3/3", f"Criando/Atualizando modelo ollama '{model_name}'...")

    modelfile_path = Path("conf") / "Modelfile"
    if not modelfile_path.exists():
        print_error(f"Modelfile não encontrado em {modelfile_path}")
        return

    base_model, parameters, system_prompt = parse_modelfile(modelfile_path)
    if not base_model:
        print_error("Instrução FROM não encontrada no Modelfile")
        return

    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    client = ollama.Client(host=ollama_host)

    try:
        client.create(
            model=model_name,
            from_=base_model,
            system=system_prompt,
            parameters=parameters or None,
        )
        print_success(f"Modelo ollama '{model_name}' criado/atualizado com sucesso!")
    except ollama.ResponseError as e:
        print_error(f"Erro ao criar modelo ollama: {e.error} (status {e.status_code})")
    except Exception as e:
        print_error(f"Não foi possível conectar ao Ollama em {ollama_host}: {e}")

def main():
    print_header("Setup: API Flask + LLama")
    
    try:
        model_name = load_config()
        create_ollama_model(model_name)
        
        print_header("Setup concluído!")
        print(f"\033[36mpython app.py\033[0m")
        
    except Exception as e:
        print_error(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()