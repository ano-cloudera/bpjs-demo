#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

export BPJS_SQLITE_DB="${REPO_ROOT}/BPJS_MCP_SQL_Lite_Pack/bpjs_mcp_demo.sqlite"
export BPJS_PDF_OUTPUT_DIR="${REPO_ROOT}/output/pdf"
export PYTHONUNBUFFERED=1

mkdir -p "${REPO_ROOT}/output/pdf"

exec "${REPO_ROOT}/.venv-mcp/bin/python" "${REPO_ROOT}/mcp/pdf/pdf_summary_mcp_server.py"