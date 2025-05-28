from fastapi import APIRouter, HTTPException, Depends
from google.cloud import storage
from app.firestore_client import db
from app.utils.model_prediction_utils import load_dataset
from app.utils.dashboard import get_stock_pie, get_total_revenues, get_stock_evolution
from app.utils.token_generation import oauth2_scheme, get_current_user
from app.routers.model_prediction import predict_values

router = APIRouter()
BUCKET_NAME = "smartinv"

@router.get("/dashboard_data/", tags=["dashboard"])
async def dashboard_data(
    token: str = Depends(oauth2_scheme),
    current_user: dict = Depends(get_current_user)
):
    # fetch user → company
    email = current_user["email"]
    query = db.collection("users").where("email", "==", email).limit(1).stream()
    user_doc = next(query, None)
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    company = user_doc.to_dict()["name_company"].replace(" ", "").lower()

    # load df for stock & revenues
    storage_client = storage.Client()
    df = load_dataset(storage_client, company)

    #stock_pie = get_stock_pie(df)
    revenues  = get_total_revenues(df)

    # build items list
    items = [c.replace("nombre_producto_", "") for c in df.columns
             if c.startswith("nombre_producto_")]

    # pull full predictions table from your existing endpoint
    full = await predict_values(token, company)

    # for each item, grab the row for the most recent (anio,mes)
    predictions = []
    series = {}
    for item in items:
        col = f"nombre_producto_{item}"

        rows = [r for r in full if r.get(col) == 1]
        if not rows:
            continue

        latest = max(rows, key=lambda r: (r["anio"], r["mes"]))
        predictions.append({
            "item":       item,
            "prediction": float(latest["prediction"])
        })

        series[col] = get_stock_evolution(storage_client, company, col)

    return {
        "revenues":    revenues,
        "items":       items,
        "predictions": predictions,
        "series": series
    }
