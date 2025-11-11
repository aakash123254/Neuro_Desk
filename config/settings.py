import os 
from pathlib import Path 
import google.generativeai as genai 
from dotenv import load_dotenv

# -----------------------------
# 1. Load environment variables
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent 
ENV_PATH = BASE_DIR / '.env' 

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

else:
    print(f"⚠️ No .env file found ar {ENV_PATH}. You can still set GEMINI_API_KEY manually.")
    

# -----------------------------
# 2. Paths and directories
# -----------------------------
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR  = DATA_DIR / "uploads"
CHUNKS_DIR = DATA_DIR / "chunks"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
OUTPUTS_DIR = DATA_DIR / "outputs"

# Create directories
for d in [DATA_DIR,UPLOADS_DIR, CHUNKS_DIR, EMBEDDINGS_DIR, OUTPUTS_DIR]:
    os.makedirs(d,exists_ok=True)
    

# -----------------------------
# 3. Gemini Configuration
# -----------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY","")
if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY not set in environment variables.")

# Default Gemini models
GEMINI_MODEL_TEXT = "gemini-1.5-flash" #FAst+Effiecient 
GEMINI_MODEL_PRO = "gemini_1.5-pro" #best for deep reasoning tasks 

def configure_gemini():
    """Initialize Gemini API using the API key."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found. Please add it to your .env file.")
    genai.configure(api_key=GEMINI_API_KEY)
    return True 

