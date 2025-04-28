from fastapi import HTTPException
import pandas as pd
from io import BytesIO

BUCKET_NAME = "smartinv"

def load_dataset(storage_client, company_name:str) -> pd.DataFrame:
    """Returns a dataset from the bucket
    @param storage_client: the client used for interacting
    @param company_name: the company name in lowercase
    """
    blobs = list(storage_client.list_blobs(
        BUCKET_NAME, prefix=f"{company_name}/data/"
    ))
    dataset_blobs = [
        b for b in blobs
        if "dataset_" in b.name and b.name.endswith(".csv")
    ]
    if not dataset_blobs:
        raise HTTPException(status_code=404, detail="No dataset found for this company.")
    latest_blob = sorted(dataset_blobs, key=lambda b: b.name, reverse=True)[0]
    raw = latest_blob.download_as_bytes()
    df = pd.read_csv(BytesIO(raw))
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df