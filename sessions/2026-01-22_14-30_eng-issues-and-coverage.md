# Session: Engineering Issues Investigation & Diego Coverage

**Date:** 2026-01-22
**Duration:** ~3 hours
**Project:** HOME (Multi-project)
**Focus:** Engineering team accountability analysis + Diego OOO coverage

---

## Summary

Major session with two main workstreams:
1. Deep investigation of Engineering team issues over 4 months
2. Covering for Diego while he was OOO

---

## Work Completed

### 1. Engineering Issues Report (4 Months)

**Scope:** September 2025 - January 2026

**Data Sources Searched:**
- Slack: 317 messages from 15 queries
- Linear PLA/KLA: 250 issues analyzed
- Soranzo conversations: 289 messages

**Key Findings:**

| Client | Open Issues | Oldest | Critical |
|--------|-------------|--------|----------|
| QuickBooks | 30 | 275 days (PLA-2350) | Backlog abandoned |
| Gong | 21 | 267 days (PLA-2367) | BLOCKED 8 months |
| Brevo | 11 | 217 days (PLA-2574) | ETA communication |
| Tropic | 6 | 258 days (PLA-2397) | Paused |

**Files Generated:**
- `Downloads/ENG_ISSUES_REPORT_4MONTHS.md` - Full report
- `Downloads/ENG_ISSUES_BY_CLIENT.json` - Consolidated data
- `Downloads/SLACK_ENG_ISSUES_RAW.json` - Raw Slack data
- `Downloads/LINEAR_ENG_ISSUES_DETAIL.json` - Linear issues

**Pattern Identified:**
Not Engineering incompetence - systemic process gaps:
- No SLA for blocked issues
- No backlog hygiene
- Poor ETA communication
- Lack of escalation process

### 2. Diego OOO Coverage

**Period:** 2026-01-21 to 2026-01-22

**Issues Handled:**

| Client | Issue | Resolution |
|--------|-------|------------|
| Brevo - Backdating | API limitation | Shivani asked Hugo about Option A |
| Brevo - Pro Account | No Corporate SSO | Ismael needs different approach |
| People.ai - Opportunity Type | Empty field breaks matching | Eduardo to populate, Gabriel monitoring |

### 3. Company Strategic Analysis

**Sam's Discovery:** CEO realized projects run without:
- Written commitments
- Documented deadlines
- Clear status tracking

**Key Quote (Deyton):** "You're probably not going to find any project more appropriate. They're all like this."

**Sam's Action Plan:**
1. Push for clarity on Mailchimp (Red status)
2. Work with Gayathri on documentation system

### 4. Gabrielle/Mailchimp Analysis

**Pattern Found:** ETAs slipping daily (01-20 → 01-21 → 01-22)

**Root Cause:** Scope too big for timeline, not performance issue

### 5. English Communication Support

Helped Thiago with:
- Shivani messages about Brevo
- Gabriel Taufer coordination on People.ai
- Kat message about Alexandra/SOW
- LinkedIn comment for Sam's post

---

## Knowledge Learned

### Diego's Direct Input on Clients

| Client | Diego's Assessment |
|--------|-------------------|
| People.ai | Resource contention, not Eng fault |
| Brevo Sandbox | QA issue, fix returned 2-3x |
| Tabs | No issues since he took over |
| Tropic | All running on time since handover |

### Company Culture Insight

Sam discovering operational reality:
- Projects have no written deadlines
- Status communicated via calls, not docs
- Nobody escalated risks to leadership

---

## Recommendations Generated

### For Thiago

1. Talk to Gabrielle 1:1 about Mailchimp real status
2. Message Gayathri offering TSA Routine Indicators as input
3. Create Mailchimp status table before asked
4. Don't take solo ownership of problems

### For Engineering Process

1. SLA for blocked issues (max 30 days before escalation)
2. Weekly backlog review
3. Dataset release process documentation
4. Assignee accountability tracking

---

## Files Referenced

| File | Purpose |
|------|---------|
| `Downloads/TSA_ROUTINE_INDICATORS_V4.xlsx` | Metrics framework |
| `Downloads/TSA_INDICATORS_TEAM_BRIEFING.md` | Team communication |
| `.claude/memory.md` | Global context |

---

## Next Steps

1. Monitor Brevo responses from Hugo
2. Check Eduardo/Gabriel progress on People.ai
3. Follow up on Sam's documentation initiative
4. Diego returns Friday - handover notes ready

---

## Session Metrics

| Metric | Value |
|--------|-------|
| Tools Used | Slack API, Linear API, Read, Write |
| Files Created | 5 |
| Messages Drafted | 8 |
| Strategic Decisions | 4 |

---

*Consolidated via SpineHUB protocol*
