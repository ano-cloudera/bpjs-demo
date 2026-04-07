import json
import os
import sqlite3
from datetime import datetime

from mcp.server.fastmcp import FastMCP

DB_PATH = os.environ.get(
    "BPJS_SQLITE_DB",
    "/home/cdsw/bpjs-demo/BPJS_MCP_SQL_Lite_Pack/bpjs_mcp_demo.sqlite",
)

LOG_FILE = "/home/cdsw/bpjs-demo/mcp/sqlite/mcp_sqlite.log"

mcp = FastMCP("bpjs-sqlite")


def log(msg: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")


def get_conn():
    log(f"Opening DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_text(rows):
    if not rows:
        return "Tidak ada data."
    data = [dict(r) for r in rows]
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def health_check() -> str:
    """Check whether the BPJS SQLite MCP tool is running."""
    log("Tool called: health_check")
    return "BPJS SQLite MCP tool is running."


@mcp.tool()
def get_claim_status_summary() -> str:
    """Get current jumlah kasus per status."""
    log("Tool called: get_claim_status_summary")
    sql = """
    SELECT status, COUNT(*) AS total
    FROM claim_cases
    GROUP BY status
    ORDER BY total DESC
    """
    with get_conn() as conn:
        rows = conn.execute(sql).fetchall()
    return rows_to_text(rows)


@mcp.tool()
def get_overdue_review_cases() -> str:
    """Get review cases overdue lebih dari 3 hari."""
    log("Tool called: get_overdue_review_cases")
    sql = """
    SELECT case_id, queue_status, assigned_reviewer, overdue_days, next_action
    FROM review_queue
    WHERE overdue_days > 3
    ORDER BY overdue_days DESC
    LIMIT 10
    """
    with get_conn() as conn:
        rows = conn.execute(sql).fetchall()
    return rows_to_text(rows)


@mcp.tool()
def get_top_priority_claims() -> str:
    """Get top 5 active priority claims with highest claim amount."""
    log("Tool called: get_top_priority_claims")
    sql = """
    SELECT case_id, participant_name, claim_amount, status, priority_level, anomaly_score
    FROM claim_cases
    WHERE status IN ('Pending Verifikasi', 'Dalam Review', 'Eskalasi')
    ORDER BY claim_amount DESC
    LIMIT 5
    """
    with get_conn() as conn:
        rows = conn.execute(sql).fetchall()
    return rows_to_text(rows)


@mcp.tool()
def get_referral_clarification_cases() -> str:
    """Get referral cases that still need clarification."""
    log("Tool called: get_referral_clarification_cases")
    sql = """
    SELECT referral_id, participant_id, referral_target, referral_status, owner_unit
    FROM referral_cases
    WHERE clarification_needed = 1
    ORDER BY referral_date DESC
    LIMIT 10
    """
    with get_conn() as conn:
        rows = conn.execute(sql).fetchall()
    return rows_to_text(rows)


if __name__ == "__main__":
    log("Starting MCP server")
    mcp.run()