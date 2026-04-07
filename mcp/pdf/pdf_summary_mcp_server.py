import os
import sqlite3
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from mcp.server.fastmcp import FastMCP

DB_PATH = os.environ.get("BPJS_SQLITE_DB", "")
OUTPUT_DIR = os.environ.get("BPJS_PDF_OUTPUT_DIR", "./output/pdf")
LOG_FILE = os.path.join(os.path.dirname(__file__), "mcp_pdf.log")

mcp = FastMCP("bpjs-pdf-summary")


def log(msg: str) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def draw_wrapped_text(c, text, x, y, max_width, line_height=14, font_name="Helvetica", font_size=10):
    c.setFont(font_name, font_size)
    words = str(text).split()
    line = ""
    current_y = y

    for word in words:
        test_line = f"{line} {word}".strip()
        if c.stringWidth(test_line, font_name, font_size) <= max_width:
            line = test_line
        else:
            c.drawString(x, current_y, line)
            current_y -= line_height
            line = word

    if line:
        c.drawString(x, current_y, line)
        current_y -= line_height

    return current_y


def section_title(c, title, x, y):
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, title)
    return y - 16


@mcp.tool()
def create_case_summary_pdf(case_id: str) -> str:
    """Create a PDF summary for one claim case based on current operational data."""
    log(f"Tool called: create_case_summary_pdf case_id={case_id}")
    ensure_output_dir()

    with get_conn() as conn:
        case_row = conn.execute(
            """
            SELECT case_id, participant_id, participant_name, region, provider_type,
                   facility_name, claim_type, diagnosis_group, claim_amount, status,
                   priority_level, anomaly_score, suspected_issue, owner_unit
            FROM claim_cases
            WHERE case_id = ?
            """,
            (case_id,),
        ).fetchone()

        review_row = conn.execute(
            """
            SELECT case_id, queue_status, assigned_reviewer, assigned_team,
                   sla_due_date, overdue_days, next_action, escalation_level
            FROM review_queue
            WHERE case_id = ?
            """,
            (case_id,),
        ).fetchone()

    if not case_row:
        return f"Kasus {case_id} tidak ditemukan."

    filename = f"case_summary_{case_id}.pdf"
    file_path = os.path.join(OUTPUT_DIR, filename)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    x = 2 * cm
    y = height - 2 * cm
    max_width = width - 4 * cm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, "Ringkasan Kasus Klaim")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Tanggal pembuatan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 24

    y = section_title(c, "Identitas Kasus", x, y)
    fields = [
        ("Case ID", case_row["case_id"]),
        ("Participant ID", case_row["participant_id"]),
        ("Nama Peserta", case_row["participant_name"]),
        ("Region", case_row["region"]),
        ("Jenis Provider", case_row["provider_type"]),
        ("Fasilitas", case_row["facility_name"]),
        ("Tipe Klaim", case_row["claim_type"]),
        ("Diagnosis Group", case_row["diagnosis_group"]),
        ("Nilai Klaim", f"Rp {case_row['claim_amount']:,}".replace(",", ".")),
        ("Status Klaim", case_row["status"]),
        ("Priority Level", case_row["priority_level"]),
        ("Anomaly Score", case_row["anomaly_score"]),
        ("Suspected Issue", case_row["suspected_issue"]),
        ("Owner Unit", case_row["owner_unit"]),
    ]

    for label, value in fields:
        y = draw_wrapped_text(c, f"{label}: {value}", x, y, max_width)

    y -= 6
    y = section_title(c, "Status Review", x, y)

    if review_row:
        review_fields = [
            ("Queue Status", review_row["queue_status"]),
            ("Assigned Reviewer", review_row["assigned_reviewer"]),
            ("Assigned Team", review_row["assigned_team"]),
            ("SLA Due Date", review_row["sla_due_date"]),
            ("Overdue Days", review_row["overdue_days"]),
            ("Next Action", review_row["next_action"]),
            ("Escalation Level", review_row["escalation_level"]),
        ]
        for label, value in review_fields:
            y = draw_wrapped_text(c, f"{label}: {value}", x, y, max_width)
    else:
        y = draw_wrapped_text(c, "Tidak ada data review queue untuk kasus ini.", x, y, max_width)

    y -= 6
    y = section_title(c, "Ringkasan Singkat", x, y)

    summary_lines = [
        f"Kasus {case_row['case_id']} berada pada status {case_row['status']} dengan nilai klaim Rp {case_row['claim_amount']:,}.".replace(",", "."),
        f"Kasus terkait peserta {case_row['participant_name']} di region {case_row['region']} dan fasilitas {case_row['facility_name']}.",
        f"Indikasi utama yang tercatat adalah: {case_row['suspected_issue']}.",
    ]
    if review_row:
        summary_lines.append(
            f"Kasus saat ini ditangani oleh {review_row['assigned_reviewer']} dengan next action: {review_row['next_action']}."
        )

    for line in summary_lines:
        y = draw_wrapped_text(c, f"- {line}", x, y, max_width)

    c.save()
    return (
        f"PDF berhasil dibuat.\n"
        f"Nama file: {filename}\n"
        f"Lokasi file: {file_path}"
    )


