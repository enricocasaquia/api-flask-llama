from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent
CONF_DIR = BASE_DIR / "conf"
INSTANCE_DIR = BASE_DIR / "instance"

INSTANCE_DIR.mkdir(exist_ok=True)

def _load_json(filename):
    with open(CONF_DIR / filename, encoding="utf-8") as f:
        return json.load(f)

CONFIG = _load_json("config.json")
FLASGGER = _load_json("flasgger.json")
CONFIG["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{INSTANCE_DIR / 'api_flask_llama.db'}"