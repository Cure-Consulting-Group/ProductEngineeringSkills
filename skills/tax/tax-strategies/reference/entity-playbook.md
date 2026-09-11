# Entity Playbook — how to build one

The strategy catalog in `strategy-playbook.md` is organised by *strategy*. A
working playbook is organised by *entity*, because that is how decisions actually
get made: someone asks "what should this company do before year end," not "where
does §41(h) apply."

This file is the method for building that per-entity playbook. Write the result
into the project's `.claude/tax-profile.md` — not here. The facts belong to the
taxpayer; the method belongs to the library.

## Build order

1. **Fix the classification before anything else.** For each entity: the legal
   form, the *tax* classification, the return it files, its states, and its
   fiscal year. These diverge more often than people expect — an LLC that elected
   S-corp treatment files an 1120-S on March 15, and a group that assumes
   otherwise misses the deadline by a month. Take the classification from the
   **filed election and the prior return**, never from the entity's name or how
   anyone describes it.
2. **Write down each entity's role in the group.** Hub, product spoke, inventory
   business, pre-licence business, exempt organisation, individual. The role
   determines which strategies are even reachable.
3. **Record the binding constraint per entity.** What is actually driving tax, or
   preventing a deduction from being worth anything? Zero basis. An NOL that
   makes this year's deduction worthless. No payroll, so no wage QREs. Not yet
   carrying on a trade or business. Strategies that do not touch the binding
   constraint produce noise.
4. **Then screen the catalog** against each entity, and keep only what survives
   step 3.
5. **Sequence by deadline, not by size.** A trivial election with a hard date
   outranks a large structural change with a flexible one.

## Questions that must be answered per entity type

### C corporation — services or consulting hub

- Is its own stock **permanently disqualified** from §1202 under §1202(e)(3)?
  Consulting, health, law, accounting, and financial services all are. If so,
  QSBS has to live at spoke level and that decision belongs at formation.
- Is there **owner payroll**? Without it there are no wage QREs, and a §41 credit
  collapses to supplies plus 65% of contractor spend. Any recommendation to start
  payroll needs a reasonable-compensation analysis *first* — wages manufactured
  to produce a credit are net-negative and indefensible.
- Is the **§41(h) payroll offset** available and elected? Up to \$500,000 of credit a year (tax years beginning after 2022):
  \$250,000 against the employer share of Social Security tax, the rest against
  Medicare tax, which is what converts a dead
  carryforward into cash at a company with no tax liability. **It must be elected
  on a timely filed original return** — it cannot be added by amendment.
- Is there unamortized **2022–2024 domestic R&E** on the books that §174A
  retroactive relief could recover?
- Are **intercompany services** papered — written agreement, a defensible method,
  benchmarking, and actual invoicing *and payment*? Booked-but-unpaid fees invite
  a §482 reallocation.
- Is there an **NOL carryforward**, and when does it absorb? This changes the
  value of every deduction accelerated into a loss year.
- Does **§531** accumulated-earnings exposure grow as products monetize? Document
  business needs in board minutes while the need is real.

### C corporation — product spoke

- **When was the stock issued?** The §1202 clock starts at issuance, and the
  regime differs on either side of 2025-07-04. Every month of delay in forming
  and issuing adds a month to the exit horizon.
- Is there vesting? **§83(b) is 30 days, no extensions, no relief.**
- Was the **gross-assets evidence captured at issuance**? It cannot be
  reconstructed later, and it is the fact QSBS turns on.
- Did the **IP arrive before it had value**? A §351 contribution after value
  accrues may be a taxable sale or a §482 event instead.
- Does it have **franchise obligations regardless of income** in its state of
  incorporation and every state it is qualified in?

### Pass-through — Schedule C, partnership, or S corporation

- What is **stock and debt basis** at year end? Zero basis suspends losses under
  §1366(d), and a shareholder **guarantee creates no debt basis** — only a direct
  loan does. A basis schedule is the single most commonly missing workpaper.
- Is officer compensation **reasonable** (S corp)? Zero salary with
  distributions is the most examined position in the category, and an artificially
  low wage can also *reduce* the §199A deduction through the W-2 wage limit.
- Is there a **PTET election** available, and is its deadline irrevocable?
- Has it had **consecutive losses**? Count them against the 3-of-5 §183
  presumption and build the profit-motive file now.

### Inventory business

- Does **ending inventory** match the story the business tells about itself? A
  business described as building inventory that reports \$0 ending inventory has
  a §263A/§471(c) problem, not a rounding difference.
- Is the reported **activity code** consistent with what it actually does?
  Manufacturing-only provisions such as §168(n) do not reach a business whose
  return reports retail.

### Pre-operating or pre-licence entity

- What is the **business-begins date**? It is a factual determination that controls
  non-R&E §195 versus §162 treatment and needs to be fixed contemporaneously.
  Qualifying R&E remains §174A before that date when the entity has a realistic
  prospect of entering the business the research serves.
- How many consecutive zero-revenue years? At some point the question stops being
  §183 and becomes whether a trade or business exists at all.

### Exempt organisation

- Is it continuing or winding down? A dissolution has its own sequence — see the
  `nonprofit-dissolution` skill.

## Cross-entity items

These are decided once for the group, not per entity:

- **Where QSBS lives**, and whether the structure supports it.
- **Transfer pricing** method and paper for every intercompany service.
- **Which entity employs the engineers** — the credit follows the employer, and
  QREs do not transfer with an invoice.
- **Spinout sequencing**: IP assignment before the trademark filing, before the
  first regulated agreement, before first revenue.
- **The individual's** estimated payments, which absorb every pass-through
  result above.

## Output

For each entity, a numbered priority list where every row carries: the action,
the section, why it matters *for this entity*, the deadline as a **date**, and
who executes it. Anything without a date and an owner will not happen.
