import pandas as pd
import datetime
import csv
import os

# --- Configuration ---
excel_file_path = 'bitre_fatal_crashes_dec2024.xlsx' # INPUT: Your Excel file name/path
sheet_name = 'BITRE_Fatal_Crash_Count_By_Date'      # INPUT: Sheet name
date_column_name = 'Date'                             # INPUT: Column name with the full date
crash_count_column_name = 'Number of fatal crashes'     # INPUT: Column name for crash count
output_csv_file = 'fact_daily_summary_data.csv'       # OUTPUT: Name for the fact CSV
# --- End Configuration ---

print(f"Reading sheet '{sheet_name}' from '{excel_file_path}'...")

try:
    # Read the Excel sheet, specifying the header row (3rd row, index 2)
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name, header=2)

    # --- Validate Columns ---
    required_columns = [date_column_name, crash_count_column_name]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing required columns in sheet '{sheet_name}' (using header row 3): {missing_cols}")
        print(f"Detected columns are: {list(df.columns)}")
        # Attempt to strip whitespace as headers might have extra spaces
        df.columns = df.columns.str.strip()
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
             print(f"Still missing after stripping spaces: {missing_cols}. Please check exact column names.")
             exit()
        else:
             print("Found columns after stripping whitespace.")


    print(f"Parsing dates from column '{date_column_name}' using format 'D-Mon-YY'...")
    # Convert the date column using the specific format 'D-Mon-YY'
    df['parsed_date'] = pd.to_datetime(df[date_column_name], format='%d-%b-%y', errors='coerce')

    # Convert crash count column to numeric, coercing errors to NaN
    df['crash_count_numeric'] = pd.to_numeric(df[crash_count_column_name], errors='coerce')

    # --- Data Cleaning & Selection ---
    # Keep only rows where both date and crash count are valid
    rows_before = len(df)
    df.dropna(subset=['parsed_date', 'crash_count_numeric'], inplace=True)
    rows_after = len(df)
    if rows_before > rows_after:
        print(f"Warning: Dropped {rows_before - rows_after} rows due to invalid dates or non-numeric crash counts.")

    if df.empty:
        print("Error: No valid data found after cleaning. Cannot generate fact file.")
        exit()

    # Ensure crash count is integer
    df['crash_count_numeric'] = df['crash_count_numeric'].astype(int)

    # Select and rename columns for the output CSV
    output_df = pd.DataFrame({
        'full_date': df['parsed_date'].dt.strftime('%Y-%m-%d'), # Format as YYYY-MM-DD
        'number_of_fatal_crashes': df['crash_count_numeric']
    })

    # --- Prepare CSV Output ---
    header = ['full_date', 'number_of_fatal_crashes'] # Header for the CSV file

    print(f"Writing data to '{output_csv_file}'...")
    # Write to CSV
    output_df.to_csv(output_csv_file, index=False, header=header, encoding='utf-8')

    print(f"{output_csv_file} generated successfully!")
    print("\nReminder: This CSV contains 'full_date'. During database import/ETL,")
    print("need to look up the corresponding 'date_sk' from 'dim_date'.")

except FileNotFoundError:
    print(f"Error: Input file '{excel_file_path}' not found.")
    print("Please make sure the file is in the same directory as the script or provide the full path.")
except ImportError:
     print("Error: pandas or openpyxl library not found. Please install using 'pip install pandas openpyxl'")
except Exception as e:
    print(f"An error occurred: {e}")