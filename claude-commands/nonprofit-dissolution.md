# NY Nonprofit Dissolution & Final Filings

Two tracks that run in parallel and must be sequenced correctly:

```
FEDERAL   IRS — final Form 990 series + Schedule N, terminating exempt status
STATE     NY — AG Charities Bureau approval → Certificate of Dissolution at DOS
```

**The state track gates the federal one in practice**, because the final 990 must
report where the assets actually went, and in New York the asset distribution
plan generally requires Attorney General approval before it happens.

> Confidence note: the federal requirements below are settled. **NY N-PCL
> procedure and form numbers are marked `VERIFY`** — confirm against the current
> Charities Bureau and Department of State instructions before filing, since the
> Non-Profit Revitalization Act amendments changed the process and the forms have
> been revised since.

## The one rule that cannot be broken

**Remaining assets must go to another 501(c)(3) organization or to a government
entity** — never to directors, officers, members, or any private individual.

This is the organizational-test dissolution clause required by
Treas. Reg. §1.501(c)(3)-1(b)(4), and it is almost certainly in the certificate of
incorporation. Distributing assets to insiders is **private inurement**, can
retroactively jeopardize exempt status for open years, and exposes the individuals
to §4958 excess benefit excise taxes.

Check the certificate of incorporation for the actual dissolution clause **before**
planning any distribution — some name a specific successor organization.

## Sequence

```
1.  Board resolution adopting a Plan of Dissolution and Distribution of Assets
2.  Member approval, if a membership corporation (check the bylaws)
3.  Settle liabilities — creditors are paid before any charitable distribution
4.  NY Attorney General (Charities Bureau) approval of the Plan   [VERIFY route]
       · assets remaining → AG approval, or NY Supreme Court if AG declines
       · no assets → simplified track
5.  File Certificate of Dissolution with NY Department of State,
       with the AG approval attached                              [VERIFY form]
6.  Distribute the assets per the approved plan — get receipts
7.  Final CHAR500 with the Charities Bureau                       [VERIFY]
8.  Final IRS Form 990 series, marked FINAL, with Schedule N
9.  Final payroll returns, if there were ever employees
10. Close bank accounts, cancel registrations, retain records
```

Do not file the Certificate of Dissolution before the AG approval is in hand, and
do not distribute assets before the plan is approved.

## Federal — the final return

| Gross receipts / assets | Form |
|---|---|
| Normally ≤ \$50,000 | **Form 990-N** (e-Postcard) — has a "terminated" checkbox |
| < \$200,000 receipts **and** < \$500,000 assets | **Form 990-EZ** + Schedule N |
| Otherwise | **Form 990** + Schedule N |
| Private foundation | **Form 990-PF** — different termination rules under §507, including a potential termination tax. Get advice if this applies. |

**Schedule N** (Liquidation, Termination, Dissolution or Significant Disposition
of Assets) is the core document. It reports, asset by asset: what was distributed,
fair market value, the recipient's name, address, and EIN, and whether any officer
or director became an owner of the assets.

**Mark the return FINAL** — check the "Final return/terminated" box in the header.
This is what tells the IRS the organization is terminating; there is no separate
termination application for a public charity.

### Due date
The 15th day of the **5th month** after the end of the tax year — May 15 for a
calendar-year organization. On termination, the final return is due the 15th day of
the 5th month after the **date of termination**. Form 8868 extends filing by six
months.

### Attachments to the final return
- Certified copy of the Certificate of Dissolution / articles of dissolution
- The approved Plan of Dissolution
- A schedule of assets distributed with recipients and EINs
- Board resolution

### The penalty for skipping this
Failing to file for **three consecutive years** triggers **automatic revocation**
of exempt status under §6033(j). Filing a proper final return closes the record
cleanly instead of leaving an organization that appears delinquent.

## If there were employees

```
[ ] Final Form 941 — check the "final return" box, and attach a statement
    with the name and address of the person keeping the payroll records
[ ] Final Form 940 (FUTA)
[ ] W-2s to employees, W-3 to SSA — due by the normal January deadline,
    or earlier if requested by an employee after termination
[ ] Final NYS-45 (NY quarterly combined withholding/wage reporting)
[ ] Deregister for NY withholding and unemployment insurance
[ ] Confirm all payroll deposits are settled — Sec. 6672 trust fund
    recovery attaches personally to responsible persons and survives
    dissolution of the entity
```

That last point matters: dissolving the corporation does **not** extinguish
personal liability for unpaid withheld payroll taxes.

## If there were contractors

Final Forms 1099-NEC for the year, due January 31. The obligation survives
dissolution.

## Records retention

Keep for **at least 3 years after the final return**, and preferably permanently:
- Certificate of incorporation, bylaws, and all amendments
- The IRS determination letter
- All Forms 990 filed (these are public documents; keep the originals)
- Board minutes, especially the dissolution resolution
- Plan of Dissolution and the AG approval
- Asset distribution receipts with recipient EINs
- Final Certificate of Dissolution as filed

## What this does NOT do

Dissolution does not resolve open issues. If the organization has unfiled prior
returns, unpaid payroll taxes, or an unresolved excess-benefit transaction, those
survive. Identify them **before** dissolving, when the organization still has
assets and standing to address them.

## Reference files

- `reference/dissolution-checklist.md` — the working checklist with the document
  intake list and the information needed to begin.

## Related skills

`tax-preparation` (final return mechanics), `cpa-standards` (workpapers and
retention), `audit-risk-substantiation` (penalty exposure on unfiled returns).
