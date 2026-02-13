from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from io import StringIO

# AI + Query + Plot services
from services.ai_service import (
    build_ai_context,
    generate_insights,
    generate_query,
    generate_chart_insights
)
from fastapi.responses import FileResponse
from services.ai_module import ensure_ai_ready
from services.dataset_store import load_dataset, save_dataset
from services.query_service import execute_query
from services.plot_service import generate_plot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Utilities ----------

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.replace([np.inf, -np.inf], None)
    df = df.where(pd.notnull(df), None)
    return df


# ---------- Upload CSV ----------

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file")

    df = clean_dataframe(df)
    save_dataset(df)

    return {
        "columns": list(df.columns),
        "preview": df.head(5).to_dict(orient="records"),
        "row_count": len(df)
    }


# ---------- Dataset Overview ----------

@app.get("/stats")
def get_stats():
    stored_df = load_dataset()

    return {
        "null_counts": stored_df.isnull().sum().to_dict(),
        "dtypes": stored_df.dtypes.astype(str).to_dict(),
        "shape": {
            "rows": stored_df.shape[0],
            "columns": stored_df.shape[1]
        }
    }


# ---------- Column Analytics ----------

@app.get("/column-stats")
def column_stats(column: str = Query(...)):
    stored_df = load_dataset()

    if column not in stored_df.columns:
        raise HTTPException(status_code=404, detail="Column not found")

    series = stored_df[column]

    if not pd.api.types.is_numeric_dtype(series):
        return {"message": "Selected column is not numeric"}

    return {
        "mean": float(series.mean()),
        "median": float(series.median()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max())
    }


# ---------- AI Overview Insights ----------
@app.get("/ai/overview-insights")
def ai_overview_insights():
    stored_df = load_dataset()

    try:
        ensure_ai_ready()
        context = build_ai_context(stored_df)
        insights = generate_insights(context)
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

# ---------- NLP DATA QUERY (CHAT WITH CSV) ----------

@app.post("/ai/query")
def ai_query(payload: dict):
    stored_df = load_dataset()

    if "question" not in payload:
        raise HTTPException(status_code=400, detail="Missing question")

    user_question = payload["question"]

    ensure_ai_ready()

    query_json = generate_query(
        user_question,
        list(stored_df.columns)
    )

    if "clarification_needed" in query_json:
        return query_json

    try:
        result = execute_query(stored_df, query_json)
        return {
            "structured_query": query_json,
            "answer": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------- PLOT GENERATION ----------

@app.post("/plot")
def create_plot(config: dict):
    stored_df = load_dataset()

    try:
        fig_json = generate_plot(stored_df, config)
        return {"plot": fig_json}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
