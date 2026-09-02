"""
File Handling Demo - Student CSV Processor
Reads student marks from a CSV file, calculates totals & averages,
determines pass/fail status, and writes the processed results
to a new output file.
"""
 
import csv
 
INPUT_FILE = "students.csv"
OUTPUT_FILE = "results.csv"
PASS_MARK = 40   # minimum average marks per subject to pass
 
 
def process_students(input_file, output_file):
    processed_records = []
 
    # ---- READ ----
    print(f"Opening '{input_file}' for reading...")
    with open(input_file, "r", newline="") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            name = row["Name"]
            roll = row["Roll No"]
            m1, m2, m3 = int(row["Marks1"]), int(row["Marks2"]), int(row["Marks3"])
 
            total = m1 + m2 + m3
            average = round(total / 3, 2)
            status = "PASS" if average >= PASS_MARK else "FAIL"
 
            processed_records.append({
                "Name": name,
                "Roll No": roll,
                "Total": total,
                "Average": average,
                "Status": status
            })
 
            print(f"Processed: {name:<15} Total={total:<4} Avg={average:<6} -> {status}")
 
    # ---- WRITE ----
    print(f"\nWriting processed results to '{output_file}'...")
    with open(output_file, "w", newline="") as outfile:
        fieldnames = ["Name", "Roll No", "Total", "Average", "Status"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_records)
 
    print("Done. Results file created successfully.")
    return processed_records
 
 
if __name__ == "__main__":
    records = process_students(INPUT_FILE, OUTPUT_FILE)
 
    passed = sum(1 for r in records if r["Status"] == "PASS")
    failed = len(records) - passed
 
    print("\n----- SUMMARY -----")
    print(f"Total Students : {len(records)}")
    print(f"Passed         : {passed}")
    print(f"Failed         : {failed}")
 
