from fastapi import APIRouter, HTTPException, Query, Depends
from google.cloud import storage
import pandas as pd
import joblib
from io import BytesIO

from app.utils.token_generation import get_current_user
from app.utils.model_prediction_utils import *

router = APIRouter()
BUCKET_NAME = "smartinv"
MODEL_PATH = "./app/xgboosterDemo.pkl"

@router.get("/predict_values/", tags=["model"])
async def predict_values(
    token: str = Depends(get_current_user), 
    company_name: str = Query(...)
    ):

    storage_client = storage.Client()
    company_name = company_name.lower()

    df = load_dataset(storage_client, company_name)

    # try to get previous prediction
    y_pred_blob = storage_client.bucket(BUCKET_NAME).blob(
        f"{company_name}/predictions/y_pred.csv"
    )
    if y_pred_blob.exists():
        preds = y_pred_blob.download_as_bytes()
        df_pred = pd.read_csv(BytesIO(preds))
        df["prediction"] = df_pred["prediction"]
        return df.to_dict(orient="records")

    # if not, predict and add column
    model = joblib.load(MODEL_PATH)
    y_pred = model.predict(df).round()
    df["prediction"] = y_pred

    # upload just the PREDICTION
    pred_csv = df[["prediction"]].to_csv(index=False)
    y_pred_blob.upload_from_string(pred_csv, content_type="text/csv")

    # return the entire dataset
    return df.to_dict(orient="records")
