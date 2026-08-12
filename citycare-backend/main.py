import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root at backend entrypoint
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import uvicorn
# pyrefly: ignore [missing-import]
from core.apis.api import app

if __name__ == "__main__":
    uvicorn.run(
        "core.apis.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        server_header=False,
    )
