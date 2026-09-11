# IRC Lookup & Authority

Every number, position, and recommendation this project produces must trace to a
statutory source. This skill is the retrieval and citation layer the other tax
skills depend on.

## Core rule

**No tax conclusion without a cite, and no cite without a read.**

Do not cite a section from memory when the text is reachable. Model recall of the
Code is directionally useful and numerically unreliable — it drifts on dollar
thresholds, phase-out ranges, effective dates, and post-amendment language. Treat
recalled section *numbers* as a search index; treat recalled *amounts* as a
hypothesis to verify.

## Where authority lives in the project

Tax tooling differs per project, so this skill addresses it by **binding name**.
A project records what it actually has in `.claude/tax-profile.md` under *Engine
bindings* (template: `TAX-PROFILE-TEMPLATE.md` in this domain). Where a binding
is absent, fall back to the reference files here plus external verification.

| Binding | What it is good for |
|---|---|
| `catalog` | Curated section summaries and keyword tags for the sections the project touches most. Start here. |
| `vector-store` | Semantic retrieval over Title 26 when the section number is unknown. **Only useful against a populated corpus — see the warning below.** |
| `research-agent` | Model-backed Q&A that grounds answers in retrieved sections. |
| `sync-pipeline` | Ingests Title 26 into the store. |
| `section-schema` | Shape of a stored section record. |
| `constants` | Year-keyed brackets, limits, and phase-outs with Rev. Proc. / Notice citations. **The numeric source of truth for any engine.** |

> **Corpus warning — check before you trust it.** A `vector-store` binding
> existing is not evidence that the Code is in it. Placeholder fixtures and
> half-run sync pipelines are common, and an empty corpus returns confident
> nonsense rather than an error. Confirm the store holds real Code text, for the
> section you are about to cite, before citing it. Until then rely on the
> `catalog` and `constants` bindings, the reference files here, and external
> verification. **Never present a vector-store result as authoritative without
> confirming the corpus is real.**

## Lookup workflow

1. **Frame the question as a legal issue.** Not "can I deduct my car" but "is
   mileage on a vehicle used in a trade or business deductible under §162, and
   what substantiation does §274(d) require."
2. **Find the section.** Check `reference/section-map.md` in this skill first —
   it maps ~120 topics to controlling sections. Then the catalog. Then search.
3. **Read the operative text**, not a summary. Identify: the general rule, the
   exceptions, the definitions subsection, the limitation subsections, and the
   effective-date / sunset language.
4. **Descend the authority ladder** (see `reference/authority-hierarchy.md`).
   Statute → regulations → IRS guidance → case law. A section read without its
   regulations is usually a wrong answer.
5. **Check for amendment.** OBBBA (P.L. 119-21, enacted 2025-07-04) rewrote large
   parts of the Code effective 2025 and 2026. Pre-2025 knowledge of §§174, 168(k),
   179, 199A, 1202, 461(l), 63, 164 is stale. See `reference/obbba-changes.md`.
6. **Get the year's numbers from the `constants` binding**, not from the statute —
   most dollar amounts are inflation-adjusted annually by revenue procedure.
7. **Record the cite** in the form below.

## Citation format

This project uses two interchangeable forms; be consistent within a document.

```
IRC §199A(b)(2)(B)          # prose and reports
26 USC S 199A               # ASCII form, for code comments and datastore keys
```

A complete cite for a position includes **statute + implementing authority + the
year's number**:

> Qualified business income deduction — IRC §199A(a); Treas. Reg. §1.199A-1(c);
> 2026 threshold \$201,775 single / \$403,500 MFJ per Rev. Proc. 2025-32, recorded
> in the project's `constants` binding for tax year 2026.

## Output shape

When answering a lookup, return:

- **Controlling section** — number, title, one-sentence general rule.
- **The test** — the elements that must be satisfied, as a checklist.
- **Limits and phase-outs** — with the current-year figures and their source.
- **Exceptions and traps** — what disqualifies an otherwise-good position.
- **Authority strength** — see `reference/authority-hierarchy.md`; say plainly
  whether this is settled, supported, or aggressive.
- **Verification status** — one of:
  - `VERIFIED` — read against primary text or the `constants` binding this session.
  - `CATALOG` — from the curated catalog; summary only, text not read.
  - `RECALL` — from model knowledge; **must be verified before filing use.**

Never omit the verification status. A `RECALL` figure that reaches a return is a
preparer penalty risk under §6694.

## Reference files

- `reference/authority-hierarchy.md` — what counts as authority, precedential
  weight, the substantial-authority / reasonable-basis / more-likely-than-not
  standards, and when disclosure on Form 8275 is required.
- `reference/section-map.md` — topic → controlling section index covering income,
  deductions, credits, entities, timing, procedure, and penalties.
- `reference/obbba-changes.md` — what P.L. 119-21 changed, with effective dates,
  so pre-2025 assumptions get caught.

## Related skills

`deductions-and-credits` (benefit catalog), `tax-strategies` (planning),
`audit-risk-substantiation` (penalty exposure and disclosure).
