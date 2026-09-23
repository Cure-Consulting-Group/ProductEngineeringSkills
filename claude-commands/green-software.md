# Green Software

Outcome: an SCI score (or estimate with stated uncertainty) for the system, the few changes that
move it most, and — when asked — a stakeholder-ready sustainability report. Done when every number
names its source (provider tool, estimate formula, or grid-intensity API) and each recommendation
has an expected carbon and cost effect. Match length to the need; no filler sections.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Deploy config: `ls firebase.json vercel.json app.yaml Dockerfile *.tf 2>/dev/null | head -10 || echo "(none)"`
- Regions in config: `grep -rhoE '"?region"?\s*[:=]\s*"?[a-z]+-[a-z]+[0-9]' --include=*.json --include=*.tf --include=*.yaml --include=*.ts . 2>/dev/null | sort -u | head -8 || echo "(none found)"`

## Step 1: Classify the Sustainability Need

| Need | Output |
|------|--------|
| Sustainability audit | SCI estimate + ranked reduction levers for the existing system |
| Green architecture design | Region, compute, and scheduling choices for a new system |
| Carbon measurement | SCI method + monitoring (and the tooling in Code/Artifact Generation) |
| ESG reporting | Quarterly report from the template below |
| Mobile efficiency | Battery/network findings for the app |

## Step 2: Gather Context

Ask only for what is missing: cloud provider and regions (and whether they can move), workload
profile (batch vs real-time, steady vs bursty), monthly usage (vCPU-hours, storage TB, egress),
and any client ESG commitment or reporting obligation (CSRD, customer questionnaires).

## Step 3: The Three Levers (in order of typical impact)

1. **Carbon intensity — where and when.** Region choice dominates everything else for cloud
   workloads. Use the provider's published per-region data, not memory: GCP publishes grid carbon
   intensity and carbon-free-energy % per region (cloud.google.com/sustainability/region-carbon);
   AWS and Azure publish less granular data. Time-shift deferrable batch work to low-intensity
   windows with the Green Software Foundation Carbon Aware SDK or a forecast from Electricity Maps
   / WattTime. Latency, data-residency, and compliance constraints override carbon — say so when
   a move is blocked.
2. **Energy proportionality — scale to demand.** Idle capacity still draws substantial power.
   Scale to zero (Cloud Run, Functions) for non-latency-critical services; schedule dev/staging
   shutdown out of hours; right-size instances from utilization data, not guesses.
3. **Embodied carbon — hardware.** Prefer shared/managed services over dedicated capacity. Arm
   instances are usually the most efficient per unit of work: Google claims up to 60% better
   energy efficiency for Axion C4A vs comparable x86 (vendor figure; cite it as such); AWS Graviton
   makes similar claims.

Cure gotcha: carbon and cost usually move together, so hand the cost side to `finops` and keep
this skill to the carbon accounting and the cases where they diverge (e.g. a cheaper region with a
dirtier grid).

## Step 4: Mobile Efficiency (only for the mobile-efficiency classification)

Findings that matter beyond generic performance hygiene:
- Background work through WorkManager (Android) / BGTaskScheduler (iOS), batched so the radio
  wakes rarely; defer large transfers to unmetered networks; respect Low Power / Battery Saver.
- App size: Android App Bundles; iOS app thinning and on-demand resources. (Bitcode is deprecated
  since Xcode 14 — do not recommend it.)
- Dark theme saves display power only on OLED screens, and the saving depends on content and
  brightness. Offer it and follow the system setting; don't claim a fixed percentage.
- Profile with Android Studio Energy Profiler / Battery Historian and Xcode Organizer energy reports.

## Step 5: Measurement — Software Carbon Intensity (SCI)

SCI is ISO/IEC 21031:2024 (the Green Software Foundation spec, standardized):

```
SCI = ((E × I) + M) per R
  E = energy (kWh)            I = grid carbon intensity (gCO2e/kWh)
  M = embodied emissions (amortized share)   R = functional unit (per user, per request, per job)
```

- **E:** prefer the provider's carbon tool (GCP Carbon Footprint, AWS Customer Carbon Footprint
  Tool, Azure Emissions Impact Dashboard) — note they report monthly with a lag and use
  market- or location-based methods; state which. Otherwise estimate from vCPU-hours × per-vCPU
  power coefficients (Cloud Carbon Footprint's published coefficients) and label it an estimate.
- **I:** Electricity Maps or WattTime APIs for real-time/forecast (both need an API key; confirm
  the current Electricity Maps API host and version in its docs before use), provider annual
  averages as fallback.
- **M:** GSF Impact Framework or Cloud Carbon Footprint embodied-emissions coefficients.
- Report SCI per feature by tagging resources per service and allocating proportionally.

When a live number is needed, search the web (current sources, dated) for the region's current
carbon intensity and the latest SCI guidance.

## Step 6: Sustainability Report Template (ESG reporting)

```markdown
## Sustainability Report — [Project] — [Quarter]

| Metric | This quarter | Last quarter | Change |
|---|---|---|---|
| Compute (vCPU-hours) / storage (TB-months) / egress (TB) | | | |
| Estimated energy (kWh) | | | |
| Operational / embodied / total (kgCO2e) | | | |
| SCI (gCO2e per [unit]) | | | |

### Initiatives
| Initiative | Carbon saved (kgCO2e) | Cost saved |
|---|---|---|

### Next quarter goals
- [ ] ...

### Methodology
SCI per ISO/IEC 21031:2024. Energy from [tool / estimate]. Intensity from [source], [location- or
market-based].
```

## Code/Artifact Generation

Applies only when Step 1 classified the request as carbon measurement (tooling) or ESG reporting
(report). Audits and architecture questions get findings, not files.

| Classification | Write |
|---|---|
| Carbon measurement | `scripts/calculate-sci.ts` — SCI from billing/usage export; `src/scheduler/carbon-aware.ts` — defers flagged jobs to low-intensity windows |
| ESG reporting | `docs/sustainability-report.md` from the Step 6 template |

## Cross-References

- `finops` — cost side of the same levers
- `performance-review` — performance work that also cuts energy
- `infrastructure-scaffold` — where region and scaling decisions land
- `observability` — exporting carbon metrics to dashboards
