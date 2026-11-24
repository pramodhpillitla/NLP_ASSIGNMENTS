# NLP Assignment 3: Build MCP Server for an AI Assistant
**Student:** Pramodh | **ID:** B210195 | **Class:** C4

## Directory Contents
- `Assignment3_Report_B210195.docx`: Formal Microsoft Word Technical Report.
- `Assignment3_Report_B210195.pdf`: Formal PDF Document with protocol specifications, sequence diagrams, and benchmarks.
- `Assignment3_Report.html`: Responsive HTML Document with print-to-PDF styles.
- `Assignment3_Report.md`: Markdown Report.
- `Assignment3_MCP_Server.ipynb`: Interactive Jupyter Notebook.
- `mcp_server.py`: Complete Model Context Protocol Server (stdio JSON-RPC 2.0).
- `mcp_client_test.py`: Automated verification client testing the complete protocol lifecycle.
- `mcp_config.json`: Standard client configuration file for Claude Desktop / Antigravity.

## Execution Instructions
Run the automated MCP test client:
```bash
python mcp_client_test.py
```
Or run the server standalone over stdio:
```bash
python mcp_server.py
```
Or open the interactive Jupyter Notebook:
```bash
jupyter notebook Assignment3_MCP_Server.ipynb
```
