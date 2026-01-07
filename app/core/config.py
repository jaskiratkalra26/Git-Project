import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
LLAMA_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", "/path/to/local/llama-2")

# GitHub Configuration
GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")

# Ollama Configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "300.0"))


