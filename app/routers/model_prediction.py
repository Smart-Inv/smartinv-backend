from fastapi import APIRouter, HTTPException, Query
from google.cloud import storage
import pandas as pd
import os
import joblib
from io import BytesIO

router = APIRouter()
BUCKET_NAME = "smartinv"
MODEL_PATH = "./app/xgboosterDemo.pkl"

@router.get("/predict_values/", tags=["model"])
async def predict_values(company_name: str = Query(...)):

    storage_client = storage.Client()
    
    company_name = company_name.lower()

    # route for folder pred
    y_pred_path = f"{company_name}/predictions/y_pred.csv"

    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(y_pred_path)

        if blob.exists():
            # exists, we return it
            data = blob.download_as_bytes()
            df = pd.read_csv(BytesIO(data))
            return df.to_dict(orient="records")

        # otherwise, we must predict it
        blobs = list(storage_client.list_blobs(BUCKET_NAME, prefix=f"{company_name}/data/"))
        dataset_blobs = [b for b in blobs if "dataset_" in b.name and b.name.endswith(".csv") and "predictions" not in b.name]
        
        if not dataset_blobs:
            raise HTTPException(status_code=404, detail="No dataset found for this company.")

        # take latest
        latest_blob = sorted(dataset_blobs, key=lambda b: b.name, reverse=True)[0]
        dataset_bytes = latest_blob.download_as_bytes()
        df = pd.read_csv(BytesIO(dataset_bytes))
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        with open(MODEL_PATH, "rb") as f:
            model = joblib.load(f)

        y_pred = model.predict(df).round()
        df_pred = pd.DataFrame({"prediction": y_pred})

        # upload pred
        pred_blob = bucket.blob(y_pred_path)
        pred_blob.upload_from_string(df_pred.to_csv(index=False), content_type="text/csv")

        return df_pred.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
