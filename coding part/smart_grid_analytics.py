"""
Smart Grid Municipal Energy Analytics System and Peak Load Predictor

Course  : CSA0812 - Python Programming
Project : Smart Grid Municipal Energy Analytics

This program:
1. Reads raw municipal smart-grid telemetry.
2. Validates and filters corrupted records.
3. Aggregates energy consumption by sector.
4. Calculates average and peak load.
5. Calculates a demand-surge multiplier.
6. Classifies sectors as NORMAL, ELEVATED or CRITICAL.
7. Generates a prioritized balancing plan.
8. Displays a console dashboard.
9. Exports the final analysis to a text file.
"""

import os
from datetime import datetime


# ============================================================
# 1. STATIC CONFIGURATION
# ============================================================

SECTOR_LOOKUP = {
    "RES": "Residential",
    "COM": "Commercial",
    "IND": "Heavy_Industrial"
}

SURGE_THRESHOLD_KWH = {
    "Residential": 550.0,
    "Commercial": 1600.0,
    "Heavy_Industrial": 3300.0
}

MAX_PENALTY_MULTIPLIER = 2.5


# ============================================================
# 2. RECORD PARSING AND VALIDATION
# ============================================================

def parse_record(raw_line):
    """
    Parse one telemetry record.

    Expected format:
    Sector_Code # Timestamp # Grid_Load_kWh # Current_Tariff_Rate

    Returns:
        (record, "ok") on success
        (None, rejection_reason) on failure
    """

    fields = raw_line.strip().split("#")

    # Check number of fields
    if len(fields) != 4:
        return None, "malformed_field_count"

    sector_code, timestamp, load_raw, tariff_raw = (
        field.strip() for field in fields
    )

    # Validate sector
    if sector_code not in SECTOR_LOOKUP:
        return None, "misaligned_sector_key"

    # Validate timestamp
    if not timestamp:
        return None, "missing_timestamp"

    # Validate missing numeric fields
    if load_raw == "" or tariff_raw == "":
        return None, "missing_numeric_field"

    # Convert numeric values
    try:
        load_kwh = float(load_raw)
        tariff_rate = float(tariff_raw)
    except ValueError:
        return None, "non_numeric_value"

    # Validate physical values
    if load_kwh < 0 or tariff_rate <= 0:
        return None, "negative_or_invalid_value"

    record = {
        "sector": SECTOR_LOOKUP[sector_code],
        "timestamp": timestamp,
        "load_kwh": load_kwh,
        "tariff_rate": tariff_rate
    }

    return record, "ok"


# ============================================================
# 3. LOAD AND FILTER TELEMETRY
# ============================================================

def load_telemetry(filepath):
    """
    Read telemetry data line by line.

    Valid records are stored separately from rejected records.
    """

    valid_records = []
    rejection_log = {}

    try:
        with open(filepath, "r") as log_file:

            for line_number, raw_line in enumerate(log_file, start=1):

                if not raw_line.strip():
                    continue

                record, status = parse_record(raw_line)

                if status == "ok":
                    valid_records.append(record)

                else:
                    rejection_log[status] = (
                        rejection_log.get(status, 0) + 1
                    )

    except FileNotFoundError:
        print(f"Error: file '{filepath}' was not found.")
        return [], {}

    return valid_records, rejection_log


# ============================================================
# 4. SECTOR-WISE AGGREGATION
# ============================================================

def aggregate_by_sector(records):
    """
    Build a multi-dimensional dictionary containing
    sector-wise statistics.
    """

    sector_stats = {}

    # Initialize all sectors
    for sector_name in SECTOR_LOOKUP.values():

        sector_stats[sector_name] = {
            "reading_count": 0,
            "total_load_kwh": 0.0,
            "peak_load_kwh": 0.0,
            "total_billing": 0.0,
            "avg_load_kwh": 0.0
        }

    # Process valid records
    for record in records:

        sector_name = record["sector"]
        stats = sector_stats[sector_name]

        stats["reading_count"] += 1

        stats["total_load_kwh"] += record["load_kwh"]

        stats["total_billing"] += (
            record["load_kwh"] * record["tariff_rate"]
        )

        if record["load_kwh"] > stats["peak_load_kwh"]:
            stats["peak_load_kwh"] = record["load_kwh"]

    # Calculate average
    for sector_name, stats in sector_stats.items():

        if stats["reading_count"] > 0:
            stats["avg_load_kwh"] = (
                stats["total_load_kwh"]
                / stats["reading_count"]
            )

    return sector_stats


