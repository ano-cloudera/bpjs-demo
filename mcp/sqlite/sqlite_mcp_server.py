import json
import os
import sqlite3
from typing import Any

from mcp.server.fastmcp import FastMCP

DB_PATH = os.environ.get(
    "BPJS_SQLITE_DB",
    "/home/cdsw/bpjs-demo/BPJS_MCP_SQL_Lite_Pack/bpjs_mcp_demo.sqlite",
)

mcp = FastMCP("bpjs-sqlite")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_json(rows: list[sqlite3.Row]) -> str:
    return json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2)


def is_safe_select(query: str) -> bool:
    q = query.strip().lower()
    blocked = ["insert ", "update ", "delete ", "drop ", "alter ", "create ", "attach ", "pragma ", "replace "]
    return q.startswith("select ") and not any(token in q for token in blocked)


@mcp.tool()
def list_tables() -> str:
    """List available SQLite tables for the BPJS demo operational database."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    return rows_to_json(rows)


@mcp.tool()
def run_readonly_sql(query: str, limit: int = 20) -> str:
    """Run a read-only SELECT query against the BPJS demo SQLite database."""
    if not is_safe_select(query):
        return json.dumps(
            {
                "error": "Only read-only SELECT queries are allowed."
            },
            ensure_ascii=False,
            indent=2,
        )

    q = query.strip().rstrip(";")
    q = f"SELECT * FROM ({q}) LIMIT {int(limit)}"

    with get_conn() as conn:
        rows = conn.execute(q).fetchall()
    return rows_to_json(rows)


@mcp.tool()
def claim_status_summary() -> str:
    """Summarize claim cases by status."""
    sql = """
    SELECT status, COUNT(*) AS total
    FROM claim_cases
    GROUP BY status
    ORDER BY total DESC
    """
    with get_conn() as conn:
        rows = conn.execute(sql).fetchall()
    return rows_to_json(rows)


@mcp.tool()
def overdue_review_cases(min_overdue_days: int = 3, limit: int = 10) -> str:
    """Return review queue items overdue more than the given number of days."""
    sql = """
    SELECT case_id, queue_status, assigned_reviewer, overdue_days, next_action
    FROM review_queue
    WHERE overdue_days > ?
    ORDER BY overdue_days DESC
    LIMIT ?
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (min_overdue_days, limit)).fetchall()
    return rows_to_json(rows)


@mcp.tool()
def top_priority_claims(limit: int = 5) -> str:
    """Return the highest-value active priority claims."""
    sql = """
    SELECT case_id, participant_name, claim_amount, status, priority_level, anomaly_score
    FROM claim_cases
    WHERE status IN ('Pending Verifikasi', 'Dalam Review', 'Eskalasi')
    ORDER BY claim_amount DESC
    LIMIT ?
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (limit,)).fetchall()
    return rows_to_json(rows)


@mcp.tool()
def referral_clarification_cases(limit: int = 10) -> str:
    """Return referral cases that still need clarification."""
    sql = """
    SELECT referral_id, participant_id, referral_target, referral_status, owner_unit
    FROM referral_cases
    WHERE clarification_needed = 1
    ORDER BY referral_date DESC
    LIMIT ?
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (limit,)).fetchall()
    return rows_to_json(rows)


if __name__ == "__main__":
    mcp.run()