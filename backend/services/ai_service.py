import json
from openai import OpenAI
from core.config import OPENAI_API_KEY, MODEL_NAME

client = OpenAI(api_key=OPENAI_API_KEY)


# ============================================================
# DATASET OVERVIEW INSIGHTS
# ============================================================

def build_ai_context(df):
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "nulls": df.isnull().sum().to_dict(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "numeric_summary": df.describe().to_dict(),
        "sample_rows": df.head(5).to_dict(orient="records")
    }


def build_overview_prompt(context):
    return f"""
You are a senior data analyst.

Dataset overview:
{json.dumps(context, indent=2)}

Generate 5–7 crisp insights about:
• data quality
• distributions
• anomalies
• relationships
• next analysis steps

Use bullet points.
Be concise.
"""


def generate_insights(context):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": build_overview_prompt(context)}],
        temperature=0.3
    )
    return response.choices[0].message.content


# ============================================================
# NLP → STRUCTURED QUERY GENERATION
# ============================================================

def build_query_prompt(columns):
    return f"""
Convert natural language into structured JSON queries for pandas.

Schema:

{{
  "filters": [
    {{ "column": "name", "operator": "== | > | < | >= | <=", "value": value }}
  ],
  "groupby": "column",
  "aggregation": "mean | sum | count | min | max | median",
  "column": "target_column",
  "multiply": number (optional)
}}

Rules:
- filters optional
- groupby optional
- multiply optional
- aggregation required
- column required except for count
- Use ONLY these columns:
{columns}

If ambiguous return:

{{ "clarification_needed": true, "question": "ask user" }}

Return only JSON.
"""


def generate_query(question, columns):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": build_query_prompt(columns)},
            {"role": "user", "content": question}
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "clarification_needed": True,
            "question": "I could not interpret the question. Please rephrase."
        }


# ============================================================
# NEW — CHART INSIGHT GENERATION
# ============================================================


def build_chart_prompt(chart_context):
    return f"""
You are a senior data analyst.

Chart information:
{json.dumps(chart_context, indent=2)}

Generate 4–6 concise insights about:
• trends
• comparisons
• anomalies
• practical takeaways

Use bullet points.
Avoid generic statements.
"""


def generate_chart_insights(chart_context):
    prompt = build_chart_prompt(chart_context)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content

