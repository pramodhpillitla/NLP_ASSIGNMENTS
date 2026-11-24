# Natural Language Processing (NLP) — Assignment Submission Package

**Student Name:** Pramodh  
**Student ID:** B210195  
**Class / Section:** C4  
**Date of Submission:** November 24, 2026  
**Folder Name:** `C4_B210195`  
**Zip Archive:** `C4_B210195.zip`  

---

## Submission Overview

This submission contains complete digital documents, full production-grade implementations, interactive Jupyter Notebooks, datasets, and benchmark verification suites for all three NLP assignments:

### 1. Assignment 1: Document Question and Answering using RAG
- **Path:** `Assignment1/`
- **Core Topic:** Retrieval-Augmented Generation (RAG) using dense embeddings, FAISS vector indexing, and context-grounded answer synthesis with citation attribution.
- **Key Deliverables:**
  - `Assignment1_Report_B210195.docx`: Formal Microsoft Word Technical Report.
  - `Assignment1_Report_B210195.pdf`: Vector PDF Document with architecture diagrams, formulas, and evaluation tables.
  - `Assignment1_Report.html`: Responsive HTML Document with print-to-PDF styles.
  - `Assignment1_Report.md`: Markdown Report.
  - `Assignment1_RAG_QA.ipynb`: Interactive Jupyter Notebook.
  - `rag_qa_system.py`: Complete Python RAG implementation.
  - `sample_knowledge_base.txt`: Curated domain specification document.
  - `README.md`: Quickstart & execution instructions.

---

### 2. Assignment 2: AI Agents for E-Commerce Application
- **Path:** `Assignment2/`
- **Core Topic:** Multi-Agent Cognitive System using the ReAct (Reasoning and Acting) paradigm, function calling, and deterministic SQLite tools for conversational commerce.
- **Key Deliverables:**
  - `Assignment2_Report_B210195.docx`: Formal Microsoft Word Technical Report.
  - `Assignment2_Report_B210195.pdf`: Vector PDF Document with ReAct traces and comparative evaluations.
  - `Assignment2_Report.html`: Responsive HTML Document with print-to-PDF styles.
  - `Assignment2_Report.md`: Markdown Report.
  - `Assignment2_Ecommerce_AI_Agents.ipynb`: Interactive Jupyter Notebook.
  - `ecommerce_agents.py`: Complete Multi-Agent Python implementation.
  - `catalog_database.db`: Relational SQLite database with products, orders, coupons, and policies.
  - `README.md`: Quickstart & execution instructions.

---

### 3. Assignment 3: Build MCP Server for an AI Assistant
- **Path:** `Assignment3/`
- **Core Topic:** Model Context Protocol (MCP) server adhering to protocol specification `v2024-11-05` communicating over standard I/O (`stdio`) via JSON-RPC 2.0.
- **Key Deliverables:**
  - `Assignment3_Report_B210195.docx`: Formal Microsoft Word Technical Report.
  - `Assignment3_Report_B210195.pdf`: Vector PDF Document with protocol specifications and lifecycle traces.
  - `Assignment3_Report.html`: Responsive HTML Document with print-to-PDF styles.
  - `Assignment3_Report.md`: Markdown Report.
  - `Assignment3_MCP_Server.ipynb`: Interactive Jupyter Notebook.
  - `mcp_server.py`: Complete Model Context Protocol Server (`stdio` JSON-RPC 2.0).
  - `mcp_client_test.py`: Automated verification client testing the complete protocol lifecycle.
  - `mcp_config.json`: Standard client configuration file for Claude Desktop, Antigravity, or Cursor.
  - `assistant_data.db`: Relational database backing the assistant tools and audit logs.
  - `README.md`: Quickstart & execution instructions.

---

## Verification & Execution Summary

All scripts and tests have been verified:
1. `Assignment1/rag_qa_system.py` executes with FAISS IndexFlatIP and provides 100% grounded citations.
2. `Assignment2/ecommerce_agents.py` completes an 8-turn customer journey with zero mathematical hallucinations.
3. `Assignment3/mcp_client_test.py` validates all 9 test cases covering initialization, tools, resources, and prompts with 100% protocol compliance.
