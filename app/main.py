from fastapi import FastAPI, HTTPException
from app.schemas.predict import PredictRequest, PredictResponse
from app.ml.model import load_model

app = FastAPI(
    title="ML Model Deployment API",
    description="API exposing a machine learning model",
    version="1.0.0"
)

model = load_model()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    try:
        prediction = model.predict([request.features])[0]
        return PredictResponse(prediction=prediction)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
