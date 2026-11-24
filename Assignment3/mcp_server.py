"""
Model Context Protocol (MCP) Server for an AI Assistant
Standard: Model Context Protocol (v2024-11-05) | Transport: stdio (JSON-RPC 2.0)
Student Name: Pramodh | Student ID: B210195 | Section: C4

Provides AI Assistants with:
- Tools: query_database, calculate_financial_metrics, search_assistant_docs, system_health_check
- Resources: assistant://system_config, assistant://database_schema, assistant://audit_logs
- Prompts: financial_analysis_prompt, system_diagnostic_prompt
"""

import sys
import json
import os
import sqlite3
import platform
import psutil
import datetime
from typing import Dict, Any, List

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "enterprise-assistant-mcp"
SERVER_VERSION = "1.0.0"

# Setup internal assistant database
DB_PATH = os.path.join(os.path.dirname(__file__), "assistant_data.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        department TEXT NOT NULL,
        quarter TEXT NOT NULL,
        revenue REAL NOT NULL,
        expenses REAL NOT NULL,
        headcount INTEGER NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        description TEXT NOT NULL
    )
    """)
    # Seed sample data if empty
    cur.execute("SELECT COUNT(*) FROM metrics")
    if cur.fetchone()[0] == 0:
        data = [
            ("Cloud AI", "Q1-2026", 1450000.0, 820000.0, 42),
            ("Cloud AI", "Q2-2026", 1820000.0, 950000.0, 50),
            ("E-Commerce", "Q1-2026", 3200000.0, 2100000.0, 110),
            ("E-Commerce", "Q2-2026", 3900000.0, 2300000.0, 125),
            ("Cybersecurity", "Q1-2026", 890000.0, 450000.0, 28),
            ("Cybersecurity", "Q2-2026", 1120000.0, 510000.0, 32)
        ]
        cur.executemany("INSERT INTO metrics (department, quarter, revenue, expenses, headcount) VALUES (?, ?, ?, ?, ?)", data)
        cur.execute("INSERT INTO audit_log (timestamp, event_type, description) VALUES (?, ?, ?)",
                    (datetime.datetime.now().isoformat(), "SYSTEM_INIT", "Database initialized with baseline corporate metrics."))
        conn.commit()
    conn.close()

init_db()

# ==========================================
# TOOL DEFINITIONS & HANDLERS
# ==========================================
TOOLS = [
    {
        "name": "query_database",
        "description": "Executes read-only SQL SELECT queries against the enterprise assistant database.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL SELECT query to execute (e.g. 'SELECT * FROM metrics WHERE department = \'Cloud AI\'')"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "calculate_financial_metrics",
        "description": "Computes high-precision financial metrics such as CAGR, Net Margin, and ROI.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "metric_type": {
                    "type": "string",
                    "enum": ["net_margin", "roi", "cagr"],
                    "description": "Financial metric to compute"
                },
                "revenue": {"type": "number", "description": "Total revenue"},
                "expenses": {"type": "number", "description": "Total expenses"},
                "initial_value": {"type": "number", "description": "Initial investment / value (for CAGR)"},
                "final_value": {"type": "number", "description": "Final value (for CAGR)"},
                "years": {"type": "number", "description": "Number of periods in years (for CAGR)"}
            },
            "required": ["metric_type"]
        }
    },
    {
        "name": "search_assistant_docs",
        "description": "Searches internal technical and operational SOP documentation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword or topic"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "system_health_check",
        "description": "Returns current host server telemetry, memory, CPU load, and uptime status.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

def handle_query_database(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    query = params.get("query", "").strip()
    if not query.lower().startswith("select"):
        return [{"type": "text", "text": "Error: Only read-only SELECT queries are permitted for assistant safety."}]
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(query)
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchall()
        conn.close()
        results = [dict(zip(columns, r)) for r in rows]
        return [{"type": "text", "text": json.dumps({"row_count": len(results), "data": results}, indent=2)}]
    except Exception as e:
        conn.close()
        return [{"type": "text", "text": f"Database Execution Error: {str(e)}"}]

def handle_calculate_financial_metrics(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    m_type = params.get("metric_type")
    if m_type == "net_margin":
        rev = params.get("revenue", 0.0)
        exp = params.get("expenses", 0.0)
        if rev <= 0:
            return [{"type": "text", "text": "Error: Revenue must be strictly positive."}]
        net_profit = rev - exp
        margin_pct = (net_profit / rev) * 100.0
        return [{"type": "text", "text": json.dumps({
            "metric": "Net Profit Margin",
            "revenue": rev, "expenses": exp,
            "net_profit": round(net_profit, 2),
            "margin_percentage": f"{margin_pct:.2f}%"
        }, indent=2)}]
    elif m_type == "roi":
        gain = params.get("revenue", 0.0)
        cost = params.get("expenses", 0.0)
        if cost <= 0:
            return [{"type": "text", "text": "Error: Cost/expenses must be strictly positive."}]
        roi_pct = ((gain - cost) / cost) * 100.0
        return [{"type": "text", "text": json.dumps({
            "metric": "Return on Investment (ROI)",
            "gain": gain, "cost": cost,
            "roi_percentage": f"{roi_pct:.2f}%"
        }, indent=2)}]
    elif m_type == "cagr":
        v_init = params.get("initial_value", 0.0)
        v_final = params.get("final_value", 0.0)
        yrs = params.get("years", 1.0)
        if v_init <= 0 or yrs <= 0:
            return [{"type": "text", "text": "Error: Initial value and years must be positive."}]
        cagr_val = ((v_final / v_init) ** (1.0 / yrs) - 1.0) * 100.0
        return [{"type": "text", "text": json.dumps({
            "metric": "Compound Annual Growth Rate (CAGR)",
            "initial_value": v_init, "final_value": v_final, "years": yrs,
            "cagr_percentage": f"{cagr_val:.2f}%"
        }, indent=2)}]
    return [{"type": "text", "text": f"Unknown metric type '{m_type}'"}]

def handle_search_assistant_docs(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    q = params.get("query", "").lower()
    docs = [
        {"title": "Incident Escalation SOP", "content": "Severity 1 outages require notifying the on-call engineer within 10 minutes and updating the status board."},
        {"title": "Cloud AI Deployment Protocol", "content": "Models must pass regression testing with latency < 50ms and 99.9% availability before production canary rollout."},
        {"title": "Financial Audit Guidelines", "content": "Quarterly financial reconciliations occur on the 5th business day of each new quarter under ISO-27001 standards."}
    ]
    matched = [d for d in docs if q in d["title"].lower() or q in d["content"].lower()]
    return [{"type": "text", "text": json.dumps(matched or docs, indent=2)}]

def handle_system_health_check(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    health = {
        "status": "HEALTHY",
        "server_name": SERVER_NAME,
        "protocol_version": PROTOCOL_VERSION,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_usage_percent": psutil.cpu_percent(interval=None),
        "virtual_memory_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage(".").percent,
        "timestamp": datetime.datetime.now().isoformat()
    }
    return [{"type": "text", "text": json.dumps(health, indent=2)}]

# ==========================================
# RESOURCE DEFINITIONS & HANDLERS
# ==========================================
RESOURCES = [
    {
        "uri": "assistant://system_config",
        "name": "Assistant System Configuration",
        "description": "Static and dynamic operational configuration parameters for the AI assistant.",
        "mimeType": "application/json"
    },
    {
        "uri": "assistant://database_schema",
        "name": "Database Schema Definition",
        "description": "Live introspection of SQLite tables, columns, and data types.",
        "mimeType": "text/plain"
    },
    {
        "uri": "assistant://audit_logs",
        "name": "Assistant Audit Logs",
        "description": "Chronological stream of assistant actions and system modifications.",
        "mimeType": "application/json"
    }
]

def handle_read_resource(uri: str) -> Dict[str, Any]:
    if uri == "assistant://system_config":
        return {
            "contents": [{
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps({
                    "environment": "production",
                    "max_tokens": 4096,
                    "default_timeout_sec": 30,
                    "allowed_sql_statements": ["SELECT"],
                    "cache_ttl_seconds": 300
                }, indent=2)
            }]
        }
    elif uri == "assistant://database_schema":
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        schemas = "\n\n".join([r[0] for r in cur.fetchall() if r[0]])
        conn.close()
        return {
            "contents": [{
                "uri": uri,
                "mimeType": "text/plain",
                "text": schemas
            }]
        }
    elif uri == "assistant://audit_logs":
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, timestamp, event_type, description FROM audit_log ORDER BY id DESC LIMIT 10")
        rows = cur.fetchall()
        conn.close()
        logs = [{"id": r[0], "timestamp": r[1], "event": r[2], "description": r[3]} for r in rows]
        return {
            "contents": [{
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(logs, indent=2)
            }]
        }
    return {"contents": []}

# ==========================================
# PROMPT DEFINITIONS & HANDLERS
# ==========================================
PROMPTS = [
    {
        "name": "financial_analysis_prompt",
        "description": "Generates a comprehensive executive financial briefing for a specified department.",
        "arguments": [
            {
                "name": "department",
                "description": "Name of department (e.g. Cloud AI, E-Commerce)",
                "required": True
            }
        ]
    },
    {
        "name": "system_diagnostic_prompt",
        "description": "Generates an architectural health diagnostic report based on server telemetry.",
        "arguments": []
    }
]

def handle_get_prompt(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "financial_analysis_prompt":
        dept = arguments.get("department", "Cloud AI")
        return {
            "description": f"Executive Financial Briefing for {dept}",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Please conduct a detailed financial evaluation of the '{dept}' department using data retrieved from the assistant database. Analyze revenue growth, operating expenses, and profit margins. Formulate strategic recommendations for subsequent quarters."
                    }
                }
            ]
        }
    elif name == "system_diagnostic_prompt":
        return {
            "description": "Diagnostic Health Review",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": "Please inspect current server hardware metrics (CPU load, memory consumption, disk capacity) and identify any operational bottlenecks or reliability risks."
                    }
                }
            ]
        }
    return {"description": "Unknown prompt", "messages": []}

# ==========================================
# MAIN JSON-RPC 2.0 PROTOCOL LOOP (stdio)
# ==========================================
def send_response(response: Dict[str, Any]):
    line = json.dumps(response)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()

def run_server():
    # Log to stderr so stdout remains purely JSON-RPC messages
    sys.stderr.write(f"[{SERVER_NAME}] Server started on stdio. Protocol: {PROTOCOL_VERSION}\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as e:
            send_response({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error", "data": str(e)}})
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        # Handle notifications
        if req_id is None:
            if method == "notifications/initialized":
                sys.stderr.write(f"[{SERVER_NAME}] Client completed handshake.\n")
                sys.stderr.flush()
            continue

        # 1. Initialize Handshake
        if method == "initialize":
            send_response({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False},
                        "prompts": {"listChanged": False}
                    },
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION
                    }
                }
            })

        # 2. Tools
        elif method == "tools/list":
            send_response({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            # Log audit event
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("INSERT INTO audit_log (timestamp, event_type, description) VALUES (?, ?, ?)",
                        (datetime.datetime.now().isoformat(), "TOOL_CALL", f"Invoked tool '{tool_name}'"))
            conn.commit()
            conn.close()

            if tool_name == "query_database":
                content = handle_query_database(tool_args)
            elif tool_name == "calculate_financial_metrics":
                content = handle_calculate_financial_metrics(tool_args)
            elif tool_name == "search_assistant_docs":
                content = handle_search_assistant_docs(tool_args)
            elif tool_name == "system_health_check":
                content = handle_system_health_check(tool_args)
            else:
                send_response({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found."}})
                continue

            send_response({"jsonrpc": "2.0", "id": req_id, "result": {"content": content, "isError": False}})

        # 3. Resources
        elif method == "resources/list":
            send_response({"jsonrpc": "2.0", "id": req_id, "result": {"resources": RESOURCES}})

        elif method == "resources/read":
            uri = params.get("uri")
            res = handle_read_resource(uri)
            send_response({"jsonrpc": "2.0", "id": req_id, "result": res})

        # 4. Prompts
        elif method == "prompts/list":
            send_response({"jsonrpc": "2.0", "id": req_id, "result": {"prompts": PROMPTS}})

        elif method == "prompts/get":
            p_name = params.get("name")
            p_args = params.get("arguments", {})
            res = handle_get_prompt(p_name, p_args)
            send_response({"jsonrpc": "2.0", "id": req_id, "result": res})

        # 5. Ping
        elif method == "ping":
            send_response({"jsonrpc": "2.0", "id": req_id, "result": {}})

        else:
            send_response({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method '{method}' not found."}})

if __name__ == "__main__":
    run_server()
