def execute_query(df, query):
    working_df = df.copy()

    # -------- Filters --------
    if "filters" in query:
        for f in query["filters"]:
            col = f["column"]
            op = f["operator"]
            val = f["value"]

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

    # -------- Grouping --------
    if "groupby" in query:
        working_df = working_df.groupby(query["groupby"])

    agg = query["aggregation"]
    column = query.get("column")

    # -------- Aggregations --------
    if agg == "mean":
        result = working_df[column].mean()
    elif agg == "sum":
        result = working_df[column].sum()
    elif agg == "count":
        if hasattr(working_df, "groups"):  
            # If grouped
            result = working_df.size()
        else:
            # Normal dataframe
            result = len(working_df)
    elif agg == "min":
        result = working_df[column].min()
    elif agg == "max":
        result = working_df[column].max()
    elif agg == "median":
        result = working_df[column].median()
    else:
        raise ValueError("Unsupported aggregation")

    # -------- Math modifier --------
    if "multiply" in query:
        result = result * query["multiply"]

    # Convert pandas result to JSON safe
    if hasattr(result, "to_dict"):
        return result.to_dict()

    return float(result)
