import pandas as pd
from fastapi import UploadFile
from io import StringIO
import numpy as np

async def parse_csv(file: UploadFile):
    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode("utf-8")))

    # Replace invalid JSON values
    df = df.replace([np.inf, -np.inf], None)
    df = df.where(pd.notnull(df), None)

    return {
        "columns": list(df.columns),
        "preview": df.head(5).to_dict(orient="records"),
        "row_count": len(df)
    }
