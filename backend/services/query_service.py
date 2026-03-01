import pandas as pd
import numpy as np


# =====================================================
# MAIN QUERY EXECUTION
# =====================================================

def execute_query(df: pd.DataFrame, query: dict):
    """Execute structured query on dataframe with comprehensive error handling"""
    working_df = df.copy()

    # ---------------- Filters ----------------
    for f in query.get("filters", []):
        col = f["column"]
        op = f["operator"]
        val = f["value"]

        # Validate column exists
        if col not in working_df.columns:
            raise ValueError(f"Column '{col}' not found in dataset")

        # Handle comparison operators
        try:
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
            elif op == "contains":
                working_df = working_df[
                    working_df[col].astype(str).str.contains(str(val), case=False, na=False)
                ]
            else:
                raise ValueError(f"Unsupported operator '{op}'")
                
        except TypeError as e:
            raise ValueError(
                f"Type mismatch: Cannot compare column '{col}' with value '{val}'. "
                f"Column type: {working_df[col].dtype}"
            )

    # Check if filters left any data
    if len(working_df) == 0:
        return {"error": "No data matches the specified filters", "result": None}

    # ---------------- Grouping ----------------
    group_col = query.get("groupby")

    if group_col:
        if group_col not in working_df.columns:
            raise ValueError(f"Groupby column '{group_col}' not found")

        working_df = working_df.groupby(group_col)

    # ---------------- Aggregation ----------------
    agg = query["aggregation"]
    column = query.get("column")

    try:
        if agg == "count":
            if hasattr(working_df, "groups"):
                result = working_df.size()
            else:
                result = len(working_df)

        elif agg == "mean":
            if not column:
                raise ValueError("Column required for 'mean' aggregation")
            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found")
            result = working_df[column].mean()

        elif agg == "sum":
            if not column:
                raise ValueError("Column required for 'sum' aggregation")
            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found")
            result = working_df[column].sum()

        elif agg == "min":
            if not column:
                raise ValueError("Column required for 'min' aggregation")
            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found")
            result = working_df[column].min()

        elif agg == "max":
            if not column:
                raise ValueError("Column required for 'max' aggregation")
            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found")
            result = working_df[column].max()

        elif agg == "median":
            if not column:
                raise ValueError("Column required for 'median' aggregation")
            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found")
            result = working_df[column].median()

        else:
            raise ValueError(f"Unsupported aggregation: '{agg}'")

    except (KeyError, TypeError) as e:
        raise ValueError(f"Aggregation failed: {str(e)}")

    # ---------------- Math Modifier ----------------
    if "multiply" in query:
        try:
            result = result * query["multiply"]
        except TypeError:
            raise ValueError("Cannot multiply result - incompatible types")

    # ---------------- JSON Safe Output ----------------
    if isinstance(result, pd.Series):
        result = result.replace([np.inf, -np.inf], None)
        result = result.where(pd.notnull(result), None)
        return result.to_dict()

    if pd.isna(result) or np.isinf(result):
        return None

    if isinstance(result, (np.integer, np.floating)):
        return float(result)

    return result


# =====================================================
# QUERY EXPLANATION (ENGLISH)
# =====================================================

def explain_query(query_json: dict):
    """Generate human-readable explanation of the query"""
    parts = []

    if query_json.get("filters"):
        filters_text = ", ".join(
            f"{f['column']} {f['operator']} {f['value']}"
            for f in query_json["filters"]
        )
        parts.append(f"Filter rows where {filters_text}")

    if query_json.get("groupby"):
        parts.append(f"group by {query_json['groupby']}")

    agg = query_json["aggregation"]
    col = query_json.get("column")

    if agg == "count":
        parts.append("count rows")
    else:
        parts.append(f"compute {agg} of {col}")

    if query_json.get("multiply"):
        parts.append(f"multiply by {query_json['multiply']}")

    return " → ".join(parts).capitalize() + "."


# =====================================================
# PANDAS CODE GENERATOR (COPY-PASTE READY)
# =====================================================

def generate_pandas_code(query):
    """Generate complete, ready-to-run pandas code with imports"""
    lines = []
    
    # Add imports
    lines.append("# Import required libraries")
    lines.append("import pandas as pd")
    lines.append("import numpy as np")
    lines.append("")
    lines.append("# Load your dataset")
    lines.append("# df = pd.read_csv('your_file.csv')  # Uncomment and modify path")
    lines.append("")
    lines.append("# Execute query")
    
    code = "result = df"

    # Filters
    if query.get("filters"):
        filter_parts = []
        for f in query["filters"]:
            col = f["column"]
            op = f["operator"]
            val = f["value"]

            if isinstance(val, str):
                val_str = f"'{val}'"
            else:
                val_str = str(val)

            if op == "contains":
                filter_parts.append(f"df['{col}'].str.contains('{val}', case=False, na=False)")
            else:
                filter_parts.append(f"(df['{col}'] {op} {val_str})")

        if len(filter_parts) == 1:
            code += f"[{filter_parts[0]}]"
        else:
            # Use bitwise AND (&) for multiple conditions in pandas
            code += "[" + " & ".join(filter_parts) + "]"

    # Groupby
    if query.get("groupby"):
        code += f".groupby('{query['groupby']}')"

    # Aggregation
    agg = query["aggregation"]
    col = query.get("column")

    if agg == "count":
        code += ".size()"
    else:
        code += f"['{col}'].{agg}()"

    # Multiply
    if query.get("multiply"):
        code += f" * {query['multiply']}"

    lines.append(code)
    lines.append("")
    lines.append("# Display result")
    lines.append("print(result)")
    
    return "\n".join(lines)

# =====================================================
# SIMPLE CODE (NO COMMENTS)
# =====================================================

def generate_pandas_code_simple(query):
    """Generate just the core pandas code line without comments"""
    code = "result = df"

    if query.get("filters"):
        filter_parts = []
        for f in query["filters"]:
            col = f["column"]
            op = f["operator"]
            val = f["value"]

            if isinstance(val, str):
                val_str = f"'{val}'"
            else:
                val_str = str(val)

            if op == "contains":
                filter_parts.append(f"df['{col}'].str.contains('{val}', case=False, na=False)")
            else:
                filter_parts.append(f"(df['{col}'] {op} {val_str})")

        if filter_parts:
            code += "[" + " & ".join(filter_parts) + "]"

    if query.get("groupby"):
        code += f".groupby('{query['groupby']}')"

    agg = query["aggregation"]
    col = query.get("column")

    if agg == "count":
        code += ".size()"
    else:
        code += f"['{col}'].{agg}()"

    if query.get("multiply"):
        code += f" * {query['multiply']}"

    return code