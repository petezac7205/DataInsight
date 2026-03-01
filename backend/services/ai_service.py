import json
from openai import OpenAI, OpenAIError
from core.config import OPENAI_API_KEY, MODEL_NAME

client = OpenAI(api_key=OPENAI_API_KEY)


# ============================================================
# DATASET OVERVIEW INSIGHTS
# ============================================================

def build_ai_context(df):
    """Build context with safeguards for large datasets"""
    sample_size = min(5, len(df))
    
    # Only include columns with nulls
    null_counts = df.isnull().sum()
    nulls_dict = {col: int(count) for col, count in null_counts.items() if count > 0}
    
    # Limit numeric summary to top 10 numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns[:10]
    
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "nulls": nulls_dict if nulls_dict else "No missing values",
        "dtypes": df.dtypes.astype(str).to_dict(),
        "numeric_summary": df[numeric_cols].describe().to_dict() if len(numeric_cols) > 0 else {},
        "sample_rows": df.head(sample_size).to_dict(orient="records")
    }


def build_overview_prompt(context):
    return f"""
You are a senior data analyst.

Dataset overview:
{json.dumps(context, indent=2)}

Generate 5–7 crisp insights about:
- data quality (missing values, data types)
- distributions (numeric ranges, categorical balance)
- anomalies (outliers, unusual patterns)
- relationships (potential correlations)
- recommended analysis steps

Use bullet points.
Be concise and actionable.
Focus on what matters most for understanding this specific dataset.
"""


def generate_insights(context):
    """Generate AI insights with error handling"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": build_overview_prompt(context)}],
            temperature=0.3,
            timeout=30
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        print(f"OpenAI API Error in generate_insights: {e}")
        return "❌ Failed to generate insights. Please check your API key and try again."


# ============================================================
# NLP → STRUCTURED QUERY GENERATION
# ============================================================

def build_query_prompt(columns):
    return f"""
You are a data query parser. Convert natural language questions into structured JSON for pandas operations.

Available columns: {columns}

Output Schema:
{{
  "filters": [
    {{ "column": "col_name", "operator": "==|>|<|>=|<=|contains", "value": value }}
  ],
  "groupby": "column_name",
  "aggregation": "mean|sum|count|min|max|median",
  "column": "target_column",
  "multiply": number
}}

RULES:
1. "filters" is OPTIONAL - only include if the question specifies conditions
2. "groupby" is OPTIONAL - only include if the question asks "by [column]" or "for each [column]"
3. "aggregation" is REQUIRED - must be one of: mean, sum, count, min, max, median
4. "column" is REQUIRED for all aggregations EXCEPT "count"
5. "multiply" is OPTIONAL - only for unit conversions

PATTERN RECOGNITION:

Total/Overall Count:
- "How many [rows/records/items]?" → {{"aggregation": "count"}}
- "Total number of X" → {{"aggregation": "count"}}
- "Count all X" → {{"aggregation": "count"}}

Filtered Count:
- "How many X where Y" → {{"filters": [...], "aggregation": "count"}}
- "Count X with condition" → {{"filters": [...], "aggregation": "count"}}

Average/Mean:
- "Average X" → {{"aggregation": "mean", "column": "X"}}
- "Mean of X" → {{"aggregation": "mean", "column": "X"}}
- "What's the typical X" → {{"aggregation": "mean", "column": "X"}}

Sum/Total:
- "Total X" → {{"aggregation": "sum", "column": "X"}}
- "Sum of X" → {{"aggregation": "sum", "column": "X"}}

Min/Max:
- "Highest/Maximum/Largest X" → {{"aggregation": "max", "column": "X"}}
- "Lowest/Minimum/Smallest X" → {{"aggregation": "min", "column": "X"}}

Grouped Aggregation:
- "X by Y" → {{"groupby": "Y", "aggregation": "...", "column": "X"}}
- "X for each Y" → {{"groupby": "Y", "aggregation": "...", "column": "X"}}

Conditions:
- "greater than" / "more than" / "above" → operator: ">"
- "less than" / "below" / "under" → operator: "<"
- "equals" / "is" / "are" → operator: "=="
- "contains" / "includes" / "has" → operator: "contains"

GENERIC EXAMPLES (adapt to actual columns):

Q: "How many records are there?"
A: {{"aggregation": "count"}}

Q: "What is the average of column_A?"
A: {{"aggregation": "mean", "column": "column_A"}}

Q: "How many items where status equals active?"
A: {{"filters": [{{"column": "status", "operator": "==", "value": "active"}}], "aggregation": "count"}}

Q: "Total revenue by region"
A: {{"groupby": "region", "aggregation": "sum", "column": "revenue"}}

Q: "Average price for products over 100"
A: {{"filters": [{{"column": "price", "operator": ">", "value": 100}}], "aggregation": "mean", "column": "price"}}

Q: "Count users in each category"
A: {{"groupby": "category", "aggregation": "count"}}

Q: "Highest salary by department"
A: {{"groupby": "department", "aggregation": "max", "column": "salary"}}

COLUMN MATCHING:
- Use ONLY columns from the available list: {columns}
- Match columns flexibly (e.g., "price" can match "Price", "product_price", "unit_price")
- If a column name is ambiguous, pick the most likely match
- Be case-insensitive when matching

CLARIFICATION:
Only ask for clarification if:
- The question is genuinely ambiguous with multiple valid interpretations
- A required column clearly doesn't exist and there's no reasonable match
- The operation requested is impossible with the available data

Return: {{"clarification_needed": true, "question": "specific clarification question"}}

OUTPUT FORMAT:
Return ONLY valid JSON. No markdown, no code blocks, no explanations.
"""


def generate_query(question, columns):
    """Generate structured query from natural language"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": build_query_prompt(columns)},
                {"role": "user", "content": question}
            ],
            temperature=0,
            timeout=30
        )

        content = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        return json.loads(content)
        
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}\nContent: {content}")
        return {
            "clarification_needed": True,
            "question": "I could not interpret the question. Please rephrase."
        }
    except OpenAIError as e:
        print(f"OpenAI API Error in generate_query: {e}")
        return {
            "clarification_needed": True,
            "question": "API error occurred. Please try again."
        }


# ============================================================
# AI PROFILE INSIGHTS
# ============================================================

def build_profile_prompt(profile_data):
    return f"""
You are a senior data scientist analyzing dataset profiling results.

Here is automated profiling output:
{json.dumps(profile_data, indent=2)}

Generate 6–10 meaningful insights in plain language.

Focus on:
- Strong relationships between variables (correlations, patterns)
- Data quality issues (outliers, missing data, imbalanced categories)
- Distribution characteristics (skewness, dominant values)
- Potential modeling considerations
- Business implications of the patterns found

Guidelines:
- Explain what the numbers MEAN, don't just repeat them
- Prioritize actionable insights
- Use bullet points
- Be specific about which variables are involved
- Suggest next steps for analysis or data cleaning
"""


def generate_profile_insights(profile_data):
    """Generate narrative insights from profiling data"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": build_profile_prompt(profile_data)}],
            temperature=0.3,
            timeout=30
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        print(f"OpenAI API Error in generate_profile_insights: {e}")
        return "❌ Failed to generate profile insights. Please try again."