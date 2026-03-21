import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "inversiones_data.json")

PAGE_CONFIG = {
    "page_title": "Control de Inversiones",
    "page_icon": "📈",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

DEFAULT_DATA = {
    "meta": {
        "creado": "2025-01-01",
        "ultima_modificacion": "",
        "version": 1
    },
    "origen_capital": [
        {"nombre": "Luigi", "tipo": "Capital personal", "monto": 15250, "cuota": 0, "plazo": 0, "comentario": ""},
        {"nombre": "Isabel", "tipo": "Capital personal", "monto": 20450, "cuota": 0, "plazo": 0, "comentario": ""},
        {"nombre": "Interbank", "tipo": "Prestamo", "monto": 11800, "cuota": 620, "plazo": 36, "comentario": "620 por 36 meses"},
        {"nombre": "Ripley", "tipo": "Prestamo", "monto": 24800, "cuota": 1000, "plazo": 36, "comentario": "1,000 por 36 meses"},
    ],
    "operaciones_cambio": [
        {
            "nombre": "Primera compra de dolares",
            "soles_usados": 62073,
            "tc_compra": 3.42,
            "tc_venta": 3.47,
            "activa": True,
        }
    ],
    "devolucion": {
        "monto_devuelto": 18000,
    },
    "segunda_compra": {
        "usd_manual": 8122,
        "tc": 3.47,
    },
    "mdf": {
        "usd_total": 10143,
        "soles_faltantes_manual": 7047,
    },
    "venta_final": {
        "melaminas": 2070,
        "precio_por_unidad": 5.80,
    },
    "historial": []
}
