import pandas as pd


# =====================================================
# ROW OPERATIONS
# =====================================================

def apply_filter(df, operation):
    conditions = operation["conditions"]
    logic = operation.get("logic", "AND")

    masks = []

    for cond in conditions:
        col = cond["column"]
        op = cond["operator"]
        val = cond["value"]

        if op == "==":
            masks.append(df[col] == val)
        elif op == ">":
            masks.append(df[col] > val)
        elif op == "<":
            masks.append(df[col] < val)
        elif op == ">=":
            masks.append(df[col] >= val)
        elif op == "<=":
            masks.append(df[col] <= val)
        else:
            raise ValueError(f"Unsupported operator {op}")

    if logic == "AND":
        mask = masks[0]
        for m in masks[1:]:
            mask &= m
    else:
        mask = masks[0]
        for m in masks[1:]:
            mask |= m

    return df[mask]


def top_n(df, column, n):
    return df.sort_values(by=column, ascending=False).head(n)


def bottom_n(df, column, n):
    return df.sort_values(by=column, ascending=True).head(n)


def random_sample(df, n):
    return df.sample(n=n)


def drop_null_rows(df):
    return df.dropna()


def row_range(df, start, end):
    return df.iloc[start:end]


def remove_duplicates(df):
    return df.drop_duplicates()


# =====================================================
# COLUMN OPERATIONS
# =====================================================

def select_columns(df, columns):
    return df[columns]


def drop_columns(df, columns):
    return df.drop(columns=columns)


def rename_columns(df, mapping):
    return df.rename(columns=mapping)


def reorder_columns(df, columns):
    return df[columns]


def fill_null(df, column, method, value=None):
    if method == "mean":
        df[column] = df[column].fillna(df[column].mean())
    elif method == "median":
        df[column] = df[column].fillna(df[column].median())
    elif method == "mode":
        df[column] = df[column].fillna(df[column].mode()[0])
    elif method == "constant":
        df[column] = df[column].fillna(value)
    elif method == "ffill":
        df[column] = df[column].fillna(method="ffill")
    elif method == "bfill":
        df[column] = df[column].fillna(method="bfill")
    else:
        raise ValueError(f"Unsupported fill method {method}")
    return df


def drop_columns_with_null_threshold(df, threshold):
    null_ratio = df.isnull().mean()
    cols_to_drop = null_ratio[null_ratio > threshold].index
    return df.drop(columns=cols_to_drop)


# =====================================================
# MASTER TRANSFORMATION ENGINE
# =====================================================

def transform_dataframe(df, config):
    working_df = df.copy()

    # ---------- Row operations ----------
    for op in config.get("row_operations", []):

        t = op["type"]

        if t == "filter":
            working_df = apply_filter(working_df, op)

        elif t == "top_n":
            working_df = top_n(working_df, op["column"], op["n"])

        elif t == "bottom_n":
            working_df = bottom_n(working_df, op["column"], op["n"])

        elif t == "random_sample":
            working_df = random_sample(working_df, op["n"])

        elif t == "drop_nulls":
            working_df = drop_null_rows(working_df)

        elif t == "row_range":
            working_df = row_range(
                working_df,
                op["start"],
                op["end"]
            )

        elif t == "remove_duplicates":
            working_df = remove_duplicates(working_df)

        else:
            raise ValueError(f"Unknown row operation {t}")

    # ---------- Column operations ----------
    for op in config.get("column_operations", []):

        t = op["type"]

        if t == "select":
            working_df = select_columns(working_df, op["columns"])

        elif t == "drop":
            working_df = drop_columns(working_df, op["columns"])

        elif t == "rename":
            working_df = rename_columns(working_df, op["mapping"])

        elif t == "reorder":
            working_df = reorder_columns(working_df, op["columns"])

        elif t == "fill_null":
            working_df = fill_null(
                working_df,
                op["column"],
                op["method"],
                op.get("value")
            )

        elif t == "drop_null_threshold":
            working_df = drop_columns_with_null_threshold(
                working_df,
                op["threshold"]
            )

        else:
            raise ValueError(f"Unknown column operation {t}")

    return working_df
