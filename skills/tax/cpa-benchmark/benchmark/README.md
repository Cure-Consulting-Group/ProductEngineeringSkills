# Benchmark harness

Zero dependencies. Node 18+.

```
run.mjs              scorer / exam runner
questions/*.json     bundled question banks — add files freely, they auto-load
```

Commands: `stats`, `sources`, `list`, `template`, `score <file>`, `key`.
Flags: `--set <name>`, `--area <substring>`, `--questions <dir>` (repeatable).

Answer file is a flat map of question id to answer:

```json
{ "REG-001": "B", "REG-008": 14129.55 }
```

Exit code 0 = pass (>=75%), 1 = fail. Suitable as a CI or pre-filing gate.

## Project overlays

The bundled sets are portable — doctrine and law, no client facts. A project adds
its own applied questions, built on its real entities and figures, without
copying them into this shared library:

| How | Precedence |
|---|---|
| `.claude/tax-benchmark/questions/` under the working directory | auto-discovered |
| `CPA_BENCHMARK_QUESTIONS=dir1:dir2` | after auto-discovery |
| `--questions <dir>`, repeatable | last, wins over both |

Overlay files use the same schema. Later sources win on question id, so a project
can also correct a bundled question locally. `node run.mjs sources` prints the
directories in play and which set came from where.

See `../SKILL.md` for the self-assessment protocol and maintenance rules.
