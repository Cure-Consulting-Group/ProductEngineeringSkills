---
name: qsbs-compliance
version: "1.0.0"
description: "Track and enforce IRC §1202 QSBS qualification — gross asset test (<$50M), active business test (>80% qualified), C-Corp status, holding period tracking, and disqualifying event detection"
when_to_use: "Use when reviewing entity structure, equity changes, asset growth, business activity classification, or any change that could affect QSBS qualification. Also use for annual QSBS health checks. NOT for general tax advice (consult a CPA). NOT for compliance frameworks like HIPAA/GDPR (use compliance-architect)."
argument-hint: "[entity-or-product]"
allowed-tools: ["Read", "Grep", "Glob"]
context: fork
---

# QSBS Compliance Tracker

IRC §1202 Qualified Small Business Stock compliance monitoring. QSBS allows up to $10M (or 10× basis) in capital gains exclusion per shareholder — but qualification is fragile. A single disqualifying event can void the entire exclusion retroactively.

This skill does NOT constitute tax advice. All output requires CPA/tax attorney review.

## Step 1: Classify the QSBS Task

| Task | Output | Urgency |
|------|--------|---------|
| Initial qualification assessment | Full §1202 checklist with pass/fail per criterion | High — do before any equity event |
| Holding period tracker | Per-shareholder holding period table with 5-year countdown | Ongoing |
| Disqualifying event scan | Risk analysis of proposed corporate action | Critical — run before any structural change |
| Annual health check | Year-end compliance scorecard | Annual |
| Equity event impact | Pre/post analysis of proposed issuance, buyback, or redemption | Before event |
| Entity structure review | C-Corp status verification, subsidiary analysis | On change |

## Step 2: Gather Context

1. **Entity** — which C-Corp? (Vendly Inc., Autograph Health Inc., etc.)
2. **Incorporation** — state, date, current status
3. **Stock issuance history** — dates, shareholders, consideration paid, share classes
4. **Gross assets** — current aggregate gross assets (cash + property + equipment at cost basis, not FMV)
5. **Business activities** — breakdown of qualified vs non-qualified activities by revenue/time
6. **Recent or planned actions** — any redemptions, buybacks, recapitalizations, conversions, or entity changes

## Step 3: §1202 Qualification Criteria

Run each test. ALL must pass simultaneously and continuously.

### Test 1: C-Corporation Requirement
- Entity must be a domestic C-Corporation at time of stock issuance
- S-Corp, LLC, LP, or foreign corp stock does NOT qualify
- **Check**: Read articles of incorporation, verify no S-election (Form 2553) filed
- **Disqualifier**: Converting to S-Corp or LLC voids QSBS retroactively for all shares issued during C-Corp period? No — only shares issued while a C-Corp qualify; conversion doesn't void existing QSBS but no new QSBS can be issued

### Test 2: Original Issuance
- Stock must be acquired at original issuance (not secondary market)
- Must be acquired for money, property (not stock), or services
- Convertible debt that converts counts if conversion is into newly issued stock
- SAFE conversions count if resulting stock is newly issued
- **Check**: Review cap table for secondary transfers, stock purchase agreements

### Test 3: Gross Asset Test (<$50M)
- Aggregate gross assets must not exceed $50M at any time from incorporation through immediately after the stock issuance
- Gross assets = cash + adjusted basis of all property (NOT fair market value)
- Includes assets of subsidiaries (>50% owned)
- **Check**: Balance sheet at each issuance date, adjusted basis records
- **Disqualifier**: Exceeding $50M at any point after incorporation and before/during issuance permanently disqualifies that issuance

### Test 4: Active Business Test (>80% Qualified)
- At least 80% of assets (by value) must be used in the active conduct of one or more qualified trades or businesses
- Measured continuously during substantially all of the holding period
- **Excluded businesses** (these do NOT qualify):
  - Professional services (health, law, engineering, accounting, consulting, financial services)
  - Banking, insurance, financing, leasing, investing
  - Farming
  - Mining, oil, gas
  - Hotels, motels, restaurants (operating, not SaaS for them)
- **Software/SaaS IS qualified** — building and selling software products qualifies
- **Consulting revenue is NOT qualified** — if >20% of revenue comes from consulting/professional services, risk increases
- **Check**: Revenue breakdown by activity type, employee time allocation

