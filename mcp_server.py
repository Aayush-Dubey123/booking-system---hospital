"""
mcp_server.py — Standalone entrypoint for HospitalCare FastMCP server.

Can be run independently via `python mcp_server.py` or imported by FastAPI.
Reuses existing HospitalCare backend logic directly.
"""

import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent / "citycare-backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# pyrefly: ignore [missing-import]
from core.mcp import mcp

if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", "8001"))
    mcp.run(transport="http", port=port)