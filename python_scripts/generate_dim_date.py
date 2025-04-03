import pandas as pd
import datetime
import csv
import os

# --- Configuration ---
excel_file_path = 'bitre_fatal_crashes_dec2024.xlsx' # INPUT: Your Excel file name/path
sheet_name = 'BITRE_Fatal_Crash_Count_By_Date'      # INPUT: Sheet containing dates
date_column_name = 'Date'                             # INPUT: Column name with the full date
output_csv_file = 'dim_date_data.csv'                 # OUTPUT: Name for the date CSV
# --- End Configuration ---

print(f"Reading sheet '{sheet_name}' from '{excel_file_path}'...")

try:
    # *** Corrected line: Added header=2 ***
    # Tells pandas that the header row is the 3rd row (index 2)
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, header=2)
    # *************************************

    # Check if the date column exists *after* setting the correct header
    if date_column_name not in df.columns:
        print(f"Error: Column '{date_column_name}' not found in sheet '{sheet_name}' (using header row 3).")
        print(f"Detected columns are: {list(df.columns)}")
        # Clean up column names if they have leading/trailing spaces
        df.columns = df.columns.str.strip()
        if date_column_name not in df.columns:
             print(f"Still not found after stripping spaces. Please check the exact column name in row 3 of the Excel sheet.")
             exit()
        else:
             print(f"Found '{date_column_name}' after stripping whitespace from headers.")


    print(f"Parsing dates from column '{date_column_name}' using format 'D-Mon-YY'...")
    # Convert the date column using the specific format 'D-Mon-YY' (e.g., '1-Jan-89')
    df['parsed_date'] = pd.to_datetime(df[date_column_name], format='%d-%b-%y', errors='coerce')

    # Drop rows where date conversion failed
    rows_before = len(df)
    df.dropna(subset=['parsed_date'], inplace=True)
    rows_after = len(df)
    if rows_before > rows_after:
        print(f"Warning: Dropped {rows_before - rows_after} rows due to invalid date formats.")

    # Ensure dates are only date part (no time)
    df['parsed_date'] = df['parsed_date'].dt.date

    # Get unique dates from the successfully parsed dates
    unique_dates = sorted(df['parsed_date'].unique())
    print(f"Found {len(unique_dates)} unique dates after parsing.")

    if not unique_dates:
        print("Error: No valid dates found after parsing. Cannot generate dimension table.")
        exit()

    # Prepare data for CSV
    date_dimension_data = []
    header = [
        'full_date', 'year', 'month', 'day', 'month_name',
        'day_name', 'day_of_week_iso', 'is_weekday', 'quarter',
        'year_month_display', 'year_quarter_display'
    ]

    for dt_date in unique_dates:
        year = dt_date.year
        month = dt_date.month
        day = dt_date.day
        month_name = dt_date.strftime('%B')
        day_name = dt_date.strftime('%A')
        day_of_week_iso = dt_date.isoweekday() # Monday=1, Sunday=7
        is_weekday = day_of_week_iso < 6 # Monday to Friday
        quarter = (month - 1) // 3 + 1
        year_month_display = f"{year}-{month:02d}"
        year_quarter_display = f"{year}-Q{quarter}"

        date_dimension_data.append([
            dt_date.strftime('%Y-%m-%d'), # Format as YYYY-MM-DD string
            year,
            month,
            day,
            month_name,
            day_name,
            day_of_week_iso,
            is_weekday,
            quarter,
            year_month_display,
            year_quarter_display
        ])

    print(f"Writing data to '{output_csv_file}'...")
    # Write to CSV
    with open(output_csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(date_dimension_data)

    print("dim_date_data.csv generated successfully!")

except FileNotFoundError:
    print(f"Error: Input file '{excel_file_path}' not found.")
    print("Please make sure the file is in the same directory as the script or provide the full path.")
except ImportError:
     print("Error: pandas or openpyxl library not found. Please install using 'pip install pandas openpyxl'")
except Exception as e:
    print(f"An error occurred: {e}")