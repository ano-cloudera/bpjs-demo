import argparse
import sqlite3
import json
import re
from typing import Any

FORBIDDEN = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|REPLACE|ATTACH|DETACH|PRAGMA)\b", re.I)

def main():
    parser = argparse.ArgumentParser(description="Read-only SQLite query helper for BPJS MCP demo")
    parser.add_argument("--db", required=True, help="Path to sqlite database")
    parser.add_argument("--sql", required=True, help="SELECT query only")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    sql = args.sql.strip().rstrip(";")
    if not sql.lower().startswith("select"):
        raise SystemExit("Only SELECT queries are allowed")
    if FORBIDDEN.search(sql):
        raise SystemExit("Forbidden SQL detected")
    sql = f"SELECT * FROM ({sql}) LIMIT {args.limit}"

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(sql).fetchall()]
    print(json.dumps(rows, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()