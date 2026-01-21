# QBO IES - Intercompany Balance Sheet Troubleshooting Guide

> **Created:** 2026-01-20
> **Source:** Investigation for Intuit (David Ball) - TCO/Keystone environments
> **Authors:** Thiago Rodrigues (TSA Lead), Alexandra Lacerda (TSA)

---

## Overview

This document captures learnings from investigating a "Consolidated Balance Sheet isn't balancing" error in QuickBooks Online Intuit Enterprise Suite (IES) Multi-Entity environments.

---

## Common Causes of IC Imbalance

### 1. Deleted Accounts in IC Mappings

**Symptom:** IC mappings show "(deleted)" in account fields

**How to Check:**
1. Go to Multi-Entity > Overview > Resources > Intercompany Account Mapping
2. Review all mapping pairs
3. Look for "(deleted)" in any Due From/Due To fields

**Solution:**
1. Create the missing account in Shared Chart of Accounts
2. Update all affected IC mappings to use the new account

### 2. Unbalanced Due From/Due To Amounts

**Symptom:** Due From in Entity A doesn't match Due To in Entity B

**How to Check:**
1. Run Balance Sheet for each entity
2. Compare:
   - Entity A "Due From Entity B" vs Entity B "Due To Entity A"
   - These should be equal

**Solution:**
1. Create adjustment Journal Entries:
   - Debit: Opening Balance Equity
   - Credit: Due To [Entity] (for the difference amount)
2. Post JEs in the entity with the lower Due To balance

---

## IC Mapping Structure

### Standard Mapping Pairs
For each pair of entities, you need:
| Field | Entity 1 | Entity 2 |
|-------|----------|----------|
| Due From Company 1 | Asset account | - |
| Due To Company 1 | - | Liability account |
| Due From Company 2 | - | Asset account |
| Due To Company 2 | Liability account | - |

### Account Types
- **Due From:** Other Current Assets (asset)
- **Due To:** Other Current Liabilities (liability)

---

## Shared Chart of Accounts

### How to Create IC Accounts
1. Go to Consolidated View
2. Access Shared Chart of Accounts
3. Click New Account
4. Configure:
   - Account Number: 1083 (or next available)
   - Account Name: "Due From [Entity Name]"
   - Account Type: Other Current Assets
   - Detail Type: Other Current Assets
   - Share with: All companies

---

## Journal Entry Template for IC Adjustments

```
Journal Date: [Current Date]
Journal No.: ADJ-IC-[XXX]

Line 1 (Debit):
  Account: Opening Balance Equity
  Amount: $[Difference Amount]

Line 2 (Credit):
  Account: Due To [Entity Name]
  Amount: $[Difference Amount]

Memo: IC balance adjustment per investigation [Date]
```

---

## Known Limitation (BUG)

### Consolidated View Sync Issue

**Observed Behavior:**
- Journal Entries created in individual entities are saved correctly
- Individual entity Balance Sheets reflect the changes
- Consolidated View DOES NOT reflect entity changes
- Refresh attempts (F5, Ctrl+Shift+R, period change) don't help

**Root Cause:** System/backend issue - not data or configuration

**Workaround:** None available - requires Engineering fix

**Escalation Path:**
1. Document all fixes attempted
2. Verify fixes work at entity level
3. Create Linear ticket with full dossier
4. Escalate to Intuit Engineering

---

## Entities in TCO Environment

| Entity | Role |
|--------|------|
| Traction Control Outfitters | Parent |
| Apex Tire & Auto Retail | Child |
| RoadReady Service Solutions | Child |
| Global Tread Distributors | Child |

---

## Related Resources

- **Dossier (PT):** `Downloads/DOSSIE Consolidated Balance Sheet Out of Balance Investigation.txt`
- **Dossier (EN):** `Downloads/DOSSIER_Consolidated_Balance_Sheet_Investigation_EN.md`
- **Linear Ticket:** PLA-3201
- **QBO Help:** "Tips to resolve an unbalanced consolidated balance sheet in Intuit Enterprise Suite"

---

## Tags

`#qbo` `#ies` `#multi-entity` `#intercompany` `#balance-sheet` `#troubleshooting` `#bug` `#consolidation`