### Test 5: Holding Period (5 Years)
- Shareholder must hold stock for at least 5 years from issuance date
- Partial exclusion available via §1045 rollover if sold before 5 years (held >6 months)
- **Check**: Issuance date per shareholder, calculate 5-year anniversary

### Test 6: Redemption Restrictions
- The corporation must not have made significant redemptions (>5% of aggregate value) within 2 years before or 1 year after the issuance
- "Significant" = more than de minimis
- Targeted redemptions of the shareholder's family are always disqualifying
- **Check**: All buyback/redemption transactions within the window

## Step 4: Disqualifying Event Detection

Scan for these red flags. Any one can void QSBS:

| Event | Risk Level | Action |
|-------|-----------|--------|
| S-Corp election filed | **CRITICAL** | Blocks all future QSBS issuance |
| LLC conversion | **CRITICAL** | Voids qualification structure entirely |
| Gross assets exceed $50M | **CRITICAL** | Disqualifies all issuances after threshold crossed |
| Stock buyback >5% within window | **HIGH** | May disqualify specific issuances |
| Revenue mix shifts to >20% consulting | **HIGH** | Active business test at risk |
| Merger or acquisition | **HIGH** | Depends on structure — stock-for-stock may preserve, asset sale may not |
| Stock transferred (not original issuance) | **MEDIUM** | Transferred shares lose QSBS status (exceptions: gift, death, certain partnerships) |
| Significant idle cash / investment assets | **MEDIUM** | Assets not used in active business reduce the 80% test |
| Foreign subsidiary >50% | **MEDIUM** | Must be domestic C-Corp; foreign sub assets may not count toward active business |
| Real estate holding | **LOW** | Rental real estate is generally not "active" unless substantial services |

## Step 5: Output — QSBS Compliance Scorecard

Generate this artifact for each entity:

```markdown
# QSBS Compliance Scorecard — [Entity Name]

**Assessment Date**: [date]
**Entity**: [name], [state] C-Corporation
**Incorporation Date**: [date]
**Status**: QUALIFIED / AT RISK / DISQUALIFIED

## §1202 Test Results

| Test | Status | Detail |
|------|--------|--------|
| C-Corp Status | PASS/FAIL | [current entity type, any elections] |
| Original Issuance | PASS/FAIL | [secondary transfers found?] |
| Gross Asset Test (<$50M) | PASS/FAIL | Current: $[X]M. Headroom: $[50-X]M |
| Active Business (>80%) | PASS/FAIL | Qualified: [X]%, Non-qualified: [Y]% |
| Holding Period (5yr) | TRACKING | [table of shareholders with dates] |
| Redemption Window | PASS/FAIL | [recent redemptions within 2yr/1yr] |

## Holding Period Tracker

| Shareholder | Shares | Issuance Date | 5-Year Date | Status |
|-------------|--------|---------------|-------------|--------|
| [name] | [count] | [date] | [date] | [X yr Y mo remaining] |

## Risk Factors

| Risk | Severity | Mitigation |
|------|----------|------------|
| [identified risk] | CRITICAL/HIGH/MEDIUM/LOW | [recommended action] |

## Upcoming Events Requiring QSBS Review

- [ ] [planned equity event or corporate action]

## Disclaimer

This assessment is for planning purposes only. It does not constitute tax or legal
advice. Consult a qualified CPA and tax attorney before making decisions based on
QSBS qualification status. IRC §1202 has complex interaction with state tax laws
that vary by jurisdiction.
```

## Step 6: Cure Portfolio QSBS Status

For Cure Consulting Group entities, track these specifically:

| Entity | Key Risk | Monitoring Frequency |
|--------|----------|---------------------|
| Vendly Inc. | Consulting revenue mix (Cure performs dev work — is this "consulting"?) | Quarterly |
| Autograph Health Inc. | Gross asset test as fundraising increases | Each funding round |
| Any new C-Corp | Original issuance documentation at formation | At incorporation |

## Cross-References

- For HIPAA/GDPR/PCI compliance: use `compliance-architect`
- For cap table modeling: use `investor-reporting` or `fundraising-materials`
- For entity structure decisions: consult tax attorney (no skill replaces this)
- For Delaware franchise tax: use `corp-finance-ops` (when available)
