import os
from dotenv import load_dotenv
from pathlib import Path

# Resolve project root (DATAINSIGHT/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load .env explicitly from project root
load_dotenv(PROJECT_ROOT / ".env")

GROK_API_KEY = os.getenv("GROK_API_KEY") or os.getenv("GROQ_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
