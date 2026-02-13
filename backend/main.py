from fastapi import FastAPI, UploadFile, File, HTTPException, Query
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
from services.query_service import execute_query
from services.plot_service import generate_plot

app = FastAPI()

stored_df: pd.DataFrame | None = None


# =====================================================
# Utilities
# =====================================================

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.replace([np.inf, -np.inf], None)
    df = df.where(pd.notnull(df), None)
    return df


# =====================================================
# Upload CSV
# =====================================================

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    global stored_df

    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file")

    df = clean_dataframe(df)
    stored_df = df

    return {
        "columns": list(df.columns),
        "preview": df.head(5).to_dict(orient="records"),
        "row_count": len(df)
    }


# =====================================================
# Dataset Overview
# =====================================================

@app.get("/stats")
def get_stats():
    if stored_df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")

    return {
        "null_counts": stored_df.isnull().sum().to_dict(),
        "dtypes": stored_df.dtypes.astype(str).to_dict(),
        "shape": {
            "rows": stored_df.shape[0],
            "columns": stored_df.shape[1]
        }
    }


# =====================================================
# Column Analytics
# =====================================================

@app.get("/column-stats")
def column_stats(column: str = Query(...)):
    if stored_df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")

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


# =====================================================
# AI Dataset Insights
# =====================================================

@app.get("/ai/overview-insights")
def ai_overview_insights():
    if stored_df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")

    try:
        context = build_ai_context(stored_df)
        insights = generate_insights(context)
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


# =====================================================
# NLP Query (Chat with CSV)
# =====================================================

@app.post("/ai/query")
def ai_query(payload: dict):
    if stored_df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")

    if "question" not in payload:
        raise HTTPException(status_code=400, detail="Missing question")

    user_question = payload["question"]

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


# =====================================================
# Plot Generation
# =====================================================

@app.post("/plot")
def create_plot(config: dict):
    if stored_df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")

    try:
        # 1. Generate plot
        fig_json = generate_plot(stored_df, config)

        # 2. Prepare data for insight generation
        working_df = stored_df.copy()

        filters = config.get("filters", [])
        if filters:
            from services.plot_service import apply_filters
            working_df = apply_filters(working_df, filters)

        x = config.get("x")
        y = config.get("y")
        aggregation = config.get("aggregation")

        if aggregation and x and y:
            from services.plot_service import aggregate_data

            plot_df = aggregate_data(working_df, x, y, aggregation)
        else:
            plot_df = working_df[[x, y]].dropna()

        # 3. Build compressed insight context (efficient!)
        chart_context = {
            "chart_type": config["chart_type"],
            "x": x,
            "y": y,
            "aggregation": aggregation,
            "row_count": len(plot_df),
            "y_stats": {
                "min": float(plot_df[y].min()) if y else None,
                "max": float(plot_df[y].max()) if y else None,
                "mean": float(plot_df[y].mean()) if y else None
            }
        }

        # 4. Generate AI insights automatically
        insights = generate_chart_insights(chart_context)

        return {
            "plot": fig_json,
            "insights": insights
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




# =====================================================
# NEW — AI Chart Insights
# =====================================================




# =====================================================
# NEW — TRANSFORMATION FOR ROWS AND COLUMNS
# =====================================================

@app.post("/transform")
def transform_data(config: dict):
    global stored_df

    if stored_df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")

    try:
        from services.transform_service import transform_dataframe

        stored_df = transform_dataframe(stored_df, config)

        return {
            "columns": list(stored_df.columns),
            "row_count": len(stored_df),
            "preview": stored_df.head(5).to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =====================================================
# EXPORT CSV
# =====================================================

from fastapi.responses import FileResponse


@app.get("/export/csv")
def export_csv():
    global stored_df

    if stored_df is None:
        raise HTTPException(status_code=400, detail="No dataset available")

    file_path = "exported_dataset.csv"

    # Save current dataframe (after transforms if any)
    stored_df.to_csv(file_path, index=False)

    return FileResponse(
        path=file_path,
        filename="modified_dataset.csv",
        media_type="text/csv"
    )
