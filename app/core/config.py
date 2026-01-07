import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
LLAMA_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", "/path/to/local/llama-2")
