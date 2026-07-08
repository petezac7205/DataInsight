# DataInsight

DataInsight is a web-based **Data Analysis & Transformation Developer Tool** that enables users to clean, transform, visualize, and analyze tabular datasets through an intuitive interface. The platform combines configurable data processing pipelines, interactive visualizations, AI-powered insights, and natural language querying to simplify exploratory data analysis while maintaining reproducible workflows.

---

## Features

### Data Upload
- Upload CSV datasets
- Automatic dataset preview
- Dataset statistics and metadata
- Column type detection

### Data Transformation
#### Row Operations
- Conditional filtering (single & multiple conditions)
- Row range selection
- Top N / Bottom N rows
- Random sampling
- Remove duplicate rows
- Drop null rows

#### Column Operations
- Select / Drop columns
- Rename columns
- Reorder columns
- Fill missing values
  - Mean
  - Median
  - Mode
  - Constant
  - Forward Fill
  - Backward Fill
  - Interpolation
- Drop columns exceeding null threshold
- Data type conversion
- Column normalization
- Derived column creation
- Column concatenation

### Data Analysis
- Dataset statistics
- Interactive Plotly visualizations
- AI-generated dataset insights

##Natural Language Query System
-DataInsight allows users to query uploaded datasets using plain English instead of writing code or SQL.

### Visualization
Supported charts:
- Bar Chart
- Line Chart
- Scatter Plot
- Histogram
- Box Plot
- Correlation Heatmap

### Export
- Export transformed dataset as CSV

---

# Project Structure

```
DataInsight
│
├── backend
│   ├── core
│   │   └── config.py
│   │
│   ├── services
│   │   ├── ai_service.py
│   │   ├── file_service.py
│   │   ├── plot_service.py
│   │   ├── query_service.py
│   │   ├── stats_service.py
│   │   └── transform_service.py
│   │
│   ├── main.py
│   ├── upload.py
│   ├── plotgen.py
│   └── requirements.txt
│
└── frontend
    ├── public
    ├── src
    ├── app.js
    ├── package.json
    └── package-lock.json
```

---

# Backend Overview

### `main.py`
Main FastAPI application that exposes all backend API endpoints and coordinates requests between frontend and backend services.

### `core/config.py`
Stores application configuration and environment variables.

### `services/file_service.py`
Handles dataset upload, loading, export, and file-related operations.

### `services/stats_service.py`
Generates dataset statistics including data types, missing values, and summary information.

### `services/transform_service.py`
Implements the transformation engine responsible for row-level and column-level operations, feature engineering, normalization, datatype conversion, and configurable transformation pipelines.

### `services/plot_service.py`
Generates interactive Plotly visualizations based on user-selected chart configurations.

### `services/query_service.py`
Executes structured dataframe queries generated from natural language prompts.

### `services/ai_service.py`
Interfaces with the LLM to generate dataset insights and convert natural language questions into structured query objects.

---

# Frontend

The frontend provides an interactive interface for:

- Uploading datasets
- Configuring transformations
- Visualizing data
- Querying datasets using natural language
- Viewing AI-generated insights
- Exporting processed datasets

---

# Workflow

```
Upload CSV
      │
      ▼
Dataset Preview
      │
      ▼
Data Transformation
      │
      ▼
Visualization / AI Insights / NLP Querying
      │
      ▼
Export Processed Dataset
```

---


## Authors

Developed as a full-stack data analytics platform integrating configurable data transformation, interactive visualization, and AI-assisted exploratory analysis.
