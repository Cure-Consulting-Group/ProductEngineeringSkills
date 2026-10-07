#!/usr/bin/env python3
"""Offline incremental Recruiting calculator; writes reports in this directory only."""
import csv
import json
import runpy
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
shared = runpy.run_path(str(PARENT / "cost_model.py"))
calculate = shared["calculate"]
money = shared["money"]


def load_config():
    config = json.loads((PARENT / "assumptions.json").read_text())
    recruiting = json.loads((HERE / "assumptions.json").read_text())
    config["baseline_products"] = 1
    config["scenarios"] = recruiting["scenarios"]
    config["prepared_date"] = recruiting["prepared_date"]
    config["cash_reserve_fraction"] = recruiting["cash_reserve_fraction"]
    return config, recruiting


def build_hours(recruiting):
    base = [sum(item["hours"][i] for item in recruiting["effort"]) for i in (0, 1)]
    return base, [x * (1 + recruiting["build_time_reserve_fraction"]) for x in base]


def generate():
    config, recruiting = load_config()
    results = [calculate(config, name, 1) for name in recruiting["scenarios"]]
    with (HERE / "cost-breakdown.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scenario", "product", "line_item", "incremental_monthly_usd"])
        for result in results:
            for label, value in result["lines"].items():
                writer.writerow([result["scenario"], recruiting["product"], label, round(value, 6)])
            writer.writerow([result["scenario"], recruiting["product"], "Planning reserve (not expected invoice)", round(result["reserve"], 6)])

    base, reserved = build_hours(recruiting)
    lines = [
        "# Initiated Recruiting — generated incremental cost results", "",
        "Pricing assumption check: " + recruiting["prepared_date"] + ". USD. One product's marginal usage on the existing shared platform.",
        "No second coordinator, scheduler jobs, dashboard, macOS CI, existing subscriptions or existing product hosting is charged here.",
        "Usage includes 30% retry/token overhead from the shared model; planning envelope adds 25% unused cash headroom.", "",
        "| Scenario | LLM/month | Modeled incremental cash/month | With reserve/month | Founder operating hours/month | Repair attempts/month |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        lines.append("| " + result["scenario"] + " | " + money(result["llm"]) + " | " + money(result["modeled_monthly_cash"]) + " | " + money(result["monthly_planning_envelope"]) + " | " + f'{result["founder_hours_low"]:.1f}–{result["founder_hours_high"]:.1f}' + " | " + str(int(result["repair_attempts"])) + " |")
    lines += ["", "## Monthly line items", "", "| Item | " + " | ".join(r["scenario"] for r in results) + " |", "|---|" + "---:|" * len(results)]
    for label in results[0]["lines"]:
        lines.append("| " + label + " | " + " | ".join(money(r["lines"][label]) for r in results) + " |")
    lines += [
        "", "## Build investment", "",
        f"Story sum: {base[0]:.0f}–{base[1]:.0f} founder-active hours; with one 20% reserve: {reserved[0]:.1f}–{reserved[1]:.1f} hours.",
        "At 20 focused hours/week this is " + f"{reserved[0]/20:.1f}–{reserved[1]/20:.1f} equivalent build weeks, before fixed observation windows and access delays.",
        "Incremental setup/test cash allowance: " + money(recruiting["build_incremental_cash"][0]) + "–" + money(recruiting["build_incremental_cash"][1]) + ". Existing subscription invoices are unchanged baseline cash.",
        "", "## Twelve operating months after integration, plus one setup allowance", "",
        "| Scenario | Modeled incremental cash incl. setup | Envelope incl. operating reserve and setup | Founder operating hours/year |",
        "|---|---:|---:|---:|",
    ]
    for result in results:
        low, high = recruiting["build_incremental_cash"]
        lines.append("| " + result["scenario"] + " | " + money(result["annual_modeled_cash"] + low) + "–" + money(result["annual_modeled_cash"] + high) + " | " + money(result["annual_planning_envelope"] + low) + "–" + money(result["annual_planning_envelope"] + high) + " | " + f'{result["founder_hours_low"]*12:.1f}–{result["founder_hours_high"]*12:.1f}' + " |")
    lines += ["", "## Token and retry sensitivity", "", "| Scenario | Base cash/month | 2× tokens | 5× tokens | No retry overhead | 2× billed attempts/runtime |", "|---|---:|---:|---:|---:|---:|"]
    for result in results:
        name = result["scenario"]
        variants = [calculate(config, name, 1, token_multiplier=2), calculate(config, name, 1, token_multiplier=5), calculate(config, name, 1, retry_multiplier=1), calculate(config, name, 1, retry_multiplier=2)]
        lines.append("| " + name + " | " + money(result["modeled_monthly_cash"]) + " | " + " | ".join(money(v["modeled_monthly_cash"]) for v in variants) + " |")
    lines += ["", "Token variants change LLM tokens only. Retry variants change LLM and Cloud Run worker/browser time. CI and allowances are already monthly totals.", "", "## Time payback illustration — balanced profile", "", "Assumes the same current-workflow task scope and balanced midpoint founder operating time. Values are scenarios, not measured savings.", "", "| Current coordination hours/month | Net hours saved/month | Build-time payback | Cash envelope per saved hour |", "|---|---:|---:|---:|"]
    balanced = next(r for r in results if r["scenario"] == "balanced")
    operating_mid = (balanced["founder_hours_low"] + balanced["founder_hours_high"]) / 2
    build_mid = sum(reserved) / 2
    for baseline in recruiting["manual_coordination_baselines"]:
        saved = baseline - operating_mid
        payback = f"{build_mid/saved:.1f} months" if saved > 0 else "No time payback"
        cash_per_hour = money(balanced["monthly_planning_envelope"]/saved) if saved > 0 else "n/a"
        lines.append(f"| {baseline} | {saved:.1f} | {payback} | {cash_per_hour} |")
    lines += ["", "Founder build hours are additional to operating hours. Cash per saved hour is an incremental usage hurdle, not an assigned wage. Repair acceptance and product outcomes are not inferred from modeled attempts."]
    (HERE / "cost-results.md").write_text("\n".join(lines) + "\n")
    return results


if __name__ == "__main__":
    for result in generate():
        print(result["scenario"] + ": " + money(result["modeled_monthly_cash"]) + "/month; envelope " + money(result["monthly_planning_envelope"]))
