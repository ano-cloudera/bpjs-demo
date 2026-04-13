# BPJS Healthcare Claims AI Demo

> **AI-Powered Claims Management & Review System for BPJS Healthcare Operations**
> 
> Built with Cloudera AI/ML platform for internal stakeholder demonstrations

## 📋 Overview

This project demonstrates an AI-powered healthcare claims management system designed for BPJS (Badan Penyelenggara Jaminan Sosial) healthcare operations. It leverages **Cloudera AI** with **Model Context Protocol (MCP)** servers to enable natural language querying of operational data, automated PDF report generation, and intelligent claims review workflows.

### Key Features

- 🔍 **Natural Language to SQL**: Query claims data using everyday Indonesian language
- 📊 **Automated PDF Reports**: Generate professional claim summaries and operational briefs
- 🤖 **MCP Server Architecture**: Two specialized MCP servers (SQLite + PDF)
- 🛡️ **Read-Only Guardrails**: Safe demo environment with SELECT-only queries
- 📈 **Anomaly Detection**: Built-in risk scoring and priority classification
- 👥 **Reviewer Workload Management**: Track reviewer assignments and overdue cases

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              Cloudera AI / RAG Studio                │
│         (Natural Language Interface)                 │
└──────────────┬──────────────────────┬───────────────┘
               │                      │
               ▼                      ▼
    ┌──────────────────┐   ┌─────────────────────┐
    │  SQLite MCP      │   │  PDF MCP Server     │
    │  Server          │   │                     │
    │                  │   │                     │
    │ • Query claims   │   │ • Case summaries    │
    │ • Review queues  │   │ • Operational briefs│
    │ • Referrals      │   │ • Professional PDFs │
    │ • Admin flags    │   │   with BPJS branding│
    └────────┬─────────┘   └─────────┬───────────┘
             │                        │
             ▼                        ▼
    ┌──────────────────┐   ┌─────────────────────┐
    │  SQLite Database │   │  Output Directory   │
    │  (bpjs_mcp_demo  │   │  (output/pdf/)      │
    │   .sqlite)       │   │                     │
    │                  │   │                     │
    │ • claim_cases    │   │ • Case summary PDFs │
    │ • review_queue   │   │ • Operational       │
    │ • referral_cases │   │   summary PDFs      │
    │ • participant_   │   │                     │
    │   admin_flags    │   │                     │
    └──────────────────┘   └─────────────────────┘
