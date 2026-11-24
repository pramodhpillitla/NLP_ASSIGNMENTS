# Build MCP Server for an AI Assistant
## Design, Implementation, and Protocol Verification of Model Context Protocol (MCP) Server
**Student Name:** Pramodh | **Student ID:** B210195 | **Section:** C4  
**Course:** Natural Language Processing | **Date:** November 24, 2026

---

## 1. Executive Summary & Problem Formulation
The **Model Context Protocol (MCP)**, open-sourced by Anthropic, addresses tool integration fragmentation by establishing an open, universal, and bidirectional standard connecting AI models (Clients) with external execution environments and data repositories (Servers).

---

## 2. MCP Architectural Specification
```
┌────────────────────────────────────────────────────────┐
│               Host Application (MCP Client)            │
│          (Claude Desktop / Antigravity / IDE)          │
└───────────────────────────┬────────────────────────────┘
                            │
               JSON-RPC 2.0 │ over Standard I/O (stdio)
                            │
┌───────────────────────────▼────────────────────────────┐
│                    MCP Server Process                  │
│                (enterprise-assistant-mcp)              │
│                                                        │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────┐ │
│  │      TOOLS      │ │    RESOURCES    │ │  PROMPTS  │ │
│  │ - query_db      │ │ - system_config │ │ - finance │ │
│  │ - calc_metrics  │ │ - db_schema     │ │ - diag    │ │
│  │ - search_docs   │ │ - audit_logs    │ │           │ │
│  │ - health_check  │ │                 │ │           │ │
│  └────────┬────────┘ └────────┬────────┘ └───────────┘ │
└───────────┼───────────────────┼────────────────────────┘
            ▼                   ▼
┌────────────────────────────────────────────────────────┐
│         Relational SQLite Database & OS Host           │
└────────────────────────────────────────────────────────┘
```

---

## 3. Test Verification Suite Results
| Test ID | Method Tested | Target Identifier | Expected Payload | Verification Status |
|---|---|---|---|---|
| TC-01 | initialize | enterprise-assistant-mcp | protocolVersion: 2024-11-05 | PASSED |
| TC-02 | tools/list | All Tools | 4 tools registered with JSON Schema | PASSED |
| TC-03 | tools/call | query_database | Returned 2 rows for Cloud AI metrics | PASSED |
| TC-04 | tools/call | calculate_financial_metrics | Computed CAGR = 25.52% | PASSED |
| TC-05 | tools/call | system_health_check | Status: HEALTHY, CPU < 15% | PASSED |
| TC-06 | resources/list | All Resources | 3 resources registered with URIs | PASSED |
| TC-07 | resources/read | assistant://system_config | Returned JSON configuration payload | PASSED |
| TC-08 | prompts/list | All Prompts | 2 parameterized templates | PASSED |
| TC-09 | prompts/get | financial_analysis_prompt | Returned templated user message | PASSED |

---

## 4. Conclusion
Assignment 3 successfully demonstrated an enterprise-grade Model Context Protocol (MCP) server, verified via an automated test client with 100% protocol compliance.
