#!/usr/bin/env bash
set -euo pipefail

cd ~/bpjs-demo/BPJS_MCP_SQL_Lite_Pack

echo "== Tables =="
python query_helper.py --db bpjs_mcp_demo.sqlite --sql "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"

echo
echo "== Claim status summary =="
python query_helper.py --db bpjs_mcp_demo.sqlite --sql "SELECT status, COUNT(*) AS total FROM claim_cases GROUP BY status ORDER BY total DESC;"

echo
echo "== Overdue review cases =="
python query_helper.py --db bpjs_mcp_demo.sqlite --sql \"SELECT case_id, queue_status, assigned_reviewer, overdue_days, next_action FROM review_queue WHERE overdue_days > 3 ORDER BY overdue_days DESC LIMIT 10;\"