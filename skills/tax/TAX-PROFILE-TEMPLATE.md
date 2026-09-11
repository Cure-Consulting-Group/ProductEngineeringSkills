# Tax profile — template

Copy to `.claude/tax-profile.md` in the consuming project and fill it in. The tax
skills read this file for everything specific to the taxpayer: which entities
exist, what they file, and where the project's tax tooling lives.

**Keep it in the project, not in this library.** Filed figures, basis balances,
and EINs belong in the repo that owns them.

---

## Entities

One row per entity, including the individual. Take the tax classification from
the **filed election and the prior return**, not from the entity's name.

| Entity | Role | Legal form | Tax classification | Return | States | FY | Binding constraint |
|---|---|---|---|---|---|---|---|
| | hub / spoke / inventory / pre-licence / exempt / individual | | | | formation + nexus | | what actually prevents a deduction from being worth anything |

Roles are used by `irc-lookup/reference/section-map.md`,
`return-review/reference/common-errors.md`, and
`tax-strategies/reference/entity-playbook.md`.

### Per-entity facts worth recording

- Carryforwards: NOL by year, suspended losses, credit carryforwards
- Basis: stock and debt basis at year end for each pass-through owner
- Elections made, with the date and the return they were made on
- Payroll: yes/no, and since when
- Open questions, with who owns each one

## Prior-year anchors

- Prior-year AGI and total tax (the §6654 safe-harbor inputs)
- Whether the 110% high-income safe harbor applies
- Accountant of record, and what they sign

## Engine bindings

Where the project ships tax tooling, record it here by binding name. Skills refer
to these names rather than to paths, so a skill works unchanged in a project that
has none. Leave a row blank if the project does not have it.

| Binding | Path | Notes |
|---|---|---|
| `constants` | | Year-keyed brackets, limits, phase-outs. **The numeric source of truth.** |
| `calculator` | | Computes a return; used for baselines |
| `optimizer` | | Strategy search |
| `validator` | | Pre-filing validation / filing readiness |
| `audit-risk` | | Risk scoring |
| `catalog` | | Curated IRC section summaries |
| `vector-store` | | Semantic search over Title 26 — **confirm the corpus is real before citing it** |
| `research-agent` | | Grounded Q&A |
| `sync-pipeline` | | Corpus ingestion |
| `section-schema` | | Stored section record shape |
| `document-ai` | | W-2 / 1099 / 1098 extraction |
| `withholding` | | W-4 and withholding modelling |
| `retirement` | | Roth conversion, contribution limits |
| `salt` | | PTET and SALT workaround modelling |
| `exit-planning` | | Sale and exit scenarios |
| `reasonable-compensation` | | Officer comp analysis |

## Benchmark overlay

`cpa-benchmark` ships portable question sets. Applied questions built on this
taxpayer's own entities and figures go in:

```
.claude/tax-benchmark/questions/*.json
```

They are auto-discovered from the working directory and merged with the bundled
sets — same schema, and an overlay question sharing an id with a bundled one
replaces it. Run `node run.mjs sources` to see what actually loaded.
