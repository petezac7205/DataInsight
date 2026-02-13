import pandas as pd
import numpy as np

def profile_dataframe(df: pd.DataFrame):
    df_clean = df.replace([np.inf, -np.inf], None)
    df_clean = df_clean.where(pd.notnull(df_clean), None)

    numeric_cols = df_clean.select_dtypes(include=["number"]).columns
    categorical_cols = df_clean.select_dtypes(include=["object"]).columns

    return {
        "shape": {
            "rows": df_clean.shape[0],
            "columns": df_clean.shape[1]
        },
        "dtypes": df_clean.dtypes.astype(str).to_dict(),
        "null_counts": df_clean.isnull().sum().to_dict(),
        "numeric_summary": df_clean[numeric_cols].describe().to_dict() if len(numeric_cols) > 0 else {},
        "categorical_summary": {
            col: {
                "unique": df_clean[col].nunique(),
                "top": df_clean[col].mode()[0] if not df_clean[col].mode().empty else None
            }
            for col in categorical_cols
        }
    }
