import csv
import datetime

# --- Configuration ---
start_year = 1989
end_year = 2024  # Inclusive
output_filename = 'dim_year_month.csv'
# --- End Configuration ---

header = [
    'year',
    'month',
    'month_name',
    'year_month_display',
    'quarter',
    'year_quarter_display'
]

print(f"Generating data for {start_year} to {end_year}...")

all_rows = []

# Loop through each year
for year in range(start_year, end_year + 1):
    # Loop through each month (1 to 12)
    for month in range(1, 13):
        # Calculate month_name using datetime
        # Create a dummy date object for the first day of the month
        try:
            first_day_of_month = datetime.date(year, month, 1)
            month_name = first_day_of_month.strftime('%B') # Gets full month name
        except ValueError:
            # This shouldn't happen with standard month ranges, but good practice
            month_name = "Invalid Month"

        # Format year_month_display (YYYY-MM with zero padding)
        year_month_display = f"{year}-{month:02d}"

        # Calculate quarter
        quarter = (month - 1) // 3 + 1

        # Format year_quarter_display (YYYY-Qn)
        year_quarter_display = f"{year}-Q{quarter}"

        # Append the row data as a list
        all_rows.append([
            year,
            month,
            month_name,
            year_month_display,
            quarter,
            year_quarter_display
        ])

print(f"Generated {len(all_rows)} rows. Writing to CSV file: {output_filename}")

# Write the data to a CSV file
try:
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write the header
        csv_writer.writerow(header)
        # Write all the data rows
        csv_writer.writerows(all_rows)
    print("CSV file generated successfully!")
except IOError as e:
    print(f"Error writing CSV file: {e}")