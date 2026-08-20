"""API independiente del componente predictivo de Ahorro Smart."""

from fastapi import FastAPI, HTTPException, Response

from app.predictor import predictor
from app.schemas import PredictionRequest, PredictionResponse


app = FastAPI(
    title="Ahorro Smart - Servicio predictivo",
    description="Proyección informativa del gasto al cierre del mes en curso.",
    version="1.0.0",
)


@app.get("/health")
def health(response: Response):
    if not predictor.is_loaded:
        response.status_code = 503
    return {
        "status": "ok" if predictor.is_loaded else "unavailable",
        "service": "ahorro-smart-ia",
        "model_loaded": predictor.is_loaded,
        "model_name": predictor.model_name,
        "prediction_objective": predictor.prediction_objective,
        "sklearn_version": predictor.sklearn_version,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if not predictor.is_loaded:
        raise HTTPException(status_code=500, detail="El modelo predictivo no está disponible.")
    try:
        return predictor.predict(request.cutoff_date, request.expenses)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from None
    except RuntimeError:
        raise HTTPException(status_code=500, detail="No fue posible generar la proyección.") from None
