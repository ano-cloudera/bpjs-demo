#!/usr/bin/env bash
set -euo pipefail

cd /home/cdsw/bpjs-demo

export BPJS_SQLITE_DB="/home/cdsw/bpjs-demo/BPJS_MCP_SQL_Lite_Pack/bpjs_mcp_demo.sqlite"
export PYTHONUNBUFFERED=1

exec /home/cdsw/bpjs-demo/.venv-mcp/bin/python /home/cdsw/bpjs-demo/mcp/sqlite/sqlite_mcp_server.py