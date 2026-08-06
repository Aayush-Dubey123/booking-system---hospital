import uvicorn
from core.apis.api import app

if __name__ == "__main__":
    uvicorn.run(
        "core.apis.api",
        host="0.0.0.0",
        port=8000,
        reload=True,
        server_header=False,
    )