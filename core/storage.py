import json
import streamlit as st
from datetime import datetime
from copy import deepcopy
from supabase import create_client

from config.settings import DEFAULT_DATA

ROW_ID = 1  # Fila unica para datos compartidos


def _get_client():
    """Devuelve el cliente Supabase usando secrets de Streamlit."""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


def cargar_datos():
    try:
        client = _get_client()
        resp = client.table("app_data").select("data").eq("id", ROW_ID).execute()
        if resp.data and "origen_capital" in resp.data[0].get("data", {}):
            return resp.data[0]["data"]
    except Exception:
        pass
    return deepcopy(DEFAULT_DATA)


def guardar_datos(data):
    data["meta"]["ultima_modificacion"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        client = _get_client()
        client.table("app_data").upsert({"id": ROW_ID, "data": data}).execute()
    except Exception:
        pass
