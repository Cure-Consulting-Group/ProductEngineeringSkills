# Green Software

Build software that minimizes environmental impact. Sustainability is not a nice-to-have — it reduces costs, satisfies ESG requirements, and future-proofs against carbon regulation.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify the Sustainability Need

| Need | Output |
|------|--------|
| Sustainability audit | Carbon footprint assessment of existing system |
| Green architecture design | Low-carbon architecture from the start |
| Carbon measurement | SCI scoring + monitoring dashboard |
| Resource optimization | Right-sizing infrastructure to eliminate waste |
| ESG reporting | Sustainability metrics for stakeholder reporting |
| Mobile efficiency | Battery and network optimization for mobile apps |

## Step 2: Gather Context

1. **Infrastructure** — cloud provider (GCP, AWS, Azure), on-prem, hybrid?
2. **Cloud regions** — which regions are workloads deployed to? Can they move?
3. **Workload profile** — real-time vs batch? Steady vs bursty? CPU-bound vs I/O-bound?
4. **Current resource usage** — monthly compute hours, storage TB, network egress GB?
5. **Client ESG requirements** — any sustainability commitments, reporting obligations, or certifications?
6. **Energy sources** — does cloud provider publish carbon intensity per region?

## Step 3: Carbon-Aware Architecture

```
Three levers to reduce software carbon emissions:

1. CARBON INTENSITY — run workloads where/when electricity is cleanest

   Region selection:
     GCP:  us-west1 (Oregon, low carbon), europe-north1 (Finland, wind/nuclear)
     AWS:  us-west-2 (Oregon), eu-north-1 (Stockholm)
     Azure: westus (Washington), swedencentral (wind power)
     Avoid: asia-south1, us-east4 (coal-heavy grids)

   Check live carbon intensity: https://app.electricitymaps.com
   GCP publishes per-region carbon data: cloud.google.com/sustainability/region-carbon

   Time-shifting batch jobs:
     - Schedule non-urgent workloads for low-carbon windows
     - Most grids are cleanest 10am-4pm (solar peak) and overnight (low demand)
     - Use carbon-aware schedulers: Green Software Foundation's carbon-aware-sdk
     - Cloud Functions / Cloud Run: schedule batch jobs with Cloud Scheduler

2. ENERGY PROPORTIONALITY — match resources to actual demand

   Idle servers consume 40-60% of peak power but do 0% useful work.
   Autoscale to zero whenever possible (Cloud Run, Lambda, App Engine).
   Never run 24/7 infrastructure for workloads that run 8 hours/day.

3. EMBODIED CARBON — reduce hardware manufacturing impact

   Use shared infrastructure (cloud) over dedicated servers
   Extend hardware lifecycle (don't over-provision just to replace sooner)
   Prefer ARM-based instances (Graviton, Tau T2A) — 60% less energy per compute unit
```

## Step 4: Energy-Efficient Patterns

```
Every watt saved = cost saved = carbon saved. Optimize ruthlessly.

Minimize data transfer:
  - Compress responses (gzip/brotli — 70-90% reduction)
  - Use binary protocols (protobuf, MessagePack) over JSON where volume is high
  - Paginate everything — never return unbounded lists
  - GraphQL: require query complexity limits, ban open-ended resolvers
  - Cache aggressively: CDN for static, Redis for dynamic, HTTP cache headers

Efficient algorithms:
  - Profile before optimizing — measure, don't guess
  - O(n) vs O(n^2) matters at scale — review hot paths for algorithmic waste
  - Batch database queries (N+1 is an energy problem, not just a performance one)
  - Debounce/throttle expensive operations (search-as-you-type, scroll handlers)

Reduce compute waste:
  - Eliminate dead code paths (unused features still get deployed and loaded)
  - Remove redundant processing (don't re-parse, re-validate, or re-fetch)
  - Use streaming over buffering for large payloads
  - Prefer push (webhooks, SSE) over poll (repeated empty requests waste energy)

Right-size infrastructure:
  - Audit instance sizes quarterly — most are 2-4x over-provisioned
  - Use committed use discounts (GCP CUDs, AWS Savings Plans) for steady-state
  - Dev/staging environments: schedule shutdown outside business hours
  - Database: right-size instance, enable autoscaling, review query plans
```

## Step 5: Mobile Efficiency

```
Mobile devices are battery-powered. Wasted energy = bad UX + environmental cost.

Battery optimization:
  - Batch network requests (don't wake the radio for every small call)
  - Use WorkManager (Android) / BGTaskScheduler (iOS) for background work
  - Respect low-power mode: reduce animations, polling frequency, background sync
  - Profile with Android Battery Historian / Xcode Energy Organizer

Efficient networking:
  - Use HTTP/2 or HTTP/3 (multiplexing reduces connections)
  - Implement delta sync (send changes, not full state)
  - Compress images before upload (client-side, not server-side)
  - Respect metered connections: defer large downloads to WiFi

Reduce app size:
  - Android: use App Bundles (only ship code for user's device)
  - iOS: enable bitcode, app thinning, on-demand resources
  - Both: tree-shake unused libraries, compress assets, use WebP/AVIF
  - Target: <30MB initial download (smaller = more installs, less energy to download)

UI efficiency:
  - Lazy load off-screen content (RecyclerView/LazyColumn, UICollectionView)
  - Reduce overdraw: profile with GPU overdraw visualization
  - Limit animations: 60fps when needed, skip animations in low-power mode
  - Dark mode: saves 30-60% display power on OLED (offer as default)
```