@mcp.tool()
def create_operational_summary_pdf() -> str:
    """Create a PDF operational summary for supervisors based on current claim review data."""
    log("Tool called: create_operational_summary_pdf")
    ensure_output_dir()

    with get_conn() as conn:
        status_rows = conn.execute(
            """
            SELECT status, COUNT(*) AS total_cases
            FROM claim_cases
            GROUP BY status
            ORDER BY total_cases DESC
            """
        ).fetchall()

        overdue_rows = conn.execute(
            """
            SELECT case_id, queue_status, assigned_reviewer, overdue_days, next_action
            FROM review_queue
            WHERE overdue_days > 3
            ORDER BY overdue_days DESC
            LIMIT 10
            """
        ).fetchall()

        reviewer_rows = conn.execute(
            """
            SELECT assigned_reviewer, COUNT(*) AS total_cases
            FROM review_queue
            GROUP BY assigned_reviewer
            ORDER BY total_cases DESC
            LIMIT 10
            """
        ).fetchall()

    filename = f"operational_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(OUTPUT_DIR, filename)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    x = 2 * cm
    y = height - 2 * cm
    max_width = width - 4 * cm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x, y, "Ringkasan Operasional Klaim")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Tanggal pembuatan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 24

    y = section_title(c, "Jumlah Kasus per Status", x, y)
    for row in status_rows:
        y = draw_wrapped_text(c, f"- {row['status']}: {row['total_cases']} kasus", x, y, max_width)

    y -= 6
    y = section_title(c, "Top Overdue Cases", x, y)
    for row in overdue_rows[:5]:
        line = (
            f"- {row['case_id']} | {row['queue_status']} | "
            f"{row['assigned_reviewer']} | overdue {row['overdue_days']} hari | "
            f"{row['next_action']}"
        )
        y = draw_wrapped_text(c, line, x, y, max_width)

    y -= 6
    y = section_title(c, "Reviewer Workload", x, y)
    for row in reviewer_rows[:5]:
        y = draw_wrapped_text(c, f"- {row['assigned_reviewer']}: {row['total_cases']} kasus", x, y, max_width)

    y -= 6
    y = section_title(c, "Catatan Ringkas", x, y)
    notes = [
        "Dokumen ini merangkum kondisi operasional klaim berdasarkan data SQLite yang tersedia saat ini.",
        "Gunakan ringkasan ini sebagai bahan supervisor untuk melihat backlog, overdue review, dan distribusi workload.",
        "Prioritaskan tindak lanjut pada kasus overdue tertinggi dan reviewer dengan beban kerja paling besar.",
    ]
    for note in notes:
        y = draw_wrapped_text(c, f"- {note}", x, y, max_width)

    c.save()
    return (
        f"PDF berhasil dibuat.\n"
        f"Nama file: {filename}\n"
        f"Lokasi file: {file_path}"
    )


if __name__ == "__main__":
    log("Starting PDF MCP server")
    mcp.run()