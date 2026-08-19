# Ahorro Smart - Servicio predictivo

Servicio FastAPI independiente que carga el modelo entrenado en T40 y genera proyecciones informativas de gastos mensuales por categoría.

## Requisitos

- Python 3.13 o compatible.
- Dependencias declaradas en `requirements.txt`.
- Artefactos `models/expense_forecast_model.joblib` y `models/model_metadata.json`.

## Instalación

Desde `ia-service`:

```powershell
python -m pip install -r requirements.txt
```

## Ejecución

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

La documentación interactiva queda disponible en `http://127.0.0.1:8000/docs`.

## GET /health

Informa la disponibilidad del servicio, la carga del modelo, su nombre y la versión de Scikit-learn registrada en los metadatos.

## POST /predict

Recibe un período objetivo y un historial de gastos, agrega los movimientos por mes y categoría, reconstruye las características de T40 y entrega diez proyecciones junto con el total mensual.

## Formato de entrada

```json
{
  "target_period": "2026-07",
  "expenses": [
    {"date": "2026-06-05", "category": "Alimentación", "amount": 25000}
  ]
}
```

`target_period` utiliza `YYYY-MM`. Se requieren movimientos históricos en cada uno de los tres meses inmediatamente anteriores. Todo movimiento del período objetivo o posterior se rechaza para impedir fuga de información futura.

## Formato de salida

La respuesta contiene el período, modelo, proyecciones por categoría, predicción original, indicador de ajuste no negativo, total proyectado y cantidad de meses históricos utilizados.

## Validaciones

- Solo se aceptan las diez categorías oficiales de gasto.
- Las fechas deben ser válidas y los montos mayores que cero.
- El historial no puede estar vacío ni contener meses objetivo o posteriores.
- Se exigen tres meses calendario previos utilizables.
- Las predicciones deben ser finitas.

Cuando una predicción original es negativa se conserva en `raw_prediction`, se marca `nonnegative_adjustment=true` y se publica `projected_amount=max(0, raw_prediction)`. Este postprocesamiento no modifica ni reentrena el modelo.

## Modelo utilizado

El servicio reutiliza `GradientBoostingRegressor`, entrenado en T40 con datos completamente simulados. Las variables son categoría, mes, índice temporal desde 2024-01, tres rezagos, media móvil anterior y representación cíclica del mes.

## Limitaciones

Las proyecciones tienen finalidad académica e informativa y no constituyen asesoría financiera profesional. El entrenamiento se realizó con un escenario sintético controlado; el comportamiento con datos reales puede diferir. La evaluación formal de precisión se realiza por separado en el Ítem 22.
