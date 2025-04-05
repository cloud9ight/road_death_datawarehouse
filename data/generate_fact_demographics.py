import pandas as pd
import numpy as np
import os
import re

# --- Configuration ---
# Input Files (Assuming NO HEADERS in these files)
population_excel = 'population_2021.xlsx'
dwellings_csv = 'LGA (count of dwellings).csv' # This file's LGA name will be prioritized

# Output File
output_csv = 'lga_demographics_2021.csv' # New name

# Assign column names for files WITHOUT headers
pop_column_names = ['LGA_Name_Pop', 'Population_2021'] # Temp name for pop LGA
dwl_column_names = ['LGA_Name_Dwl', 'Dwelling_Count_2021'] # This name will be kept

# Output column names
out_lga_name = 'LGA_Name' # Final LGA name column (will use dwelling's name)
out_pop = 'Population_2021'
out_dwl = 'Dwelling_Count_2021'
# --- End Configuration ---

# --- Normalization Function ---
# ... (Normalization function remains the same) ...
def normalize_lga_name(series):
    """Cleans and normalizes LGA names for better matching."""
    if not isinstance(series, pd.Series):
        return series
    normalized = series.astype(str).str.lower().str.strip()
    normalized = normalized.str.replace(r'\s*\(\s*[a-z]+\s*\)\s*$', '', regex=True)
    suffixes_to_remove = [' regional', ' city', ' shire', ' council', ' borough', ' district', ' rural city']
    for suffix in sorted(suffixes_to_remove, key=len, reverse=True):
        normalized = normalized.str.replace(r'\s*' + re.escape(suffix.strip()) + r'$', '', regex=True)
    normalized = normalized.str.strip()
    normalized.replace('', np.nan, inplace=True)
    return normalized
# --- End Normalization Function ---

print("Starting demographic data merging process (Dwelling LGA name prioritized)...")

