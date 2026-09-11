# Development Cost Taxonomy & Allocation

How to capture engineering spend so it can be characterized, credited, and
defended — organized by entity, then product, then cost type.

## The capture dimensions

Every development dollar needs four tags. Missing any one makes it unusable.

```
ENTITY     which taxpayer bore the cost         → one row per entity in the group
PRODUCT    which business component              → per repo/product, not "engineering"
CHARACTER  §174A domestic / §174 foreign / §162 / §195 non-R&E startup / funded
PERIOD     pre-release or post-release, by date  → the §41(d)(4)(A) boundary
```

For a pre-revenue entity with a realistic prospect of entering the business the
software serves, qualifying development remains §174A. Only its non-R&E
pre-opening costs fall under §195; revenue is not the dividing line.

"Engineering — $X" in a general ledger is worthless for a credit claim. The
allocation must exist at the **business component** level, because that is the
level at which §41 is computed and examined.

## Chart of accounts structure

Add these as subaccounts or classes so the books produce the analysis directly,
rather than requiring reconstruction at year end.

```
6000  RESEARCH & DEVELOPMENT
  6100  R&D Wages
    6110  Engineering wages — domestic          [QRE, 100%]
    6120  Engineering wages — foreign           [§174 15-yr, NO credit]
    6130  Direct supervision of research        [QRE, 100%]
    6140  Direct support of research            [QRE, 100%]
  6200  Contract Research
    6210  Domestic contractors — risk retained  [QRE at 65%]
    6220  Domestic contractors — funded/IP out  [deductible, NO credit]
    6230  Foreign contractors                   [§174 15-yr, NO credit]
  6300  R&D Supplies & Compute
    6310  Cloud compute — dev/test/training     [QRE, 100%]
    6320  Cloud compute — production hosting    [§162, NOT a QRE]
    6330  Development tooling & licenses        [§162 or QRE — see below]
    6340  R&D supplies (tangible, consumed)     [QRE]
  6400  Post-Release / Maintenance
    6410  Bug fixes, routine maintenance        [§162, NOT a QRE]
    6420  Customer-specific adaptation          [§162, NOT a QRE]
```

**The single most valuable split** is 6310 vs 6320 — cloud spend for development
and training is a QRE; production hosting of a released product is not. One AWS
or Firebase bill contains both. Tag projects in the cloud console **now** so the
allocation comes from the provider's own reporting rather than an estimate.

### Tooling — a common over-claim
General-purpose developer tooling (IDEs, GitHub, Slack, design tools) is normal
§162 overhead, not a QRE. QRE supplies must be **used and consumed in the
research** and are tangible property; software subscriptions generally are
neither. Cloud *compute* is a QRE by a separate statutory provision
(§41(b)(2)(A)(iii)), which is why it is treated differently from other SaaS.

## Wage allocation

```
For each person, for each month:
  hours or % by product  →  qualified vs non-qualified
  ≥80% qualified?        →  substantially-all rule: 100% of wages are a QRE
  <80%?                  →  allocate actual qualified percentage
```

Qualified services are three categories, all of which count at 100%:
- **Performing** qualified research
- **Directly supervising** it (first-line management of researchers; not
  executives two levels removed)
- **Directly supporting** it (e.g. building a test harness for the research)

Excluded regardless of title: general administration, sales, marketing, HR,
finance, customer support, and executive management not directly supervising.

**Owner-operators**: an owner who both writes code and runs the business must
allocate. A 100% claim on an owner's wages requires that ≥80% of their time
genuinely was qualified research — for a founder also doing sales, fundraising,
and operations, that is usually not true, and claiming it invites a reduction that
undermines the credible portion.

## Contract research — the 65% rule and the two tests

A contractor payment is a QRE at **65%** only if **both**:

| Test | Requirement | Failure mode |
|---|---|---|
| **Economic risk** | Payment must be contingent on the success of the research | A fixed-fee, pay-regardless contract fails |
| **Substantial rights** | Taxpayer must retain substantial rights in the results | Work-for-hire assigning all IP to the *contractor* fails; assigning to the *taxpayer* is fine |

Note the direction: you need IP flowing **to** you and risk staying **with** you.

Capture per contractor: agreement, statement of work, invoices, the risk clause,
the IP clause, and whether the work was performed in the US.

## Allocating a shared engineering team across entities

One shared team commonly builds products that will eventually sit in different
entities. Two
distinct problems:

1. **Within one entity** — allocate wages across products for §41 purposes. Products are
   separate business components; the credit is computed on the aggregate but the
   qualification analysis is per component.
2. **Across entities** — when one entity performs development for another
   spoke, that is an **intercompany service** requiring §482 arm's-length pricing.
   The performing entity has the wages and the QREs; the receiving entity has a
   deductible services fee, **not** QREs. **QREs do not transfer with an invoice.**

This decides where the credit lands before a spinout: if the parent does the
development and bills the new entity, **the parent** holds the credit. For the new
entity to hold its own credit it must employ the people doing the work. Decide
this deliberately and early — it also determines which entity can apply §41(h)
against its own payroll taxes.

## Reconciliations that must tie

```
Total engineering wages (6110–6140)  =  W-2 box 1 wages for those people
Wage QREs claimed                    ≤  total engineering wages
Cloud QREs (6310)                    +  6320  =  total cloud invoices
Contractor QREs / 0.65               =  gross domestic qualifying contractor spend
§174A deduction on the return        =  total domestic R&E per the books
                                        ± the ASC 350-40 / 985-20 book-tax difference
Sum of per-product allocations       =  100% of each person's time
```

That last one is the check most often skipped. If the per-product allocations sum
to more than 100% of a person's time, the claim is arithmetically impossible and
an examiner will find it immediately.

## Minimum viable capture for the remainder of 2026

If nothing else gets implemented this year, do these four:

1. **Tag cloud projects** in AWS/GCP/Firebase so dev vs production splits itself.
2. **Monthly allocation memo** per engineer: hours by product, signed and dated.
3. **Per-product release date log** — the pre/post-release boundary, recorded as
   each product ships.
4. **Contractor file** — agreements with the risk and IP clauses identified, and
   the work location.

Everything else can be reconstructed from the books and commit history. These four
cannot.
