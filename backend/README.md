backend/
│
├── main.py
│
├── core/
│   └── config.py
│
├── services/
│   ├── ai_service.py
│   ├── file_service.py
│   ├── stats_service.py
│   ├── query_service.py
│   ├── plot_service.py
│   └── __pycache__/
│
└── __pycache__/

DataInsight AI – Backend

Backend for DataInsight AI — an AI-powered data visualization and analysis platform.

This system converts:

• CSV files → structured data
• Natural language → pandas queries
• Dropdown charts → Plotly visualizations
• Dataset stats → AI insights

Built with FastAPI, Pandas, Plotly, OpenAI API

🧠 core/config.py

Stores:

• OpenAI API Key
• Model name

Used by ai_service.py

⚙️ services Overview
📂 file_service.py

Handles:

✔ CSV upload
✔ decoding
✔ cleaning nulls & infinities

📈 stats_service.py

Provides:

✔ dataset shape
✔ null counts
✔ column dtypes
✔ summary info

🧠 ai_service.py

Does:

✔ AI dataset insights
✔ natural language → structured JSON query

Example:

“How many survived below 20?”

→ converted into pandas-safe query JSON

🧮 query_service.py

Safely runs:

• filters
• groupby
• aggregations

on the dataframe.

No raw code execution (safe).

📊 plot_service.py

Creates interactive charts:

Chart	Input
Bar	x, y
Line	x, y
Scatter	x, y
Histogram	x
Box	x, y
Heatmap	numeric columns

Returns Plotly JSON.

🚀 API Endpoints (main.py)
Endpoint	Description
POST /upload	Upload CSV
GET /stats	Dataset overview
GET /column-stats	Column analytics
GET /ai/overview-insights	AI trends
POST /ai/query	NLP on CSV
POST /plot	Generate chart
--------------------------------------------------------------------
