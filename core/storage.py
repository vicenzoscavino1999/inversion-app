import json
import os
from datetime import datetime
from copy import deepcopy

from config.settings import DATA_FILE, DEFAULT_DATA


def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return deepcopy(DEFAULT_DATA)


def guardar_datos(data):
    data["meta"]["ultima_modificacion"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