try:
    # 1. Read LGA (count of dwellings).csv (NO HEADER) - THIS IS NOW THE BASE
    print(f"Reading {dwellings_csv} (assuming NO header)...")
    if not os.path.exists(dwellings_csv):
        raise FileNotFoundError(f"Error: File not found - {dwellings_csv}")
    df_dwellings = pd.read_csv(dwellings_csv, header=None, names=dwl_column_names)
    print(f"  Read {len(df_dwellings)} raw rows from dwelling data.")

    # Filter out 'Total' rows from dwellings data
    original_dwl_rows = len(df_dwellings)
    lga_col_dwl = dwl_column_names[0]
    df_dwellings[lga_col_dwl] = df_dwellings[lga_col_dwl].astype(str)
    df_dwellings = df_dwellings[~df_dwellings[lga_col_dwl].str.contains("Total", case=False, na=False)]
    filtered_dwl_rows = len(df_dwellings)
    if original_dwl_rows > filtered_dwl_rows:
         print(f"  Filtered out {original_dwl_rows - filtered_dwl_rows} 'Total' row(s) from dwelling data.")

    # Clean original LGA name and normalize
    df_dwellings[lga_col_dwl] = df_dwellings[lga_col_dwl].str.strip()
    df_dwellings['LGA_Normalized'] = normalize_lga_name(df_dwellings[lga_col_dwl])
    # Convert dwelling count to numeric
    dwl_val_col_name = dwl_column_names[1]
    df_dwellings[out_dwl] = pd.to_numeric(df_dwellings[dwl_val_col_name], errors='coerce')
    # Drop rows if normalized LGA name is blank/NaN or dwelling count is invalid
    df_dwellings.dropna(subset=['LGA_Normalized', out_dwl], inplace=True)
    # Drop duplicates based on normalized name
    df_dwellings = df_dwellings.drop_duplicates(subset=['LGA_Normalized'], keep='first')
    print(f"  Processing {len(df_dwellings)} unique, valid LGAs from dwelling data (after filtering Total).")


    # 2. Read population_2021.xlsx (NO HEADER)
    print(f"Reading {population_excel} (assuming NO header)...")
    if not os.path.exists(population_excel):
        raise FileNotFoundError(f"Error: File not found - {population_excel}")
    df_population = pd.read_excel(population_excel, header=None, names=pop_column_names)
    print(f"  Read {len(df_population)} raw rows from population data.")

    # Filter out 'Total' rows from population data
    original_pop_rows = len(df_population)
    lga_col_pop = pop_column_names[0]
    df_population[lga_col_pop] = df_population[lga_col_pop].astype(str)
    df_population = df_population[~df_population[lga_col_pop].str.contains("Total", case=False, na=False)]
    filtered_pop_rows = len(df_population)
    if original_pop_rows > filtered_pop_rows:
        print(f"  Filtered out {original_pop_rows - filtered_pop_rows} 'Total' row(s) from population data.")

    # Clean original LGA name and normalize
    df_population[lga_col_pop] = df_population[lga_col_pop].str.strip()
    df_population['LGA_Normalized'] = normalize_lga_name(df_population[lga_col_pop])
    # Convert population to numeric
    pop_val_col_name = pop_column_names[1]
    df_population[out_pop] = pd.to_numeric(df_population[pop_val_col_name], errors='coerce')
    # Drop rows if normalized LGA name is blank/NaN or population is invalid
    df_population.dropna(subset=['LGA_Normalized', out_pop], inplace=True)
    # Drop duplicates based on normalized name
    df_population = df_population.drop_duplicates(subset=['LGA_Normalized'], keep='first')
    print(f"  Processing {len(df_population)} unique, valid LGAs from population data (after filtering Total).")


    # 3. Merge dataframes using LGA_Normalized (Dwelling is the LEFT table)
    print("Merging dataframes based on LGA_Normalized (starting with dwelling list)...")
    df_merged = pd.merge(
        # Start with dwelling data, keeping its original name and value
        df_dwellings[[dwl_column_names[0], 'LGA_Normalized', out_dwl]],
        # Select only normalized name and population value from population df
        df_population[['LGA_Normalized', out_pop]],
        on='LGA_Normalized', # Join key
        how='left'          # Keep all dwelling LGAs
    )
    print(f"  Merged dataframe has {len(df_merged)} rows.")


    # 4. Prepare final output
    # Select the desired columns: Original Dwelling LGA Name, Population, Dwelling count
    df_final = df_merged[[dwl_column_names[0], out_pop, out_dwl]].copy()
    # Rename the original dwelling LGA name column to the final output name 'LGA_Name'
    df_final.rename(columns={dwl_column_names[0]: out_lga_name}, inplace=True)

    # Convert numbers to nullable integers
    df_final[out_pop] = df_final[out_pop].astype(pd.Int64Dtype())
    df_final[out_dwl] = df_final[out_dwl].astype(pd.Int64Dtype())


    # 5. Write to output CSV
    print(f"Writing final data to {output_csv}...")
    # Header will be LGA_Name (from dwelling file), Population_2021, Dwelling_Count_2021
    df_final.to_csv(output_csv, index=False, encoding='utf-8')

    # ... (Rest of the print/success messages remain the same) ...
    print("-" * 30)
    print(f"Successfully created {output_csv}!")
    print(f"  Total rows: {len(df_final)}")
    print("\n--- First 5 rows of output ---")
    print(df_final.head())
    print("------------------------------")
    print("\n--- Missing Population Counts (if any) ---")
    missing_population = df_final[out_pop].isnull().sum()
    print(f"  Number of LGAs with dwelling data but missing population data: {missing_population}")
    print("-------------------------------------------")


except FileNotFoundError as e:
    print(e)
except ValueError as e:
    print(f"Configuration or Data Error: {e}")
except ImportError:
    print("Error: pandas or openpyxl library not found. Please install using 'pip install pandas openpyxl'")
except Exception as e:
    print(f"An unexpected error occurred: {e}")