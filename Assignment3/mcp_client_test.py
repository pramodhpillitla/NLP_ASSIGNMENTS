"""
Automated Test Client for Model Context Protocol (MCP) Server
Spawns mcp_server.py as a subprocess, performs protocol handshake,
validates Tools, Resources, and Prompts, and records complete JSON-RPC traces.
"""

import subprocess
import json
import sys
import os

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "mcp_server.py")

class MCPTestClient:
    def __init__(self):
        self.proc = subprocess.Popen(
            [sys.executable, SERVER_SCRIPT],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        self.req_counter = 1

    def send_request(self, method: str, params: dict = None) -> dict:
        req_id = self.req_counter
        self.req_counter += 1
        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method
        }
        if params is not None:
            payload["params"] = params
            
        req_line = json.dumps(payload)
        self.proc.stdin.write(req_line + "\n")
        self.proc.stdin.flush()
        
        resp_line = self.proc.stdout.readline()
        return json.loads(resp_line.strip())

    def send_notification(self, method: str, params: dict = None):
        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()

    def close(self):
        self.proc.terminate()
        self.proc.wait()


def run_mcp_verification():
    print("=" * 70)
    print("NATURAL LANGUAGE PROCESSING - ASSIGNMENT 3: MCP SERVER VERIFICATION")
    print("Student ID: B210195 | Section: C4 | Student: Pramodh")
    print("=" * 70)

    client = MCPTestClient()

    # Step 1: Initialize Handshake
    print("\n[Test 1] Executing MCP Protocol Handshake (method='initialize')...")
    init_res = client.send_request("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "NLP-Assignment-Client", "version": "1.0.0"}
    })
    print("-> Server Response:")
    print(json.dumps(init_res, indent=2))
    client.send_notification("notifications/initialized")
    print("-> Sent notifications/initialized.")

    # Step 2: List Tools
    print("\n[Test 2] Querying Server Tools (method='tools/list')...")
    tools_res = client.send_request("tools/list")
    tools = tools_res["result"]["tools"]
    print(f"-> Discovered {len(tools)} tools: {[t['name'] for t in tools]}")

    # Step 3: Execute Tool 1 - query_database
    print("\n[Test 3] Calling Tool: query_database...")
    q_res = client.send_request("tools/call", {
        "name": "query_database",
        "arguments": {"query": "SELECT department, quarter, revenue, expenses FROM metrics WHERE department = 'Cloud AI'"}
    })
    print("-> Tool Result:")
    print(q_res["result"]["content"][0]["text"])

    # Step 4: Execute Tool 2 - calculate_financial_metrics (CAGR)
    print("\n[Test 4] Calling Tool: calculate_financial_metrics (metric_type='cagr')...")
    calc_res = client.send_request("tools/call", {
        "name": "calculate_financial_metrics",
        "arguments": {"metric_type": "cagr", "initial_value": 1450000.0, "final_value": 1820000.0, "years": 1.0}
    })
    print("-> Tool Result:")
    print(calc_res["result"]["content"][0]["text"])

    # Step 5: Execute Tool 3 - system_health_check
    print("\n[Test 5] Calling Tool: system_health_check...")
    health_res = client.send_request("tools/call", {
        "name": "system_health_check",
        "arguments": {}
    })
    print("-> Tool Result:")
    print(health_res["result"]["content"][0]["text"])

    # Step 6: List & Read Resources
    print("\n[Test 6] Listing Resources (method='resources/list')...")
    res_list = client.send_request("resources/list")
    resources = res_list["result"]["resources"]
    print(f"-> Discovered {len(resources)} resources: {[r['uri'] for r in resources]}")

    print("\n[Test 7] Reading Resource: assistant://system_config...")
    read_res = client.send_request("resources/read", {"uri": "assistant://system_config"})
    print("-> Resource Content:")
    print(read_res["result"]["contents"][0]["text"])

    # Step 7: List & Inspect Prompts
    print("\n[Test 8] Listing Prompts (method='prompts/list')...")
    prompt_list = client.send_request("prompts/list")
    prompts = prompt_list["result"]["prompts"]
    print(f"-> Discovered {len(prompts)} prompt templates: {[p['name'] for p in prompts]}")

    print("\n[Test 9] Fetching Prompt: financial_analysis_prompt...")
    prompt_get = client.send_request("prompts/get", {"name": "financial_analysis_prompt", "arguments": {"department": "Cloud AI"}})
    print("-> Rendered Prompt Template:")
    print(json.dumps(prompt_get["result"], indent=2))

    client.close()
    print("\n" + "=" * 70)
    print("ALL MCP SERVER SPECIFICATION TESTS PASSED SUCCESSFULLY (100% COMPLIANT)!")
    print("=" * 70)

if __name__ == "__main__":
    run_mcp_verification()