# ============================================================
# 5. SURGE MULTIPLIER
# ============================================================

def compute_surge_multiplier(sector_name, avg_load_kwh):
    """
    Calculate the demand-surge penalty multiplier.

    If average load is within the threshold:
        multiplier = 1.0

    Otherwise:
        multiplier = 1 + excess_ratio

    Maximum multiplier = 2.5
    """

    threshold = SURGE_THRESHOLD_KWH[sector_name]

    if avg_load_kwh <= threshold:
        return 1.0

    excess_ratio = (
        (avg_load_kwh - threshold) / threshold
    )

    multiplier = 1.0 + excess_ratio

    return round(
        min(multiplier, MAX_PENALTY_MULTIPLIER),
        2
    )


# ============================================================
# 6. PRIORITY CLASSIFICATION
# ============================================================

def classify_priority(multiplier):
    """
    Convert the surge multiplier into an operational priority.
    """

    if multiplier >= 1.5:
        return "CRITICAL"

    elif multiplier > 1.0:
        return "ELEVATED"

    return "NORMAL"


# ============================================================
# 7. BALANCING OPERATIONS PLAN
# ============================================================

def generate_balancing_plan(sector_stats):
    """
    Generate a prioritized balancing plan.

    Sectors are sorted from highest to lowest multiplier.
    """

    plan = []

    for sector_name, stats in sector_stats.items():

        multiplier = compute_surge_multiplier(
            sector_name,
            stats["avg_load_kwh"]
        )

        priority = classify_priority(multiplier)

        # Select action according to priority
        if priority == "CRITICAL":

            action = (
                f"Trigger automatic load-shedding on "
                f"non-essential {sector_name} feeders and "
                f"dispatch reserve generation capacity immediately."
            )

        elif priority == "ELEVATED":

            action = (
                f"Apply dynamic tariff surcharge to "
                f"{sector_name} consumers and issue an early "
                f"demand-response advisory."
            )

        else:

            action = (
                f"Maintain standard distribution schedule "
                f"for {sector_name}."
            )

        plan.append({
            "sector": sector_name,
            "avg_load_kwh": round(
                stats["avg_load_kwh"], 2
            ),
            "threshold_kwh": SURGE_THRESHOLD_KWH[sector_name],
            "multiplier": multiplier,
            "priority": priority,
            "action": action
        })

    # Highest urgency first
    plan.sort(
        key=lambda entry: entry["multiplier"],
        reverse=True
    )

    return plan


# ============================================================
# 8. CONSOLE DASHBOARD
# ============================================================

def print_dashboard(
    sector_stats,
    plan,
    rejection_log,
    total_valid
):
    """
    Display the complete smart-grid analysis dashboard.
    """

    print("\n" + "=" * 75)

    print(
        "  SMART GRID MUNICIPAL ENERGY ANALYTICS"
    )

    print(
        "              PEAK LOAD DASHBOARD"
    )

    print("=" * 75)

    print(f"\nValid records processed     : {total_valid}")

    total_rejected = sum(
        rejection_log.values()
    )

    print(
        f"Corrupted records rejected : {total_rejected}"
    )

    if rejection_log:

        print("\nREJECTION SUMMARY")

        for reason, count in rejection_log.items():

            readable_reason = (
                reason
                .replace("_", " ")
                .title()
            )

            print(
                f"  - {readable_reason:<28}: {count}"
            )

    print("\n" + "-" * 75)

    print(
        f"{'SECTOR':<20}"
        f"{'READINGS':<10}"
        f"{'TOTAL kWh':<14}"
        f"{'AVG kWh':<12}"
        f"{'PEAK kWh':<12}"
    )

    print("-" * 75)

    for sector_name, stats in sector_stats.items():

        print(
            f"{sector_name:<20}"
            f"{stats['reading_count']:<10}"
            f"{stats['total_load_kwh']:<14.2f}"
            f"{stats['avg_load_kwh']:<12.2f}"
            f"{stats['peak_load_kwh']:<12.2f}"
        )

    print("\n" + "-" * 75)

    print(
        "PRIORITIZED BALANCING OPERATIONS PLAN"
    )

    print("-" * 75)

    for rank, entry in enumerate(plan, start=1):

        print(
            f"\n[{rank}] Sector      : "
            f"{entry['sector']}"
        )

        print(
            f"    Average Load : "
            f"{entry['avg_load_kwh']} kWh"
        )

        print(
            f"    Threshold    : "
            f"{entry['threshold_kwh']} kWh"
        )

        print(
            f"    Multiplier   : "
            f"x{entry['multiplier']}"
        )

        print(
            f"    Priority     : "
            f"{entry['priority']}"
        )

        print(
            f"    Action       : "
            f"{entry['action']}"
        )

    print("\n" + "=" * 75)


