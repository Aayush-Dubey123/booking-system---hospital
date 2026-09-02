import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root or local backend folder
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

import uvicorn
# pyrefly: ignore [missing-import]
from core.apis.api import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    is_prod = bool(os.environ.get("RENDER") or os.environ.get("ENVIRONMENT") == "production")
    uvicorn.run(
        "core.apis.api:app",
        host="0.0.0.0",
        port=port,
        reload=not is_prod,
        server_header=False,
    )

