import json
from openai import OpenAI
from core.config import OPENAI_API_KEY, MODEL_NAME

client = OpenAI(api_key=OPENAI_API_KEY)


# -----------------------------
# OVERVIEW INSIGHTS (existing)
# -----------------------------

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
    prompt = build_overview_prompt(context)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content


# --------------------------------
# STRUCTURED QUERY GENERATION
# --------------------------------

def build_query_prompt(columns):
    return f"""
You convert natural language questions into structured JSON queries
for a pandas dataframe.

You MUST follow this schema exactly:

{{
  "filters": [
    {{
      "column": "column_name",
      "operator": "== | > | < | >= | <=",
      "value": "value"
    }}
  ],
  "groupby": "column_name",
  "aggregation": "mean | sum | count | min | max | median",
  "column": "column_name_for_aggregation",
  "multiply": number (optional)
}}

Rules:
- filters is optional
- groupby is optional
- multiply is optional
- aggregation is required
- column is required except when aggregation is "count"
- Use exact column names from this list:
{columns}

If the question is ambiguous, return:

{{
  "clarification_needed": true,
  "question": "Ask user for clarification"
}}

Return ONLY valid JSON.
No explanations.
"""


def generate_query(question, columns):
    system_prompt = build_query_prompt(columns)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
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
