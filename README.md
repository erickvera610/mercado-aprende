# Mercado Aprende
Proyecto educativo independiente de Erik José Vera Mercado. Inspirado en el concepto de marketplace de Team Alpha, sin copiar su código.

## Demo pública sin instalación

[Ejecutar demo pública](https://erickvera610.github.io/mercado-aprende/). La demo JavaScript permite explorar, publicar ejemplos y simular compras en el navegador. Guarda datos solo en el dispositivo del visitante; no incluye autenticación ni ejecuta Flask. El repositorio es público y los visitantes no tienen permiso de escritura.

## Funciones
Registro, inicio y cierre de sesión; publicación de productos; búsqueda y filtro; detalles; compra simulada; historial de compras y publicaciones. Usa Flask, SQLite, HTML y CSS propio. Todos los bloques de Python incluyen comentarios en español.

**Las compras son simuladas. No cobra dinero ni organiza envíos.** GitHub almacena el código; GitHub Pages no ejecuta Flask. Esta versión se ejecuta localmente.

## Windows / PowerShell
Instala Python 3.12. Abre una terminal dentro de esta carpeta:
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```
Abre http://127.0.0.1:5000. Deja abierta la terminal; Ctrl+C detiene el servidor.

## macOS / Linux
```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

## Prueba manual
Crea vendedor y publica una bicicleta. Cierra sesión, crea comprador y compra el artículo con esa cuenta. Revisa Mi cuenta: aparece en compras y deja de estar disponible en el catálogo. Reinicia el servidor: SQLite conserva los datos en instance/market.db.

## Tests
En Windows: `.\.venv\Scripts\python.exe -m pytest -q`. En macOS/Linux: `.venv/bin/python -m pytest -q`.
GitHub Actions ejecutará las pruebas en cada push y Pull Request cuando el código esté subido.

## Estructura
- app.py: rutas, sesión, validación, SQL y lógica de compra.
- templates/: páginas HTML; base.html comparte navegación y mensajes.
- static/style.css: diseño responsive.
- tests/test_market.py: pruebas con base temporal.
- .github/workflows/tests.yml: integración continua.
- docs/tutorial.md y docs/Tutorial_GitHub_Mercado_Aprende.pdf: guía paso a paso.
- .gitignore: excluye base, entorno, cachés y secretos.

## Alcance
SQLite simplifica la instalación frente a PostgreSQL. No incluye SQLAlchemy ni Bootstrap: es una implementación didáctica nueva. No contiene productos o usuarios precargados. No incluye pagos, envíos, carga de fotos ni recuperación de cuentas. No se asignó una licencia de distribución.
Para uso comercial se requieren HTTPS, servidor WSGI, SECRET_KEY estable fuera de Git, rate limiting, recuperación de cuentas, migraciones, copias de seguridad y revisión de seguridad. El servidor incluido escucha únicamente en localhost. Sin SECRET_KEY de entorno, la clave cambia al reiniciar y hay que volver a iniciar sesión.

## Ejecutar dentro de GitHub (Codespaces)
En el repositorio, abre **Code > Codespaces > Create codespace on main**.
La configuración de `.devcontainer/` instala las dependencias e inicia Flask automáticamente.
Abre la pestaña **Ports** y el enlace del puerto **5000**, etiquetado Mercado Aprende. Mantén privado el puerto.
Si no abre automáticamente: en la terminal ejecuta `bash .devcontainer/start.sh`.
Codespaces usa la cuota de tu cuenta y puede tener costes si superas su límite; detén el entorno al terminar con **Stop codespace**. No se ha contratado ningún plan de pago.
Los datos se conservan en ese Codespace mientras exista. Al borrarlo, se pierde su base local. No es un hosting permanente.