## Step 6: Cloud Optimization for Sustainability

```
Serverless over always-on:
  Cloud Run / Lambda / Cloud Functions:
    - Scale to zero when idle (zero energy consumed)
    - Pay per invocation (aligns cost with carbon)
    - Cold start tradeoff: acceptable for most workloads (<1s)
    - Use min-instances=0 for non-latency-critical services

  When serverless doesn't fit:
    - Persistent connections (WebSockets): use managed services (Firestore, Pub/Sub)
    - High-throughput steady load: use autoscaled GKE/ECS with aggressive scale-down

Autoscaling to zero:
  - Cloud Run: default behavior, ensure min-instances=0
  - GKE: use Knative or KEDA for event-driven scaling
  - Databases: Firestore (serverless), Cloud SQL with autoscale, or Neon (Postgres serverless)
  - Redis: use Memorystore with automatic scaling, or eliminate caching tier entirely

Storage lifecycle policies:
  - Hot → Nearline (30 days) → Coldline (90 days) → Archive (365 days)
  - Auto-delete logs after retention period (don't store forever by default)
  - Compress stored data (parquet over CSV = 75% less storage)
  - Deduplicate: don't store the same file twice (content-addressable storage)

CDN to reduce origin load:
  - Cache static assets at edge (images, JS, CSS, fonts)
  - Cache API responses where possible (public data, per-user with Vary header)
  - Use stale-while-revalidate for non-critical freshness
  - Edge compute (Cloudflare Workers, Vercel Edge) for transformations
```

## Step 7: Measurement — Software Carbon Intensity (SCI)

```
SCI = ((E x I) + M) per R

  E = Energy consumed (kWh)
  I = Carbon intensity of electricity (gCO2/kWh)
  M = Embodied carbon of hardware (amortized)
  R = Functional unit (per user, per API call, per transaction)

How to measure E (energy):
  Cloud provider tools:
    GCP: Carbon Footprint dashboard (console.cloud.google.com/carbon)
    AWS: Customer Carbon Footprint Tool
    Azure: Emissions Impact Dashboard

  Estimate from compute:
    kWh = (vCPU hours x TDP watts) / 1000
    Typical: 1 vCPU-hour ≈ 0.005-0.01 kWh

  Application-level:
    Use Scaphandre (Linux power measurement) or PowerMetrics (macOS)
    Cloud Carbon Footprint (open source): cloudcarbonfootprint.org

How to measure I (carbon intensity):
  Real-time APIs:
    Electricity Maps API: api.electricitymap.org
    WattTime API: watttime.org
  Static averages:
    GCP publishes per-region annual averages
    Use as fallback when real-time data unavailable

Green Software Foundation tools:
  - Impact Framework (IF): standardized measurement pipeline
  - Carbon Aware SDK: query carbon intensity, shift workloads
  - SCI Guidance: methodology for calculating SCI score

Per-feature carbon cost:
  - Tag cloud resources by feature/service
  - Allocate energy proportionally
  - Track SCI per feature over time
  - Include in feature cost analysis alongside infrastructure cost
```

## Step 8: Sustainability Reporting Template

```markdown
## Sustainability Report — [Project Name] — [Quarter]

### Energy Usage
| Metric | This Quarter | Last Quarter | Change |
|--------|-------------|-------------|--------|
| Total compute (vCPU-hours) | | | |
| Total storage (TB-months) | | | |
| Total network egress (TB) | | | |
| Estimated energy (kWh) | | | |

### Carbon Emissions
| Metric | This Quarter | Last Quarter | Change |
|--------|-------------|-------------|--------|
| Operational carbon (kgCO2e) | | | |
| Embodied carbon (kgCO2e) | | | |
| Total carbon (kgCO2e) | | | |
| SCI score (gCO2e per [unit]) | | | |

### Efficiency Improvements
| Initiative | Carbon Saved (kgCO2e) | Cost Saved |
|-----------|----------------------|------------|
| Region migration to low-carbon | | |
| Right-sizing instances | | |
| Storage lifecycle policies | | |
| Serverless migration | | |
| Image optimization | | |

### Goals for Next Quarter
- [ ] Reduce SCI score by [X]%
- [ ] Migrate [service] to low-carbon region
- [ ] Implement autoscale-to-zero for [service]
- [ ] Add carbon monitoring to CI/CD pipeline

### Methodology
SCI calculated per Green Software Foundation specification v1.0.
Energy estimated via [cloud provider tool / Scaphandre / Cloud Carbon Footprint].
Carbon intensity sourced from [Electricity Maps / provider averages].
```

## Code Generation (Required)

Generate sustainability tooling using Write:
1. **SCI calculator**: `scripts/calculate-sci.ts` — Software Carbon Intensity score from cloud billing
2. **Carbon-aware scheduler**: `src/scheduler/carbon-aware.ts` — delays non-urgent jobs to low-carbon periods
3. **Sustainability report**: `docs/sustainability-report.md` — SCI score, trends, optimization plan

## Cross-References

- `/infrastructure-scaffold` — cloud infrastructure where green decisions are made
- `/finops` — cost optimization aligns directly with carbon optimization
- `/performance-review` — performance improvements reduce energy waste
- `/observability` — monitoring infrastructure for carbon metrics
- `/ci-cd-pipeline` — add carbon measurement to deployment pipelines
