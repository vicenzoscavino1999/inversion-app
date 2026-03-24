import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

import streamlit as st

from config.settings import DATA_FILE, DEFAULT_DATA

ROW_ID = 1
LOCAL_BACKEND_LABEL = "JSON local (data/inversiones_data.json)"
SUPABASE_BACKEND_LABEL = "Supabase"


def _registrar_backend(label):
    try:
        st.session_state["storage_backend"] = label
    except Exception:
        pass


def _get_client():
    """Devuelve el cliente de Supabase si hay credenciales validas."""
    try:
        from supabase import create_client
    except Exception:
        return None

    try:
        config = st.secrets["supabase"]
    except Exception:
        return None

    url = config.get("url")
    key = config.get("key")
    if not url or not key:
        return None
    if "TU-PROYECTO" in url or "TU-ANON-KEY" in key:
        return None
    return create_client(url, key)


def _cargar_datos_locales():
    data_path = Path(DATA_FILE)
    if not data_path.exists():
        return deepcopy(DEFAULT_DATA)

    with data_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _guardar_datos_locales(data):
    data_path = Path(DATA_FILE)
    data_path.parent.mkdir(parents=True, exist_ok=True)
    with data_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def _backend_preferido():
    return SUPABASE_BACKEND_LABEL if _get_client() is not None else LOCAL_BACKEND_LABEL


def cargar_datos():
    client = _get_client()
    if client is not None:
        try:
            resp = client.table("app_data").select("data").eq("id", ROW_ID).execute()
            if resp.data and "origen_capital" in resp.data[0].get("data", {}):
                _registrar_backend(SUPABASE_BACKEND_LABEL)
                return resp.data[0]["data"]
        except Exception:
            pass

    data = _cargar_datos_locales()
    _registrar_backend(LOCAL_BACKEND_LABEL)
    return data


def guardar_datos(data):
    data["meta"]["ultima_modificacion"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    client = _get_client()
    if client is not None:
        try:
            client.table("app_data").upsert({"id": ROW_ID, "data": data}).execute()
            _registrar_backend(SUPABASE_BACKEND_LABEL)
            return
        except Exception:
            pass

    _guardar_datos_locales(data)
    _registrar_backend(LOCAL_BACKEND_LABEL)


def obtener_backend_activo():
    try:
        return st.session_state.get("storage_backend", _backend_preferido())
    except Exception:
        return _backend_preferido()
