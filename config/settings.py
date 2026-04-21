import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("INDRA_MONGO_URI")
HF_API_KEY = os.getenv("HF_API_KEY")

DB_NAME = "indra_ai"