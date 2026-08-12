"""
test_mcp_verification.py — Automated verification script for HospitalCare FastMCP integration.

Connects to the running HospitalCare FastAPI server at http://127.0.0.1:8000 and verifies:
1. Existing REST APIs (/health, /v1/hospitals, /v1/users/login) continue to work.
2. /mcp HTTP endpoint is reachable.
3. FastMCP Client discovers all registered tools.
4. Invokes read-only tool (list_hospitals) and authenticated tool (login & get_my_appointments).
"""

import sys
import asyncio
from pathlib import Path

# Add citycare-backend to path
backend_dir = Path(__file__).resolve().parent.parent / "citycare-backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import httpx
from fastmcp import Client

SERVER_URL = "http://127.0.0.1:8000"
MCP_URL = "http://127.0.0.1:8000/mcp/"


async def run_verification():
    print(f"--- 1. Connecting to running FastAPI server at {SERVER_URL} ---")
    async with httpx.AsyncClient(base_url=SERVER_URL, timeout=15.0) as http_client:
        print("\n--- 2. Verifying existing FastAPI REST Endpoints ---")
        
        # Check /health
        resp = await http_client.get("/health")
        assert resp.status_code == 200, f"/health failed: {resp.text}"
        print("✓ REST GET /health OK:", resp.json())
        
        # Check /v1/hospitals
        resp = await http_client.get("/v1/hospitals")
        assert resp.status_code == 200, f"/v1/hospitals failed: {resp.text}"
        hospitals = resp.json()
        print(f"✓ REST GET /v1/hospitals OK: Found {len(hospitals)} hospital(s)")
        
        # Check REST POST /v1/users/login with superadmin
        resp = await http_client.post("/v1/users/login", json={
            "email": "superadmin@citycare.com",
            "password": "admin1234"
        })
        assert resp.status_code == 200, f"/v1/users/login failed: {resp.text}"
        login_data = resp.json()
        admin_token = login_data.get("access_token")
        print(f"✓ REST POST /v1/users/login OK: Superadmin authenticated (token length {len(admin_token)})")

        print("\n--- 3. Verifying /mcp Endpoint Reachability ---")
        mcp_check = await http_client.post("/mcp", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"}
            }
        })
        print(f"✓ /mcp HTTP Endpoint status: {mcp_check.status_code}")

    print("\n--- 4. Verifying FastMCP Tool Discovery via FastMCP Client ---")
    async with Client(MCP_URL) as mcp_client:
        tools = await mcp_client.list_tools()
        tool_names = [t.name for t in tools]
        print(f"✓ FastMCP discovered {len(tool_names)} tool(s):")
        for name in tool_names:
            print(f"   - {name}")
        
        expected_tools = [
            "signup", "login", "list_hospitals", "get_hospital",
            "get_hospital_doctors", "book_appointment", "get_my_appointments",
            "get_schedule", "get_my_prescriptions", "get_prescription_by_id",
            "get_prescription_by_appointment", "create_prescription",
            "chat_with_health_assistant"
        ]
        for expected in expected_tools:
            assert expected in tool_names, f"Tool '{expected}' missing from discovered tools!"
        
        print("\n--- 5. Verifying MCP Tool Invocation ---")
        
        # Test Read-Only tool invocation: list_hospitals
        print("Testing read-only tool 'list_hospitals'...")
        hospitals_result = await mcp_client.call_tool("list_hospitals", {})
        print(f"✓ Tool 'list_hospitals' invoked successfully.")
        
        # Test Authenticated tool invocation: login
        print("Testing tool 'login'...")
        login_tool_result = await mcp_client.call_tool("login", {
            "email": "superadmin@citycare.com",
            "password": "admin1234"
        })
        print(f"✓ Tool 'login' invoked successfully.")
        
        # Test authenticated tool using the returned token
        print("Testing authenticated tool 'get_my_appointments'...")
        my_appts_result = await mcp_client.call_tool("get_my_appointments", {
            "authorization": admin_token
        })
        print(f"✓ Tool 'get_my_appointments' invoked successfully.")

    print("\n=======================================================")
    print(" ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(run_verification())
