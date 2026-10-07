#!/usr/bin/env python3
"""Offline planning calculator. Reads assumptions.json; writes reports only."""
import argparse
import csv
import json
from pathlib import Path


def work_cost(config, work_name):
    """Aggregate every model leg; tokens represent billed usage across all calls."""
    return sum(
        (leg["input_tokens"] * config["models"][leg["model"]]["input_per_million"]
         + leg["output_tokens"] * config["models"][leg["model"]]["output_per_million"])
        / 1_000_000
        for leg in config["work_types"][work_name]["legs"]
    )


def calculate(config, name, products=2, token_multiplier=1.0, retry_multiplier=None):
    scenario = config["scenarios"][name]
    scale = products / config["baseline_products"]
    rates = config["rates"]
    retry = config["token_retry_multiplier"] if retry_multiplier is None else retry_multiplier
    lines = {}
    for work_name, count in scenario["workloads"].items():
        lines["LLM: " + work_name] = count * scale * work_cost(config, work_name) * retry * token_multiplier
    reasoning_minutes = sum(
        count * scale * config["work_types"][work_name]["minutes"]
        for work_name, count in scenario["workloads"].items()
    ) * retry
    browser_minutes = scenario["browser_runs"] * scale * scenario["browser_minutes"] * retry
    job_minute_rate = 60 * (
        rates["job_vcpu"] * rates["cloud_job_vcpu_second"]
        + rates["job_memory_gib"] * rates["cloud_job_gib_second"]
    )
    lines["Cloud Run: agent workers"] = reasoning_minutes * job_minute_rate
    lines["Cloud Run: browser probes"] = browser_minutes * job_minute_rate
    lines["Cloud Run: control API"] = (
        scenario["control_active_seconds"] * scale
        * (rates["service_vcpu"] * rates["cloud_service_vcpu_second"]
           + rates["service_memory_gib"] * rates["cloud_service_gib_second"])
        + scenario["control_requests"] * scale / 1_000_000 * rates["service_per_million_requests"]
    )
    lines["Firestore: reads"] = scenario["firestore_reads"] * scale / 100_000 * rates["firestore_per_100k_reads"]
    lines["Firestore: writes"] = scenario["firestore_writes"] * scale / 100_000 * rates["firestore_per_100k_writes"]
    lines["Firestore: state storage"] = scenario["firestore_gib"] * scale * rates["firestore_gib_month"]
    lines["Storage: retained evidence"] = scenario["artifact_gib"] * scale * rates["storage_gib_month"]
    lines["Storage: evidence egress"] = scenario["egress_gib"] * scale * rates["storage_egress_gib"]
    lines["Logging: ingestion"] = scenario["logging_gib"] * scale * rates["logging_gib"]
    lines["Pub/Sub: throughput"] = scenario["pubsub_gib"] * scale / 1024 * rates["pubsub_per_tib"]
    # Fixed shared schedules; product-specific due times live in configuration.
    lines["Scheduler: shared jobs"] = scenario["scheduler_jobs"] * rates["scheduler_job_month"]
    lines["Secret Manager: versions"] = scenario["secret_versions"] * scale * rates["secret_version_month"]
    lines["Secret Manager: access"] = scenario["secret_accesses"] * scale / 10_000 * rates["secret_per_10k_access"]
    lines["GitHub: incremental Linux CI"] = scenario["linux_minutes"] * scale * rates["github_linux_minute"]
    lines["GitHub: incremental macOS CI"] = scenario["macos_minutes"] * scale * rates["github_macos_minute"]
    lines["Search: optional research calls"] = scenario["search_calls"] * scale / 1000 * rates["search_per_1000"]
    for label, amount in scenario["ancillary_allowance"].items():
        lines["Allowance: " + label] = amount * scale
    lines["Existing subscriptions: incremental"] = config["existing_subscription_increment"]
    subtotal = sum(lines.values())
    reserve = subtotal * config["cash_reserve_fraction"]
    repairs = scenario["workloads"]["repair_bundle"] * scale
    founder_low = scale * (scenario["oversight_hours"][0] + scenario["maintenance_hours"][0]) + repairs * scenario["review_hours_per_repair"][0]
    founder_high = scale * (scenario["oversight_hours"][1] + scenario["maintenance_hours"][1]) + repairs * scenario["review_hours_per_repair"][1]
    return {
        "scenario": name, "products": products, "lines": lines,
        "llm": sum(v for k, v in lines.items() if k.startswith("LLM:")),
        "modeled_monthly_cash": subtotal, "reserve": reserve,
        "monthly_planning_envelope": subtotal + reserve,
        "annual_modeled_cash": subtotal * 12,
        "annual_planning_envelope": (subtotal + reserve) * 12,
        "founder_hours_low": founder_low, "founder_hours_high": founder_high,
        "repair_attempts": repairs,
        "accepted_repairs_assumption": repairs * config["repair_acceptance_assumption"],
        "managed_runtime_worker_delta": reasoning_minutes / 60 * rates["managed_agent_session_hour"] - lines["Cloud Run: agent workers"],
    }


