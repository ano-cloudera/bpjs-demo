-- BPJS-lite MCP demo database
-- Open with sqlite3 bpjs_mcp_demo.sqlite

-- Example queries
SELECT status, COUNT(*) AS total
FROM claim_cases
GROUP BY status
ORDER BY total DESC;

SELECT case_id, participant_name, claim_amount, status, priority_level
FROM claim_cases
WHERE status IN ('Pending Verifikasi', 'Dalam Review', 'Eskalasi')
ORDER BY claim_amount DESC
LIMIT 5;

SELECT r.case_id, r.queue_status, r.assigned_reviewer, r.overdue_days, r.next_action
FROM review_queue r
WHERE r.overdue_days > 3
ORDER BY r.overdue_days DESC;

SELECT referral_status, COUNT(*) AS total
FROM referral_cases
GROUP BY referral_status
ORDER BY total DESC;

SELECT flag_type, COUNT(*) AS total
FROM participant_admin_flags
GROUP BY flag_type
ORDER BY total DESC;