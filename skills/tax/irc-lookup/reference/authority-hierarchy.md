# Authority Hierarchy & Confidence Standards

## The ladder

Weight runs from binding on everyone, to binding on the IRS only, to persuasive
only, to worthless-as-authority.

### Tier 1 — Binding law
| Authority | Notes |
|---|---|
| **Internal Revenue Code (26 U.S.C.)** | The statute. Controls unless unconstitutional. |
| **U.S. Supreme Court decisions** | Binding nationwide. |
| **Treaties** | Override conflicting statute for covered persons (§7852(d)). |

### Tier 2 — Regulations
| Authority | Weight |
|---|---|
| **Final Treasury Regulations** | Near-binding. *Chevron* deference was overruled by *Loper Bright* (2024) — courts now decide the best reading themselves, so regs are strong but no longer automatically controlling. Legislative regs (issued under a specific grant, e.g. §199A) remain the hardest to dislodge. |
| **Temporary Regulations** | Same weight as final; expire 3 years from issuance (§7805(e)). |
| **Proposed Regulations** | Not authority for a position, but *may be relied on* if the preamble says so. Signals IRS intent. |

### Tier 3 — Published IRS guidance (binding on the IRS, citable by taxpayers)
| Authority | Use |
|---|---|
| **Revenue Rulings** | IRS's legal conclusion on a stated fact pattern. Cite when your facts match. |
| **Revenue Procedures** | Procedural rules, safe harbors, and the **annual inflation adjustments** (e.g. Rev. Proc. 2025-32 for 2026). |
| **Notices / Announcements** | Interim guidance ahead of regs. Mileage rates (Notice 2026-10), retirement limits (Notice 2025-67). |
| **Actions on Decision** | IRS's acquiescence or nonacquiescence in a loss. |

### Tier 4 — Case law below the Supreme Court
| Court | Precedential reach |
|---|---|
| **Circuit Courts of Appeals** | Binding in that circuit only. **New York → 2nd Circuit** — controlling for any entity whose principal place of business is in New York (the *Golsen* rule). |
| **Tax Court (regular, "T.C.")** | Nationally persuasive; follows the taxpayer's circuit under *Golsen*. |
| **Tax Court memorandum ("T.C. Memo")** | Fact-bound, persuasive only. |
| **District Court / Court of Federal Claims** | Persuasive; refund-suit forum (requires paying first). |
| **Tax Court summary ("T.C. Summ. Op.")** | Small cases. **Cannot be cited as precedent** (§7463(b)). |

### Tier 5 — Not authority (but useful)
Private Letter Rulings, Technical Advice Memoranda, Chief Counsel Advice, and
Field Attorney Advice **may not be cited as precedent** (§6110(k)(3)) — but they
do count toward *substantial authority* under Treas. Reg. §1.6662-4(d)(3)(iii),
and they tell you how the IRS thinks. A PLR binds the IRS only as to the taxpayer
who requested it.

### Tier 6 — Never authority
IRS publications, form instructions, the IRS website, FAQs, phone advice,
software output, treatises, and this skill file. Courts have repeatedly held
taxpayers cannot rely on IRS publications to defeat the statute. Use them to
navigate; cite the law underneath.

## Confidence standards

Match the language you use to the actual strength. These thresholds drive penalty
exposure — see the `audit-risk-substantiation` skill.

| Standard | Rough confidence | What it permits |
|---|---|---|
| **Frivolous** | <5% | Nothing. §6702 penalty territory. |
| **Reasonable basis** | ~20% | Lowest defensible standard. Avoids §6662 negligence **only with disclosure** on Form 8275/8275-R. |
| **Substantial authority** | ~35–40% | Avoids the §6662 substantial-understatement penalty **without** disclosure. The working standard for most planning. |
| **More likely than not** | >50% | Required for tax shelters and reportable transactions; the standard for a preparer to avoid §6694(a) on an undisclosed unreasonable position. |
| **Should** | ~70–80% | Common opinion-letter level. |
| **Will** | ~95% | Reserved for positions with no meaningful contrary authority. |

**Substantial authority is an objective test**, weighed on the authorities that
exist — not on the taxpayer's belief and not on audit odds. "They probably won't
catch it" is not authority and must never appear in a work product.

## Disclosure decision

```
Position has substantial authority?
├── Yes → file without disclosure
└── No → reasonable basis?
    ├── Yes → disclose on Form 8275 (8275-R if contrary to a regulation)
    └── No  → do not take the position
```

Disclosure defeats the accuracy penalty but **advertises the issue**. It does not
help at all for: negligence, listed transactions, or economic-substance failures
under §7701(o) — that last one carries a **strict-liability 40% penalty**
(§6662(b)(6), (i)) that no disclosure and no opinion can avoid.

## Applying this to a multi-entity group

- **Circuit**: identify the controlling circuit once and record it in the tax
  profile. It follows the **taxpayer's residence or principal place of business**,
  not the state of incorporation — an entity incorporated in Delaware and
  operating in New York litigates under 2nd Circuit law.
- **Aggressive positions** on any group entity's return get written up with the
  authority tier and confidence standard stated explicitly. Document them
  contemporaneously, preserve reviewer independence, and do not wait for an audit.
- When a position rests on `RECALL` only, it is not yet a position. It is a
  research task.