def build_hours(config, stage):
    keys = ["pilot", "expansion"] if stage == "full" else [stage]
    values = [sum(component[key][i] for component in config["effort"] for key in keys) for i in (0, 1)]
    return [value * (1 + config["build_time_reserve_fraction"]) for value in values]


def money(value):
    return ("-$" if value < 0 else "$") + format(abs(value), ",.2f")


def generate(config, products, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    results = [calculate(config, name, products) for name in config["scenarios"]]
    summary_fields = [key for key in results[0] if key != "lines"]
    with (output_dir / "scenario-totals.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary_fields)
        writer.writeheader()
        for result in results:
            writer.writerow({key: round(value, 4) if isinstance(value, float) else value for key, value in result.items() if key != "lines"})
    with (output_dir / "cost-breakdown.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scenario", "products", "line_item", "monthly_usd"])
        for result in results:
            for label, value in result["lines"].items():
                writer.writerow([result["scenario"], products, label, round(value, 6)])
            writer.writerow([result["scenario"], products, "Planning reserve (not expected invoice)", round(result["reserve"], 6)])
    lines = [
        "# Generated cost results", "",
        "Pricing check date: " + config["prepared_date"] + ". USD; incremental platform cash only.",
        "No free-tier, cache, batch, plan allowances, or subscription credits deducted. Ancillary lines are planning allowances.",
        "Monthly tokens/worker runtime include 30% retry allowance; planning reserve adds 25% headroom.", "",
        "| Scenario | Products | LLM/month | Modeled cash/month | With reserve/month | Founder hours/month | Repair attempts |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        lines.append("| " + result["scenario"] + " | " + str(products) + " | " + money(result["llm"]) + " | " + money(result["modeled_monthly_cash"]) + " | " + money(result["monthly_planning_envelope"]) + " | " + format(result["founder_hours_low"], ".1f") + "–" + format(result["founder_hours_high"], ".1f") + " | " + format(result["repair_attempts"], ".0f") + " |")
    lines += ["", "## Monthly line items", "", "| Item | " + " | ".join(r["scenario"] for r in results) + " |", "|---|" + "---:|" * len(results)]
    for label in results[0]["lines"]:
        lines.append("| " + label + " | " + " | ".join(money(r["lines"][label]) for r in results) + " |")
    lines += ["", "## Founder build effort", "", "Two-product initial build. Component estimates include implementation and targeted testing; 20% time reserve added once.", "", "| Stage | Hours including reserve | Weeks at 20 active hours/week, before observation gates | Incremental build cash allowance |", "|---|---:|---:|---:|"]
    for stage in ["pilot", "expansion", "full"]:
        hours = build_hours(config, stage)
        cash = config["build_incremental_cash"].get(stage)
        if cash is None:
            cash = [sum(config["build_incremental_cash"][key][i] for key in ("pilot", "expansion")) for i in (0, 1)]
        lines.append("| " + stage + " | " + format(hours[0], ".1f") + "–" + format(hours[1], ".1f") + " | " + format(hours[0] / 20, ".1f") + "–" + format(hours[1] / 20, ".1f") + " | " + money(cash[0]) + "–" + money(cash[1]) + " |")
    lines += ["", "Pilot observation: 2 weeks; expansion validation: about 4 weeks. Gates and access delays are additional calendar constraints.", "", "## Twelve-month operating period after full launch", "", "Includes full-build cash allowance once, plus 12 operating months; excludes existing product bills and subscriptions.", "", "| Scenario | Incremental cash including build allowance | Cash envelope with operating reserve | Founder operating hours/year |", "|---|---:|---:|---:|"]
    build_cash = [sum(config["build_incremental_cash"][key][i] for key in ("pilot", "expansion")) for i in (0, 1)]
    for result in results:
        lines.append("| " + result["scenario"] + " | " + money(result["annual_modeled_cash"] + build_cash[0]) + "–" + money(result["annual_modeled_cash"] + build_cash[1]) + " | " + money(result["annual_planning_envelope"] + build_cash[0]) + "–" + money(result["annual_planning_envelope"] + build_cash[1]) + " | " + format(result["founder_hours_low"] * 12, ".1f") + "–" + format(result["founder_hours_high"] * 12, ".1f") + " |")
    lines += ["", "Founder build hours are additional to operating hours. For a pilot-only choice, use the pilot cash allowance rather than the full-build allowance.", "", "## Token and retry sensitivity", "", "| Scenario | Base modeled cash | 2× tokens | 5× tokens | No retry overhead | 2× billed attempts/runtime |", "|---|---:|---:|---:|---:|---:|"]
    for result in results:
        name = result["scenario"]
        sensitivity = [calculate(config, name, products, token_multiplier=2), calculate(config, name, products, token_multiplier=5), calculate(config, name, products, retry_multiplier=1), calculate(config, name, products, retry_multiplier=2)]
        lines.append("| " + name + " | " + money(result["modeled_monthly_cash"]) + " | " + " | ".join(money(item["modeled_monthly_cash"]) for item in sensitivity) + " |")
    lines += ["", "2×/5× token sensitivity changes LLM tokens only; retry sensitivity changes LLM usage and worker/browser runtime. CI minutes and ancillary allowances are already budgeted totals.", "", "## Portfolio scale — balanced profile", "", "| Products | Modeled monthly cash | With reserve | Monthly founder hours |", "|---|---:|---:|---:|"]
    for count in (2, 5, 10):
        result = calculate(config, "balanced", count)
        lines.append("| " + str(count) + " | " + money(result["modeled_monthly_cash"]) + " | " + money(result["monthly_planning_envelope"]) + " | " + format(result["founder_hours_low"], ".1f") + "–" + format(result["founder_hours_high"], ".1f") + " |")
    lines += ["", "Scale assumes identical per-product workloads and founder allocations; only shared Scheduler jobs remain fixed. Not a capacity guarantee. New product onboarding is 16–32 active hours each plus 20% time reserve.", "", "## Time payback — balanced profile", "", "Illustrative baseline coordination hours only; do not count development acceleration or avoided incidents without observation.", "", "| Manual coordination baseline/month | Net hours saved using midpoint operating time | Build time payback at midpoint full-build hours | Cash envelope break-even value per saved hour |", "|---|---:|---:|---:|"]
    balanced = calculate(config, "balanced", products)
    operating_mid = (balanced["founder_hours_low"] + balanced["founder_hours_high"]) / 2
    build_mid = sum(build_hours(config, "full")) / 2
    for baseline in config["manual_coordination_baselines"]:
        saved = baseline - operating_mid
        lines.append("| " + str(baseline) + " | " + format(saved, ".1f") + " | " + (format(build_mid / saved, ".1f") + " months" if saved > 0 else "No time payback") + " | " + (money(balanced["monthly_planning_envelope"] / saved) if saved > 0 else "n/a") + " |")
    lines += ["", "Savings are conditional assumptions, not forecasts. Founder time has no cash salary assigned. At optional $100/$150/$200 per hour, value = saved hours × rate minus operating cash; this is opportunity value, not booked cash savings.", "", "## Repair unit economics and managed-runtime comparison", ""]
    repair_tokens = work_cost(config, "repair_bundle") * config["token_retry_multiplier"]
    lines.append("Repair-bundle LLM allowance per attempt: " + money(repair_tokens) + "; at assumed 60% acceptance: " + money(repair_tokens / config["repair_acceptance_assumption"]) + " LLM per accepted repair. This excludes CI, human review and shared platform overhead.")
    lines.append("Balanced assumed accepted repairs/month: " + format(balanced["accepted_repairs_assumption"], ".1f") + "; acceptance is a pilot target, not measured throughput.")
    lines.append("Replacing only modeled agent-worker compute with managed sessions at $0.08/session-hour changes balanced cash by " + money(balanced["managed_runtime_worker_delta"]) + "/month, if runtime and tokens are identical. Browser/CI/control costs remain. Validate managed runtime feature/access fit separately.")
    (output_dir / "cost-results.md").write_text("\n".join(lines) + "\n")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assumptions", type=Path, default=Path(__file__).with_name("assumptions.json"))
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    parser.add_argument("--products", type=int, default=2, help="Scale runtime workloads; build estimate stays two-product baseline.")
    parser.add_argument("--json", action="store_true", help="Also print scenario totals as JSON.")
    args = parser.parse_args()
    if args.products < 1:
        parser.error("--products must be positive")
    config = json.loads(args.assumptions.read_text())
    results = generate(config, args.products, args.output_dir)
    if args.json:
        print(json.dumps([{k: v for k, v in r.items() if k != "lines"} for r in results], indent=2))
    else:
        for result in results:
            print(result["scenario"] + ": " + money(result["modeled_monthly_cash"]) + "/month; reserve envelope " + money(result["monthly_planning_envelope"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
