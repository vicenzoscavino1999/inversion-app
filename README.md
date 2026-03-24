## Inversion App

Aplicacion Streamlit para controlar capital, tipo de cambio, compra de MDF y venta final.

### Estructura

- `app.py`: entrypoint de la app.
- `config/`: configuracion global y datos base.
- `core/`: logica de negocio pura.
- `infra/`: persistencia y accesos externos.
- `ui/`: layout, tabs y componentes visuales.
- `data/`: datos locales y archivos de referencia.
- `legacy/`: version monolitica anterior, conservada solo como referencia.
- `tests/`: pruebas unitarias.

`data/referencias/inversiones_ordenadas_paso_a_paso.xlsx` queda como archivo fuente de referencia.
`legacy/app_inversiones.py` queda fuera del entrypoint principal para evitar mezclar la version modular con la monolitica anterior.

### Persistencia

La app usa `Supabase` cuando hay credenciales validas en `.streamlit/secrets.toml`.
Si no hay credenciales, guarda en `data/inversiones_data.json`.

### PWA

La app expone `manifest.json` e iconos desde `static/` con `enableStaticServing = true`.
Eso permite instalarla como PWA desde navegadores compatibles.

Limitacion actual: la app queda instalable, pero no implementa modo offline completo porque Streamlit sigue dependiendo de su runtime web activo.

### Ejecutar

```bash
streamlit run app.py
```

### Probar

```bash
python -m unittest discover -s tests -v
```