```

## 📁 Project Structure

```
BPJS/
├── README.md                           # This documentation
├── requirements-mcp.txt                # Python dependencies for MCP servers
├── pull_main.sh                        # Safe git pull script for main branch
│
├── BPJS_MCP_SQL_Lite_Pack/            # Database package
│   ├── bpjs_mcp_demo.sqlite           # SQLite database with demo data
│   ├── 01_schema_and_sample_queries.sql  # Schema & sample queries
│   ├── claim_cases.csv                # Sample claim cases data
│   ├── participant_admin_flags.csv    # Sample admin flags data
│   └── INSTALL_GUIDE.txt              # Installation instructions
│
├── mcp/                               # MCP Server implementations
│   ├── sqlite/                        # SQLite Query MCP Server
│   │   ├── sqlite_mcp_server.py       # Main SQLite MCP server (13 tools)
│   │   └── start_bpjs_mcp.sh          # Startup script for SQLite MCP
│   │
│   └── pdf/                           # PDF Generation MCP Server
│       ├── pdf_summary_mcp_server.py  # PDF generation MCP server (2 tools)
│       └── start_bpjs_pdf_mcp.sh      # Startup script for PDF MCP
│
├── scripts/
│   └── test_sql.sh                    # Database testing script
│
├── output/
│   └── pdf/                           # Generated PDF reports
│
├── assets/
│   └── bpjs_logo.png                  # BPJS logo for PDF branding
│
├── knowledge-base/                    # Knowledge base for RAG
└── .venv-mcp/                         # Python virtual environment for MCP
```

## 🗄️ Database Schema

The SQLite database contains four main tables:

### 1. `claim_cases`
Core claim case information:
- `case_id`, `participant_id`, `participant_name`
- `region`, `provider_type`, `facility_name`
- `claim_type`, `diagnosis_group`, `claim_amount`
- `status`, `priority_level`, `anomaly_score`
- `suspected_issue`, `owner_unit`

**Valid Statuses**: `Pending Verifikasi`, `Dalam Review`, `Eskalasi`, `Selesai`, `Ditolak`

### 2. `review_queue`
Review workflow and task management:
- `case_id`, `queue_status`, `assigned_reviewer`, `assigned_team`
- `sla_due_date`, `overdue_days`, `next_action`, `escalation_level`

**Valid Queue Statuses**: `Open`, `In Progress`, `Waiting Clarification`, `Escalated`, `Closed`

### 3. `referral_cases`
Referral and clarification tracking:
- `referral_id`, `participant_id`, `referral_source`, `referral_target`
- `referral_reason`, `referral_status`, `clarification_needed`, `owner_unit`

**Valid Referral Statuses**: `Open`, `Waiting Clarification`, `Approved`, `Rejected`, `Completed`

### 4. `participant_admin_flags`
Administrative flags on participants:
- `flag_id`, `participant_id`, `participant_name`
- `flag_type`, `flag_status`, `related_case_id`, `owner_unit`

**Valid Flag Statuses**: `Open`, `Resolved`, `Pending`

## 🛠️ MCP Server Tools

### SQLite MCP Server (`mcp/sqlite/sqlite_mcp_server.py`)

Provides 13 tools for querying claims data:

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `health_check` | Verify MCP server is running | "Is the BPJS tool running?" |
| `get_claim_status_summary` | Count cases by status | "Show claim status summary" |
| `get_overdue_review_cases` | Cases overdue >3 days | "Show overdue cases" |
| `search_case_by_id` | Get case details by ID | "Details for KR-2026-014" |
| `get_claims_by_status` | Filter claims by status | "Show pending verifikasi claims" |
| `get_cases_by_reviewer` | Cases assigned to reviewer | "Cases handled by [reviewer name]" |
| `get_review_cases_by_status` | Review queue by status | "Show open review cases" |
| `get_overdue_cases_min_days` | Overdue by minimum days | "Cases overdue more than 7 days" |
| `get_top_priority_claims` | Top 5 active high-value claims | "Show top priority claims" |
| `get_referral_cases_by_status` | Referrals by status | "Waiting clarification referrals" |
| `get_referral_clarification_cases` | Referrals needing clarification | "Referrals needing clarification" |
| `get_participant_flags` | Admin flags by status | "Show open admin flags" |
| `get_cases_summary_by_region` | Regional summary | "Summary for [region name]" |
| `get_reviewer_workload_summary` | Reviewer workload overview | "Reviewer workload summary" |
| `get_high_risk_overdue_cases` | High risk + overdue cases | "High risk overdue cases" |

### PDF MCP Server (`mcp/pdf/pdf_summary_mcp_server.py`)

Provides 2 tools for PDF generation:

| Tool | Description | Output |
|------|-------------|--------|
| `create_case_summary_pdf` | Single case summary PDF | `case_summary_[case_id].pdf` |
| `create_operational_summary_pdf` | Operational brief for supervisors | `operational_summary_[timestamp].pdf` |

## 🚀 Installation & Setup

### Prerequisites

- Cloudera AI workspace (CDS) or Python 3.9+ environment
- Node.js (if using npx-based MCP server)
- Git for version control

### Option A: SQLite MCP Server (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd bpjs-demo
   ```

2. **Set up Python virtual environment**:
   ```bash
   python -m venv .venv-mcp
   source .venv-mcp/bin/activate  # On Windows: .venv-mcp\Scripts\activate
   pip install -r requirements-mcp.txt
   ```

3. **Configure environment variables**:
   ```bash
   export BPJS_SQLITE_DB="/path/to/BPJS_MCP_SQL_Lite_Pack/bpjs_mcp_demo.sqlite"
   export PYTHONUNBUFFERED=1
   ```

4. **Start the SQLite MCP server**:
   ```bash
   ./mcp/sqlite/start_bpjs_mcp.sh
   ```

5. **Register MCP server in Cloudera AI / RAG Studio Settings**:
   ```json
   {
     "mcpServers": {
       "bpjs-sqlite": {
         "command": "/home/cdsw/bpjs-demo/.venv-mcp/bin/python",
         "args": ["/home/cdsw/bpjs-demo/mcp/sqlite/sqlite_mcp_server.py"]
       }
     }
   }
   ```

### Option B: PDF MCP Server

1. **Set environment variables**:
   ```bash
   export BPJS_SQLITE_DB="/path/to/BPJS_MCP_SQL_Lite_Pack/bpjs_mcp_demo.sqlite"
   export BPJS_PDF_OUTPUT_DIR="/path/to/output/pdf"
   export BPJS_PDF_LOGO="/path/to/assets/bpjs_logo.png"
   export PYTHONUNBUFFERED=1
   ```

2. **Start the PDF MCP server**:
   ```bash
   ./mcp/pdf/start_bpjs_pdf_mcp.sh
   ```

3. **Register MCP server in Cloudera AI / RAG Studio Settings**:
   ```json
   {
     "mcpServers": {
       "bpjs-pdf": {
         "command": "/home/cdsw/bpjs-demo/.venv-mcp/bin/python",
         "args": ["/home/cdsw/bpjs-demo/mcp/pdf/pdf_summary_mcp_server.py"]
       }
     }
   }
   ```

### Option C: Python Sidecar Service (Alternative)

If MCP package is not available in your runtime:

