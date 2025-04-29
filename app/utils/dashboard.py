from fastapi import HTTPException
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from google.cloud import storage
import joblib
from io import BytesIO

from app.utils.model_prediction_utils import load_dataset

MODEL_PATH = "./app/xgboosterDemo.pkl"
BUCKET_NAME = "smartinv"

def get_stock_pie(df: pd.DataFrame) -> list[dict]:
    """
    Returns a list of { item, quantity } using stock_final from the most recent month per product.
    """
    if 'period' not in df.columns:
        df['period'] = pd.to_datetime(
            df['anio'].astype(str) + '-' + df['mes'].astype(str) + '-01'
        )
    max_period = df['period'].max()
    pie = []
    prod_cols = [c for c in df.columns if c.startswith('nombre_producto_')]
    for col in prod_cols:
        item = col.replace('nombre_producto_', '')
        row = df[(df[col] == 1) & (df['period'] == max_period)]
        qty = int(row['stock_final'].iloc[0]) if not row.empty else 0
        pie.append({'item': item, 'quantity': qty})
    return pie

# TODO: i think i should fix this
def get_total_revenues(df: pd.DataFrame, months: int = 5) -> list[dict]:
    """
    Returns monthly list { period: "YYYY-MM", revenue: float } for the last `months` months based on dataset.
    """
    df_copy = df.copy()
    df_copy['period'] = pd.to_datetime(
        df_copy['anio'].astype(str) + '-' + df_copy['mes'].astype(str) + '-01'
    )
    df_copy['revenue'] = df_copy['unidades_vendidas'] * df_copy['precio_unitario']
    max_period = df_copy['period'].max()
    cutoff = max_period - relativedelta(months=months)
    df_filtered = df_copy[df_copy['period'] > cutoff]
    agg = (
        df_filtered
        .groupby(df_filtered['period'].dt.to_period('M'))['revenue']
        .sum()
        .reset_index()
        .sort_values('period')
    )
    return [
        {'period': str(row['period']), 'revenue': float(row['revenue'])}
        for _, row in agg.iterrows()
    ]


def get_stock_evolution_and_prediction(
    company_name: str,
    item_name: str,
    months: int = 3
) -> dict:
    """
    Returns:
      - 'series': [{ period: "YYYY-MM", stock: float }] for the last `months` months
      - 'prediction': { period: "YYYY-MM", value: float } for next month
    """
    storage_client = storage.Client()
    df = load_dataset(storage_client, company_name.lower())
    df['period'] = pd.to_datetime(
        df['anio'].astype(str) + '-' + df['mes'].astype(str) + '-01'
    )
    col_prod = f'nombre_producto_{item_name}'
    if col_prod not in df.columns:
        raise HTTPException(status_code=400, detail=f"Product '{item_name}' not found")
    df_p = df[df[col_prod] == 1].copy()
    max_period = df_p['period'].max()
    cutoff = max_period - relativedelta(months=months)
    df_hist = df_p[df_p['period'] > cutoff]
    agg = (
        df_hist
        .groupby(df_hist['period'].dt.to_period('M'))['stock_final']
        .mean()
        .reset_index()
        .sort_values('period')
    )
    series = [
        {'period': str(row['period']), 'stock': float(row['stock_final'])}
        for _, row in agg.iterrows()
    ]
    next_period = (max_period + relativedelta(months=1)).to_period('M').strftime('%Y-%m')
    X_next = df_p[df_p['period'] == max_period].drop(columns=['reposicion_este_mes', 'period'])
    model = joblib.load(MODEL_PATH)
    pred = model.predict(X_next).round()
    value = float(pred[0]) if len(pred) else 0.0
    return {
        'series': series,
        'prediction': {'period': next_period, 'value': value}
    }
