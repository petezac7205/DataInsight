# AI Data Analyst

An AI-powered data analysis tool that lets you upload CSV files and analyze them using natural language queries.

## Features

- **Natural Language Queries** - Ask questions about your data in plain English
- **AI Overview** - Automatic dataset insights powered by GPT-4o-mini
- **Deep Profiling** - Correlation detection, outlier analysis, data quality assessment
- **Pandas Code Generation** - Get copy-paste ready Python code for every query
- **Clean UI** - Professional, minimal interface

## Tech Stack

### Backend
- FastAPI
- pandas
- numpy
- OpenAI API (GPT-4o-mini)

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- React Markdown

## Project Structure
```
project/
├── backend/
│   ├── main.py
│   ├── core/
│   │   └── config.py
│   └── services/
│       ├── ai_service.py
│       ├── query_service.py
│       └── analysis_service.py
└── frontend/
    ├── app/
    │   ├── page.tsx
    │   └── analysis/
    │       └── page.tsx
    ├── components/
    │   ├── OverviewTab.tsx
    │   ├── QueryInterface.tsx
    │   └── ProfileTab.tsx
    └── lib/
        └── api.ts
```

## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API Key

### Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env`:
```
OPENAI_API_KEY=your_api_key_here
```

Run backend:
```bash
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run frontend:
```bash
npm run dev
```

## Usage

1. Open `http://localhost:3000`
2. Upload a CSV file
3. Use the **Overview** tab for AI-generated insights
4. Use the **Query** tab to ask natural language questions
5. Use the **Profile** tab for deep statistical analysis

## Example Queries
```
How many records are there?
What is the average age by class?
Count survivors by gender
Total fare by passenger class
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload CSV file |
| GET | `/ai/overview-insights` | Get AI overview |
| POST | `/ai/query` | Natural language query |
| GET | `/ai/deep-profile` | Deep data profiling |
| GET | `/export/csv` | Export dataset |
| GET | `/health` | Health check |

## License
MIT