1. Create a lightweight HTTP service using Flask/FastAPI
2. Expose read-only SELECT endpoints
3. Connect RAG Studio to the service via MCP or direct API calls

## 💡 Usage Examples

### Natural Language Queries

The MCP server translates natural language into SQL queries:

| User Query | Translates To |
|------------|---------------|
| "Tampilkan kasus pending verifikasi" | `claim_cases.status = 'Pending Verifikasi'` |
| "Kasus prioritas review tertinggi" | `priority_level IN ('High','Critical')` |
| "Kasus review yang overdue" | `review_queue.overdue_days > 0` |
| "Referral yang butuh klarifikasi" | `referral_cases.clarification_needed = 1` |
| "Flag administrasi peserta" | `participant_admin_flags` |

### Sample Complex Query

**User**: "Show me high priority overdue cases with claim amounts"

**SQL executed**:
```sql
SELECT c.case_id, c.participant_name, c.claim_amount, c.status, 
       c.anomaly_score, r.assigned_reviewer, r.overdue_days, r.next_action
FROM claim_cases c
JOIN review_queue r ON c.case_id = r.case_id
WHERE c.priority_level IN ('High','Critical')
  AND r.overdue_days > 7
ORDER BY c.claim_amount DESC
LIMIT 10;
```

### Generating PDF Reports

**User**: "Create a summary for case KR-2026-014"

**Result**: Generates `case_summary_KR-2026-014.pdf` in `output/pdf/` with:
- Case identity details
- Review status and reviewer assignment
- Summary of key findings
- Recommended next actions

**User**: "Create operational summary for supervisors"

**Result**: Generates `operational_summary_[timestamp].pdf` with:
- Cases by status breakdown
- Top overdue cases
- Reviewer workload distribution
- High risk highlights
- Supervisor action items

## 🔒 Security & Guardrails

The MCP servers implement strict security measures:

- ✅ **SELECT-only queries**: INSERT, UPDATE, DELETE, DROP, ALTER are rejected
- ✅ **Row limits**: Maximum 20 rows per query (configurable)
- ✅ **Input validation**: All parameters validated against allowed values
- ✅ **Fixed schema**: Table names are hardcoded, no dynamic table creation
- ✅ **Logging**: All tool calls logged to `mcp_sqlite.log` and `mcp_pdf.log`
- ✅ **Environment isolation**: Database path controlled via environment variables

## 🔄 Development Workflow

### Pulling Latest Changes

Use the provided safe pull script:
```bash
./pull_main.sh
```

This script:
- Verifies you're on the `main` branch
- Fetches from origin
- Checks for divergence before pulling
- Prevents accidental overwrites

### Testing the Database

Run the test script:
```bash
./scripts/test_sql.sh
```

This validates:
- Database connectivity
- Table structure
- Sample queries execution

### Adding New MCP Tools

1. Add tool function to the appropriate MCP server file
2. Decorate with `@mcp.tool()`
3. Add docstring (used as tool description by AI)
4. Implement input validation
5. Test with sample queries
6. Update this README

## 📊 Demo Scenarios

### Scenario 1: Claims Review Dashboard

**Audience**: Claims supervisors

**Flow**:
1. Ask for claim status summary
2. Query overdue cases
3. Check reviewer workload
4. Generate operational summary PDF

### Scenario 2: High-Risk Case Investigation

**Audience**: Review specialists

**Flow**:
1. Search for specific case by ID
2. Review case details and anomaly score
3. Check review queue status
4. Generate case summary PDF for escalation

### Scenario 3: Regional Performance Review

**Audience**: Regional managers

**Flow**:
1. Query cases by region
2. Get claim amount summaries
3. Check participant flags
4. Generate operational brief

## 🐛 Troubleshooting

### MCP Server Not Starting

- Verify `BPJS_SQLITE_DB` environment variable is set
- Check virtual environment is activated
- Ensure all dependencies are installed: `pip install -r requirements-mcp.txt`

### PDF Generation Fails

- Verify logo file exists at `assets/bpjs_logo.png`
- Check output directory permissions: `chmod 755 output/pdf`
- Review `mcp_pdf.log` for detailed errors

### Database Query Returns Empty

- Verify database file path is correct
- Check tables exist: `sqlite3 bpjs_mcp_demo.sqlite ".tables"`
- Validate input parameters match allowed values (see schema section)

## 📚 Additional Resources

- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [Cloudera AI Documentation](https://docs.cloudera.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [ReportLab PDF Generation](https://www.reportlab.com/docs/reportlab-userguide.pdf)

## 🤝 Contributing

For internal team contributions:
1. Create feature branch from `main`
2. Make changes and test thoroughly
3. Update documentation
4. Submit PR for review

## 📄 License

**Internal Use Only** - This project is for demonstration purposes within Cloudera internal stakeholder presentations.

---

**Built with ❤️ using Cloudera AI/ML Platform**

*For questions or support, contact the demo engineering team*
