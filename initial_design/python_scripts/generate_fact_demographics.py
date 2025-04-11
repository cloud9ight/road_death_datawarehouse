import pandas as pd
import numpy as np # Needed for NaN handling if using older pandas
import os

# --- Configuration ---
# Input Files
location_csv = 'dim_location.csv'
population_excel = 'population_2021.xlsx'
dwellings_csv = 'LGA (count of dwellings).csv'

# Output File
output_csv = 'fact_demographics_lga.csv'

# --- Column Names ---
# dim_location.csv columns
loc_id_col = 'Location_ID'
loc_lga_col = 'LGA_Name'

# Define column names for files WITHOUT headers (if applicable)
# Assuming population/dwelling files now have NO headers based on last message
pop_column_names = ['LGA_From_Pop', 'Population_Val']
dwl_column_names = ['LGA_From_Dwl', 'Dwelling_Val']

# Standardized name for unknown/blank LGAs
unknown_lga_value = "Unknown"

# Output column names
out_loc_id = 'Location_ID'
out_lga_name = 'LGA_Name'
out_pop = 'Population_2021'
out_dwl = 'Dwelling_Count_2021'
# --- End Configuration ---

print("Starting demographic data merging process...")

try:
    # 1. Read dim_location.csv
    print(f"Reading {location_csv}...")
    if not os.path.exists(location_csv):
        raise FileNotFoundError(f"Error: File not found - {location_csv}")
    df_location = pd.read_csv(location_csv)
    print(f"  Columns found: {list(df_location.columns)}")
    if loc_id_col not in df_location.columns or loc_lga_col not in df_location.columns:
        raise ValueError(f"Required columns ('{loc_id_col}', '{loc_lga_col}') not found in {location_csv}.")

    # --- Standardize LGA Name and identify original unknowns ---
    df_location_cleaned = df_location[[loc_id_col, loc_lga_col]].copy()
    # Strip whitespace first
    df_location_cleaned['LGA_Clean'] = df_location_cleaned[loc_lga_col].str.strip()
    # Record which ones were originally blank or NaN before filling
    df_location_cleaned['Is_Unknown_Orig'] = df_location_cleaned['LGA_Clean'].replace('', np.nan).isnull()
    # Fill NaN/blanks with the standard unknown value for merging purposes
    df_location_cleaned['LGA_Clean'].fillna(unknown_lga_value, inplace=True)
    df_location_cleaned['LGA_Clean'].replace('', unknown_lga_value, inplace=True) # Catch empty strings too
    # ---------------------------------------------------------
    print(f"  Read {len(df_location_cleaned)} rows from location data.")

    # 2. Read population_2021.xlsx (NO HEADER)
    print(f"Reading {population_excel} (assuming NO header row)...")
    if not os.path.exists(population_excel):
        raise FileNotFoundError(f"Error: File not found - {population_excel}")
    df_population = pd.read_excel(population_excel, header=None, names=pop_column_names)
    print(f"  Columns assigned: {list(df_population.columns)}")
    df_population.rename(columns={pop_column_names[0]: 'LGA_Clean', pop_column_names[1]: out_pop}, inplace=True)
    df_population['LGA_Clean'] = df_population['LGA_Clean'].str.strip()
    # Also standardize unknowns in population data if needed, though less critical for left merge
    df_population['LGA_Clean'].fillna(unknown_lga_value, inplace=True)
    df_population['LGA_Clean'].replace('', unknown_lga_value, inplace=True)
    df_population[out_pop] = pd.to_numeric(df_population[out_pop], errors='coerce')
    # Remove duplicates based on LGA_Clean before merge (keep first instance)
    df_population = df_population.drop_duplicates(subset=['LGA_Clean'], keep='first')
    print(f"  Read {len(df_population)} unique LGA rows from population data.")


    # 3. Read LGA (count of dwellings).csv (NO HEADER)
    print(f"Reading {dwellings_csv} (assuming NO header row)...")
    if not os.path.exists(dwellings_csv):
        raise FileNotFoundError(f"Error: File not found - {dwellings_csv}")
    df_dwellings = pd.read_csv(dwellings_csv, header=None, names=dwl_column_names)
    print(f"  Columns assigned: {list(df_dwellings.columns)}")
    df_dwellings.rename(columns={dwl_column_names[0]: 'LGA_Clean', dwl_column_names[1]: out_dwl}, inplace=True)
    df_dwellings['LGA_Clean'] = df_dwellings['LGA_Clean'].str.strip()
    # Also standardize unknowns in dwelling data
    df_dwellings['LGA_Clean'].fillna(unknown_lga_value, inplace=True)
    df_dwellings['LGA_Clean'].replace('', unknown_lga_value, inplace=True)
    df_dwellings[out_dwl] = pd.to_numeric(df_dwellings[out_dwl], errors='coerce')
    # Remove duplicates based on LGA_Clean before merge
    df_dwellings = df_dwellings.drop_duplicates(subset=['LGA_Clean'], keep='first')
    print(f"  Read {len(df_dwellings)} unique LGA rows from dwelling data.")


    # 4. Merge dataframes using the cleaned LGA name
    print("Merging dataframes...")
    df_merged = pd.merge(df_location_cleaned, df_population, on='LGA_Clean', how='left')
    df_merged = pd.merge(df_merged, df_dwellings, on='LGA_Clean', how='left')
    print(f"  Merged dataframe has {len(df_merged)} rows.")

    # --- 5. Correct values for originally unknown LGAs ---
    # Where the original LGA was blank/NaN, set pop and dwelling to NaN explicitly
    # This prevents picking up data if population/dwelling files had an "Unknown" row
    unknown_mask = df_merged['Is_Unknown_Orig'] == True
    df_merged.loc[unknown_mask, out_pop] = np.nan
    df_merged.loc[unknown_mask, out_dwl] = np.nan
    print(f"  Corrected values for {unknown_mask.sum()} originally unknown LGA rows.")
    # ------------------------------------------------------

    # 6. Prepare final output
    # Use the *original* LGA name for the output column
    df_final = df_merged[[loc_id_col, loc_lga_col, out_pop, out_dwl]].copy()
    # Rename columns for final output CSV
    df_final.rename(columns={loc_id_col: out_loc_id, loc_lga_col: out_lga_name}, inplace=True)

    # Convert pop/dwelling columns to nullable integers
    df_final[out_pop] = df_final[out_pop].astype(pd.Int64Dtype())
    df_final[out_dwl] = df_final[out_dwl].astype(pd.Int64Dtype())

    # 7. Write to output CSV
    print(f"Writing final data to {output_csv}...")
    df_final.to_csv(output_csv, index=False, encoding='utf-8')

    print("-" * 30)
    print(f"Successfully created {output_csv}!")
    print(f"  Total rows: {len(df_final)}")
    print("\n--- First 10 rows of output (including potential unknowns) ---")
    # Show more rows to potentially see an unknown one
    print(df_final.head(10))
    print("------------------------------------------------------------")
    print("\n--- Missing Value Counts ---")
    print(df_final.isnull().sum())
    print("----------------------------")


except FileNotFoundError as e:
    print(e)
except ValueError as e:
    print(f"Configuration or Data Error: {e}")
except ImportError:
    print("Error: pandas or openpyxl library not found. Please install using 'pip install pandas openpyxl'")
except Exception as e:
    print(f"An unexpected error occurred: {e}")