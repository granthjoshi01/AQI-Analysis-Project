# Incident Postmortem (Jan 29–31, 2026): Google Sheets & Looker Studio Data Loss

## Summary
On January 31, the AQI monitoring dashboard temporarily displayed no data.
The underlying Google Sheet contained only headers, and Looker Studio
reported a dataset configuration error.

The issue was detected during a routine manual check and resolved by
forcing a pipeline run.

---

## Impact
- Google Sheet temporarily showed zero rows
- Looker Studio dashboards became disconnected
- No data was lost in the authoritative CSV store

---

## Root Cause
The pipeline uses macOS `launchd` (LaunchAgent) for scheduling.
LaunchAgents do not run when the laptop is asleep or the lid is closed.

During this period:
1. The pipeline ran with no newly fetched data
2. The Google Sheets writer performed a full refresh
3. The sheet was cleared and rewritten with headers only
4. Looker Studio cached the empty dataset and invalidated the connection

---

## Detection
The issue was detected manually when reviewing the live dashboard.

---

## Resolution
- The pipeline was manually executed
- The Google Sheet was repopulated from the local CSV (source of truth)
- Looker Studio was reconnected to refresh cached schema

---

## Preventive Actions
- Added guards to prevent overwriting Google Sheets with empty datasets
- Ensured Google Sheets updates occur only when valid data exists
- Reinforced CSV as the authoritative datastore
- Documented scheduler limitations for local execution

---

## Lessons Learned
- External systems (Sheets, BI tools) must be treated as best-effort sinks
- Full refresh strategies require explicit safety checks
- Local schedulers are not equivalent to always-on servers
- Designing for failure is as important as designing for success
