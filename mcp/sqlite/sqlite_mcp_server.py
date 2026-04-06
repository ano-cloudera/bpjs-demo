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


def rows_to_json(rows):
    return json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2)


def is_safe_select(query: str) -> bool:
    q = query.strip().lower()
    blocked = [
        "insert ",
        "update ",
        "delete ",
        "drop ",
        "alter ",
        "create ",
        "attach ",
        "pragma ",
        "replace ",
    ]
    return q.startswith("select ") and not any(token in q for token in blocked)


@mcp.tool()
def list_tables() -> str:
    log("Tool called: list_tables")
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    return rows_to_json(rows)


@mcp.tool()
def claim_status_summary() -> str:
    log("Tool called: claim_status_summary")
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
    log(f"Tool called: overdue_review_cases min_overdue_days={min_overdue_days} limit={limit}")
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
    log(f"Tool called: top_priority_claims limit={limit}")
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
    log(f"Tool called: referral_clarification_cases limit={limit}")
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


@mcp.tool()
def run_readonly_sql(query: str, limit: int = 20) -> str:
    log(f"Tool called: run_readonly_sql query={query} limit={limit}")
    if not is_safe_select(query):
        return json.dumps(
            {"error": "Only read-only SELECT queries are allowed."},
            ensure_ascii=False,
            indent=2,
        )

    q = query.strip().rstrip(";")
    wrapped = f"SELECT * FROM ({q}) LIMIT {int(limit)}"

    with get_conn() as conn:
        rows = conn.execute(wrapped).fetchall()
    return rows_to_json(rows)


if __name__ == "__main__":
    log("Starting MCP server")
    mcp.run()