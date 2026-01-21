# Session: Intuit IC Balance Sheet Investigation

> **Date:** 2026-01-20 22:30
> **Duration:** ~2 hours
> **Project:** intuit-boom
> **Participants:** Thiago Rodrigues (TSA Lead), Alexandra Lacerda (TSA)

---

## Summary

Investigated "Consolidated Balance Sheet isn't balancing" error reported by David Ball (Intuit) in TCO and Keystone Construction environments. Applied all possible data fixes but discovered a system/backend bug preventing Consolidated View from syncing.

---

## What Was Done

### 1. Investigation
- Analyzed Consolidated Balance Sheet error
- Identified uneliminated IC balances ($4.8M, $7.1M, $72K)
- Found 4 IC mappings referencing deleted account
- Discovered mismatched Due From/Due To balances (~$2.2M gap)

### 2. Fixes Applied
- Created account 1083 "Due From Traction Control Outfitters (Parent)" in Shared COA
- Updated 4 IC mappings to use new account
- Created 5 Journal Entries totaling $14,085,718.11

### 3. Verification
- Confirmed JEs saved correctly in individual entities
- Confirmed individual Balance Sheets reflect changes
- Discovered Consolidated View does NOT sync changes

### 4. Documentation
- Created detailed dossier (339 lines) in Portuguese
- Translated dossier to English
- Created Linear ticket PLA-3201

---

## Files Created/Modified

| File | Action |
|------|--------|
| `intuit-boom/docs/DOSSIE_IC_BALANCE_SHEET_INVESTIGATION_2026-01-20.md` | Created |
| `Downloads/DOSSIE Consolidated Balance Sheet Out of Balance Investigation.txt` | Created |
| `Downloads/DOSSIER_Consolidated_Balance_Sheet_Investigation_EN.md` | Created |
| `SpineHUB/knowledge-base/QBO_IC_BALANCE_SHEET_TROUBLESHOOTING.md` | Created |

---

## Key Learnings

1. **IC Mapping Validation:** Always check for "(deleted)" accounts in IC mappings
2. **Due From/Due To Matching:** Must verify amounts match between entity pairs
3. **Shared COA:** Create accounts here for multi-entity IC use
4. **Consolidated View Bug:** System doesn't sync entity changes - requires Engineering

---

## Blockers Identified

| Blocker | Priority | Owner |
|---------|----------|-------|
| Consolidated View not syncing entity changes | P0 | Intuit Engineering |

---

## Next Steps

1. Wait for Engineering response on PLA-3201
2. Document as "known issue" for TSA team
3. Inform David Ball of status
4. Consider workaround if Engineering provides one

---

## Ticket Created

- **Linear:** PLA-3201 - IES Consolidated Balance Sheet not syncing entity changes

---

## Tags

`#intuit` `#qbo` `#ies` `#multi-entity` `#bug` `#investigation` `#escalation`

