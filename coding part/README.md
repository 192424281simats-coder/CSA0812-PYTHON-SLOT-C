# Smart Grid Municipal Energy Analytics System

## CSA0812 - Python Programming

### Project Title
Smart Grid Municipal Energy Analytics System and Peak Load Predictor

---

## 📌 Project Overview

This project develops a Python-based municipal smart-grid analytics system
for processing hourly electricity telemetry from three city sectors:

- Residential
- Commercial
- Heavy Industrial

The system validates raw telemetry, rejects corrupted records,
calculates sector-wise energy statistics, detects demand surges,
classifies operational priority, and generates a prioritized
balancing operations plan.

---

## 🎯 Objectives

1. Validate raw smart-grid telemetry.
2. Detect and reject corrupted records.
3. Calculate total energy consumption.
4. Calculate average hourly load.
5. Identify peak load.
6. Estimate sector-wise billing.
7. Calculate demand-surge multiplier.
8. Classify sectors as NORMAL, ELEVATED or CRITICAL.
9. Generate a prioritized balancing plan.
10. Export the final analysis as a text report.

---

## 🧠 Python Concepts Used

- Dictionaries
- Nested dictionaries
- String operations
- Lists
- Loops
- Conditional statements
- Functions
- File handling
- Exception handling
- Sorting
- Floating-point calculations
- Modular programming

---

## 🏗️ Program Architecture

The system follows a five-stage pipeline:

Raw Telemetry
      ↓
Validation & Filtering
      ↓
Sector Aggregation
      ↓
Surge Analysis
      ↓
Balancing Plan & Export

---

## 📂 Project Files

| File | Purpose |
|------|---------|
| `smart_grid_analytics.py` | Main Python application |
| `grid_log.txt` | Sample smart-grid telemetry |
| `balancing_operations_summary.txt` | Generated analysis report |
| `README.md` | Project documentation |

---

## ⚡ Sector Thresholds

| Sector | Safe Threshold |
|--------|----------------|
| Residential | 550 kWh |
| Commercial | 1600 kWh |
| Heavy Industrial | 3300 kWh |

---

## 🚦 Priority Classification

| Multiplier | Priority |
|------------|----------|
| 1.00 | NORMAL |
| > 1.00 and < 1.50 | ELEVATED |
| >= 1.50 | CRITICAL |

---

## 🧮 Surge Multiplier

If the average load is within the safe threshold:

`Multiplier = 1.0`

If the average load exceeds the threshold:

`Multiplier = 1 + ((Average Load - Threshold) / Threshold)`

The multiplier is capped at `2.5`.

---

## 🧪 Test Dataset

The supplied test dataset contains:

- 25 total records
- 19 valid records
- 6 corrupted records

The corrupted records include:

- Negative values
- Missing numeric field
- Unknown sector code
- Malformed field count
- Non-numeric value

---

## 📊 Expected Analysis

The system calculates:

- Total load
- Average load
- Peak load
- Total billing
- Surge multiplier
- Priority
- Recommended balancing action

The sectors are then ranked from highest to lowest urgency.

---

## ▶️ How to Run

Make sure Python 3 is installed.

Run:

```bash
python smart_grid_analytics.py
