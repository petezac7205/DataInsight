from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from io import StringIO
from fastapi.responses import FileResponse
import tempfile
import os

# AI + analytics services
from services.ai_service import (
    build_ai_context,
    generate_insights,
    generate_query,
    generate_profile_insights
)

from services.query_service import generate_pandas_code, explain_query, execute_query
from services.analysis_service import (
    detect_strong_correlations,
    strongest_relationship,
    detect_outliers_iqr,
    dominant_categories
)

app = FastAPI()

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stored_df: pd.DataFrame | None = None
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit


# =====================================================
# Utilities
# =====================================================

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataframe by replacing inf and null values"""
    df = df.replace([np.inf, -np.inf], None)
    df = df.where(pd.notnull(df), None)
    return df


# =====================================================
# Upload CSV
# =====================================================

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    global stored_df

    # Read and validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")

    # Parse CSV with better error handling
    try:
        df = pd.read_csv(StringIO(contents.decode("utf-8")), low_memory=False)
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding error - ensure UTF-8")
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except Exception as e:
        print(f"CSV Parse Error: {e}")  # Log for debugging
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {str(e)}")

    # Validate dataframe has data
    if df.empty:
        raise HTTPException(status_code=400, detail="CSV contains no data")

    stored_df = clean_dataframe(df)

    return {
        "columns": list(stored_df.columns),
        "row_count": len(stored_df),
        "preview": stored_df.head(5).to_dict(orient="records")
    }


# =====================================================
# AI DATASET OVERVIEW
# =====================================================

@app.get("/ai/overview-insights")
def overview_insights():
    if stored_df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")

    context = build_ai_context(stored_df)
    insights = generate_insights(context)

    return {"insights": insights}


# =====================================================
# NLP → DATA QUERY (WITH EXPLANATION)
# =====================================================

@app.post("/ai/query")
def ai_query(payload: dict):
    if stored_df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")

    question = payload.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Missing question")

    query_json = generate_query(question, list(stored_df.columns))

    if "clarification_needed" in query_json:
        return query_json

    try:
        result = execute_query(stored_df, query_json)
        
        # Import the simple version
        from services.query_service import generate_pandas_code_simple
        
        return {
            "structured_query": query_json,
            "pandas_code": generate_pandas_code(query_json),  # Full version with comments
            "pandas_code_simple": generate_pandas_code_simple(query_json),  # One-liner
            "explanation": explain_query(query_json),
            "answer": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# =====================================================
# SMART DATA PROFILING (REAL ANALYTICS)
# =====================================================

@app.get("/ai/deep-profile")
def deep_profile():
    if stored_df is None:
        raise HTTPException(status_code=400, detail="No dataset uploaded")

    raw_profile = {
        "strong_correlations": detect_strong_correlations(stored_df),
        "strongest_relationship": strongest_relationship(stored_df),
        "outliers": detect_outliers_iqr(stored_df),
        "dominant_categories": dominant_categories(stored_df)
    }

    ai_summary = generate_profile_insights(raw_profile)

    return {
        "raw_profile": raw_profile,
        "ai_insights": ai_summary
    }


# =====================================================
# EXPORT CSV
# =====================================================

@app.get("/export/csv")
def export_csv():
    if stored_df is None:
        raise HTTPException(status_code=400, detail="No dataset available")

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as tmp:
        stored_df.to_csv(tmp.name, index=False)
        temp_path = tmp.name

    return FileResponse(
        path=temp_path,
        filename="dataset.csv",
        media_type="text/csv",
        background=lambda: os.unlink(temp_path)  # Auto-cleanup after sending
    )


# =====================================================
# Health Check (Optional but Recommended)
# =====================================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "dataset_loaded": stored_df is not None,
        "rows": len(stored_df) if stored_df is not None else 0
    }