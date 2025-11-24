import os
import sys
import json
import subprocess
import platform
from pathlib import Path

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
    

def create_venv():
    """Criar/verificar virtualenv"""
    print_step("1/4", "Criando/Ativando virtualenv...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print_success("venv já existe")
    else:
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print_success("venv criada")
    
    return venv_path

def get_pip_executable(venv_path):
    """Retornar caminho do pip (Windows/Linux/Mac)"""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "pip.exe"
    else:
        return venv_path / "bin" / "pip"

def install_requirements(pip_exe):
    """Instalar requirements.txt"""
    print_step("2/4", "Instalando dependências...")
    
    if not Path("requirements.txt").exists():
        print_error("requirements.txt não encontrado")
    
    subprocess.check_call([str(pip_exe), "install", "-r", "requirements.txt"])
    print_success("Dependências instaladas")

def load_config():
    """Carregar config.json"""
    print_step("3/4", "Lendo configuração...")
    
    config_path = Path("conf") / "config.json"
    if not config_path.exists():
        print_error(f"config.json não encontrado em {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    model_name = config.get("OLLAMA_MODEL", "grupocriar")
    print(f"\033[36mModelo: {model_name}\033[0m")
    
    return model_name

def create_ollama_model(model_name):
    """Criar modelo ollama"""
    print_step("4/4", f"Criando/Atualizando modelo ollama '{model_name}'...")
    
    modelfile_path = Path("conf") / "Modelfile"
    if not modelfile_path.exists():
        print_error(f"Modelfile não encontrado em {modelfile_path}")
    
    try:
        subprocess.check_call([
            "ollama",
            "create",
            model_name,
            "-f",
            str(modelfile_path)
        ])
        print_success(f"Modelo ollama '{model_name}' criado/atualizado com sucesso!")
    except FileNotFoundError:
        print_error("ollama não está instalado ou não está no PATH")
    except subprocess.CalledProcessError as e:
        print_error(f"Erro ao criar modelo ollama: {e}")

def main():
    os.chdir(Path(__file__).parent)
    
    print_header("Setup: API Flask + LLama")
    
    try:
        venv_path = create_venv()
        pip_exe = get_pip_executable(venv_path)
        install_requirements(pip_exe)
        model_name = load_config()
        create_ollama_model(model_name)
        
        print_header("Setup concluído! Acesse a venv e execute:")
        print(f"\033[36mpython app.py\033[0m")
        
    except subprocess.CalledProcessError as e:
        print_error(f"Erro durante setup: {e}")
    except Exception as e:
        print_error(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()