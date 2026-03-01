import pandas as pd
import numpy as np


# =====================================================
# CORRELATION ANALYSIS
# =====================================================

def detect_strong_correlations(df: pd.DataFrame, threshold: float = 0.6):
    """Detect pairs of features with strong correlation"""
    numeric_df = df.select_dtypes(include="number")

    # Check if enough numeric columns
    if numeric_df.shape[1] < 2:
        return []

    # Drop columns with too many nulls (>50%)
    numeric_df = numeric_df.loc[:, numeric_df.isnull().sum() / len(numeric_df) < 0.5]

    if numeric_df.shape[1] < 2:
        return []

    # Compute correlation matrix
    corr = numeric_df.corr().abs()

    # Find strong correlations (upper triangle only to avoid duplicates)
    strong_pairs = []
    for i, col in enumerate(corr.columns):
        for j, idx in enumerate(corr.index):
            if i < j and corr.loc[col, idx] >= threshold:
                # Check for valid correlation (not NaN)
                if not pd.isna(corr.loc[col, idx]):
                    strong_pairs.append({
                        "feature_1": col,
                        "feature_2": idx,
                        "correlation": float(corr.loc[col, idx])
                    })

    # Sort by correlation strength
    strong_pairs.sort(key=lambda x: x["correlation"], reverse=True)

    return strong_pairs


def strongest_relationship(df: pd.DataFrame):
    """Find the single strongest correlation in the dataset"""
    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] < 2:
        return None

    # Drop columns with too many nulls
    numeric_df = numeric_df.loc[:, numeric_df.isnull().sum() / len(numeric_df) < 0.5]

    if numeric_df.shape[1] < 2:
        return None

    # Compute correlation
    corr = numeric_df.corr().abs()

    # Mask diagonal (self-correlation)
    np.fill_diagonal(corr.values, 0)

    # Replace NaN with 0
    corr = corr.fillna(0)

    # Find maximum correlation
    max_corr = corr.unstack().idxmax()
    value = corr.unstack().max()

    if pd.isna(value) or value == 0:
        return None

    return {
        "feature_1": max_corr[0],
        "feature_2": max_corr[1],
        "correlation": float(value)
    }


# =====================================================
# OUTLIER DETECTION
# =====================================================

def detect_outliers_iqr(df: pd.DataFrame):
    """Detect outliers using IQR method for each numeric column"""
    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        return {}

    outlier_summary = {}

    for col in numeric_df.columns:
        # Skip columns with all NaN
        if numeric_df[col].isna().all():
            continue

        # Calculate IQR
        Q1 = numeric_df[col].quantile(0.25)
        Q3 = numeric_df[col].quantile(0.75)
        IQR = Q3 - Q1

        # Skip if IQR is 0 (no variance)
        if IQR == 0:
            continue

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        # Find outliers
        outliers = numeric_df[(numeric_df[col] < lower) | (numeric_df[col] > upper)]

        if len(outliers) > 0:
            outlier_summary[col] = {
                "count": len(outliers),
                "percentage": round(len(outliers) / len(df) * 100, 2),
                "range": {
                    "lower_bound": float(lower),
                    "upper_bound": float(upper)
                }
            }

    return outlier_summary


# =====================================================
# DISTRIBUTION ANALYSIS
# =====================================================

def detect_skewed_columns(df: pd.DataFrame, threshold: float = 1.0):
    """Detect columns with skewed distributions"""
    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        return {}

    skewed = {}

    for col in numeric_df.columns:
        # Skip columns with insufficient data
        if numeric_df[col].nunique() < 3 or numeric_df[col].isna().sum() / len(df) > 0.5:
            continue

        try:
            skew_value = numeric_df[col].skew()
            
            if pd.isna(skew_value):
                continue

            if abs(skew_value) > threshold:
                skewed[col] = {
                    "skewness": float(skew_value),
                    "direction": "right" if skew_value > 0 else "left"
                }
        except Exception:
            continue

    return skewed


# =====================================================
# CATEGORICAL ANALYSIS
# =====================================================

def dominant_categories(df: pd.DataFrame, threshold: float = 0.8):
    """Find categorical columns dominated by a single value"""
    categorical = df.select_dtypes(include=["object", "category"])

    if categorical.empty:
        return {}

    dominance = {}

    for col in categorical.columns:
        # Skip if too many nulls
        if df[col].isna().sum() / len(df) > 0.5:
            continue

        value_counts = df[col].value_counts(normalize=True, dropna=True)
        
        if len(value_counts) == 0:
            continue

        top_ratio = value_counts.iloc[0]
        
        if top_ratio > threshold:
            dominance[col] = {
                "dominant_value": value_counts.index[0],
                "percentage": float(top_ratio * 100),
                "unique_count": len(value_counts)
            }

    return dominance


def segment_analysis(df: pd.DataFrame, target_col: str, top_n: int = 3):
    """Analyze target metric across categorical segments"""
    if target_col not in df.columns:
        return {"error": f"Column '{target_col}' not found"}

    if not pd.api.types.is_numeric_dtype(df[target_col]):
        return {"error": f"Column '{target_col}' must be numeric"}

    categorical_cols = df.select_dtypes(include=["object", "category"]).columns

    if len(categorical_cols) == 0:
        return {"error": "No categorical columns found for segmentation"}

    insights = {}

    for col in categorical_cols:
        try:
            grouped = df.groupby(col)[target_col].agg(['mean', 'count'])
            
            # Filter out segments with too few samples
            grouped = grouped[grouped['count'] >= 5]
            
            if len(grouped) == 0:
                continue

            # Sort by mean and get top N
            grouped = grouped.sort_values('mean', ascending=False).head(top_n)
            
            insights[col] = {
                segment: {
                    "mean": float(row['mean']),
                    "count": int(row['count'])
                }
                for segment, row in grouped.iterrows()
            }
        except Exception:
            continue

    return insights


# =====================================================
# DATA QUALITY CHECKS
# =====================================================

def data_quality_summary(df: pd.DataFrame):
    """Comprehensive data quality report"""
    total_rows = len(df)
    
    quality = {
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "missing_data": {},
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage_mb": float(df.memory_usage(deep=True).sum() / 1024 / 1024)
    }

    # Missing data analysis
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            quality["missing_data"][col] = {
                "count": int(null_count),
                "percentage": float(null_count / total_rows * 100)
            }

    return quality


# =====================================================
# COMPREHENSIVE PROFILE (COMBINES ALL)
# =====================================================

def comprehensive_profile(df: pd.DataFrame):
    """Run all analysis functions and return complete profile"""
    return {
        "data_quality": data_quality_summary(df),
        "strong_correlations": detect_strong_correlations(df),
        "strongest_relationship": strongest_relationship(df),
        "outliers": detect_outliers_iqr(df),
        "skewed_distributions": detect_skewed_columns(df),
        "dominant_categories": dominant_categories(df)
    }