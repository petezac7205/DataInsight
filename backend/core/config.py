import os
from typing import Final

# OpenAI API Configuration
OPENAI_API_KEY: Final[str | None] = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable not set. "
        "Please set it in your .env file or environment."
    )

# Model Configuration
MODEL_NAME: Final[str] = "gpt-4o-mini"  # Cost-effective choice

# Model Parameters
MODEL_CONFIG: Final[dict] = {
    "temperature": 0.7,      # Creativity level (0-1)
    "max_tokens": 2000,      # Response length limit
}