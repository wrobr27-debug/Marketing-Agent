import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    opencode_api_key: str = os.getenv("OPENCODE_API_KEY", "")
    opencode_api_base: str = os.getenv("OPENCODE_API_BASE", "https://opencode.ai/zen/v1")
    opencode_model: str = os.getenv("OPENCODE_MODEL", "north-mini-code-free")
    
    # Places API / Sourcing keys if user wants to add them in future
    google_places_api_key: str = os.getenv("GOOGLE_PLACES_API_KEY", "")

settings = Settings()
