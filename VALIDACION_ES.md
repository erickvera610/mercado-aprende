# Evidencia de validación automatizada

Se ejecutaron diez escenarios diferentes con datos ficticios o sintéticos. Este informe describe ejecuciones reales del código mediante un script automatizado. No representa tráfico de usuarios, experiencia laboral ni contribuciones realizadas manualmente por Erik.

Resultado: **10 de 10 escenarios aprobados**.

Consulta `validation-results.json` para ver cada entrada, resultado y fecha UTC de ejecución.

## Repetir las ejecuciones

Desde la carpeta del repositorio ejecuta:

```bash
python validate_scenarios.py
```

En Mercado Aprende instala primero las dependencias del README. En los otros cinco proyectos basta Python. El script utiliza almacenamiento temporal: no cambia registros personales ni realiza compras reales. Regenera el informe local; para conservar nuevos resultados en GitHub debes revisarlos y hacer un commit.

## Qué se comprobó

| Escenario | Entrada | Resultado |
|---|---|---|
| 1 | {"title": "Sample product 1", "category": "Deportes", "condition": "Usado", "price": "10.50", "description": "Fictional product for automated scenario 1."} | Aprobado |
| 2 | {"title": "Sample product 2", "category": "Libros", "condition": "Usado", "price": "17.50", "description": "Fictional product for automated scenario 2."} | Aprobado |
| 3 | {"title": "Sample product 3", "category": "Electrónica", "condition": "Usado", "price": "24.50", "description": "Fictional product for automated scenario 3."} | Aprobado |
| 4 | {"title": "Sample product 4", "category": "Deportes", "condition": "Usado", "price": "31.50", "description": "Fictional product for automated scenario 4."} | Aprobado |
| 5 | {"title": "Sample product 5", "category": "Libros", "condition": "Usado", "price": "38.50", "description": "Fictional product for automated scenario 5."} | Aprobado |
| 6 | {"title": "Sample product 6", "category": "Electrónica", "condition": "Usado", "price": "45.50", "description": "Fictional product for automated scenario 6."} | Aprobado |
| 7 | {"title": "Sample product 7", "category": "Deportes", "condition": "Usado", "price": "52.50", "description": "Fictional product for automated scenario 7."} | Aprobado |
| 8 | {"title": "Sample product 8", "category": "Libros", "condition": "Usado", "price": "59.50", "description": "Fictional product for automated scenario 8."} | Aprobado |
| 9 | {"title": "Sample product 9", "category": "Electrónica", "condition": "Usado", "price": "66.50", "description": "Fictional product for automated scenario 9."} | Aprobado |
| 10 | {"title": "Sample product 10", "category": "Deportes", "condition": "Usado", "price": "73.50", "description": "Fictional product for automated scenario 10."} | Aprobado |
