import pandas as pd
import plotly.express as px
import json


# -------------------- Filters --------------------

def apply_filters(df: pd.DataFrame, filters: list):
    working_df = df.copy()

    for f in filters:
        col = f["column"]
        op = f["operator"]
        val = f["value"]

        if col not in working_df.columns:
            raise ValueError(f"Column '{col}' not found")

        if op == "==":
            working_df = working_df[working_df[col] == val]
        elif op == ">":
            working_df = working_df[working_df[col] > val]
        elif op == "<":
            working_df = working_df[working_df[col] < val]
        elif op == ">=":
            working_df = working_df[working_df[col] >= val]
        elif op == "<=":
            working_df = working_df[working_df[col] <= val]
        else:
            raise ValueError(f"Unsupported operator {op}")

    return working_df


# -------------------- Aggregation --------------------

def aggregate_data(df: pd.DataFrame, x: str, y: str, aggregation: str):
    if x not in df.columns or y not in df.columns:
        raise ValueError("Invalid columns for aggregation")

    return (
        df.groupby(x)[y]
        .agg(aggregation)
        .reset_index()
    )


# -------------------- Plot Generator --------------------

def generate_plot(df: pd.DataFrame, config: dict):

    chart_type = config["chart_type"]
    x = config.get("x")
    y = config.get("y")
    aggregation = config.get("aggregation")
    color = config.get("color")
    filters = config.get("filters", [])

    working_df = df.copy()

    # ---------- Apply filters ----------
    if filters:
        working_df = apply_filters(working_df, filters)

    if working_df.empty:
        raise ValueError("No data available after filters")

    # ---------- Aggregation ----------
    if aggregation and x and y:
        working_df = aggregate_data(working_df, x, y, aggregation)

    # ---------- Plot types ----------

    if chart_type == "bar":
        if not x or not y:
            raise ValueError("Bar chart requires x and y")
        fig = px.bar(working_df, x=x, y=y, color=color)

    elif chart_type == "line":
        if not x or not y:
            raise ValueError("Line chart requires x and y")
        fig = px.line(working_df, x=x, y=y, color=color)

    elif chart_type == "scatter":
        if not x or not y:
            raise ValueError("Scatter requires x and y")
        fig = px.scatter(working_df, x=x, y=y, color=color)

    elif chart_type == "histogram":
        if not x:
            raise ValueError("Histogram requires x")
        fig = px.histogram(working_df, x=x, color=color)

    elif chart_type == "box":
        if not x or not y:
            raise ValueError("Box plot requires x and y")
        fig = px.box(working_df, x=x, y=y, color=color)

    elif chart_type == "heatmap":

        numeric_df = working_df.select_dtypes(include="number")

        if numeric_df.shape[1] < 2:
            raise ValueError("Heatmap requires at least 2 numeric columns")

        corr = numeric_df.corr()

        # Fix NaNs (very important)
        corr = corr.fillna(0)

        fig = px.imshow(
            corr.values,
            x=corr.columns,
            y=corr.columns,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu",
            title="Correlation Heatmap"
        )


    else:
        raise ValueError("Unsupported chart type")

    # Convert to plain JSON-safe Python structures.
    return json.loads(fig.to_json())