# ============================================================
# 9. EXPORT SUMMARY
# ============================================================

def export_summary(
    sector_stats,
    plan,
    rejection_log,
    total_valid,
    output_path
):
    """
    Export the complete analysis to a text file.
    """

    with open(output_path, "w") as out_file:

        out_file.write(
            "SMART GRID MUNICIPAL ENERGY ANALYTICS\n"
        )

        out_file.write(
            "        SUMMARY REPORT\n"
        )

        out_file.write(
            f"Generated: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        out_file.write("=" * 75 + "\n\n")

        out_file.write(
            f"Valid records processed     : {total_valid}\n"
        )

        total_rejected = sum(
            rejection_log.values()
        )

        out_file.write(
            f"Corrupted records rejected : {total_rejected}\n"
        )

        out_file.write("\nREJECTION SUMMARY\n")

        for reason, count in rejection_log.items():

            readable_reason = (
                reason
                .replace("_", " ")
                .title()
            )

            out_file.write(
                f"  - {readable_reason:<28}: {count}\n"
            )

        out_file.write(
            "\nSECTOR-WISE AGGREGATES\n"
        )

        out_file.write("-" * 75 + "\n")

        for sector_name, stats in sector_stats.items():

            out_file.write(
                f"\n{sector_name}\n"
            )

            out_file.write(
                f"    Readings      : "
                f"{stats['reading_count']}\n"
            )

            out_file.write(
                f"    Total Load    : "
                f"{stats['total_load_kwh']:.2f} kWh\n"
            )

            out_file.write(
                f"    Average Load  : "
                f"{stats['avg_load_kwh']:.2f} kWh\n"
            )

            out_file.write(
                f"    Peak Load     : "
                f"{stats['peak_load_kwh']:.2f} kWh\n"
            )

            out_file.write(
                f"    Total Billing : "
                f"Rs. {stats['total_billing']:.2f}\n"
            )

        out_file.write(
            "\nPRIORITIZED BALANCING OPERATIONS PLAN\n"
        )

        out_file.write("-" * 75 + "\n")

        for rank, entry in enumerate(plan, start=1):

            out_file.write(
                f"\n[{rank}] {entry['sector']} - "
                f"Priority: {entry['priority']}\n"
            )

            out_file.write(
                f"    Average Load: "
                f"{entry['avg_load_kwh']} kWh | "
                f"Threshold: "
                f"{entry['threshold_kwh']} kWh | "
                f"Multiplier: "
                f"x{entry['multiplier']}\n"
            )

            out_file.write(
                f"    Action: "
                f"{entry['action']}\n"
            )


# ============================================================
# 10. MAIN PROGRAM
# ============================================================

def main():

    print(
        "\nSmart Grid Municipal Energy Analytics "
        "and Peak Load Predictor"
    )

    print(
        "CSA0812 - Python Programming"
    )

    print(
        "Developed for Municipal Smart Grid Analysis\n"
    )

    default_path = "grid_log.txt"

    user_path = input(
        f"Enter path to telemetry log "
        f"[default: {default_path}]: "
    ).strip()

    filepath = (
        user_path
        if user_path
        else default_path
    )

    if not os.path.isfile(filepath):

        print(
            f"Error: file '{filepath}' not found."
        )

        return

    # Load and validate data
    valid_records, rejection_log = (
        load_telemetry(filepath)
    )

    # Aggregate valid data
    sector_stats = aggregate_by_sector(
        valid_records
    )

    # Generate balancing plan
    plan = generate_balancing_plan(
        sector_stats
    )

    # Display dashboard
    print_dashboard(
        sector_stats,
        plan,
        rejection_log,
        len(valid_records)
    )

    # Export result
    output_path = (
        "balancing_operations_summary.txt"
    )

    export_summary(
        sector_stats,
        plan,
        rejection_log,
        len(valid_records),
        output_path
    )

    print(
        f"\nBalancing operations summary "
        f"exported to: {output_path}"
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
