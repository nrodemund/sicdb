
import pandas as pd
import sqlite3
import glob
import os

# SQLite database file path
database_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'your_database.db')  # Update this to your SQLite database path

# Directory where your .csv.gz files are located
directory = r'D:\Export\sicdb\sicdb'#os.path.dirname(os.path.realpath(__file__))  # Replace with your directory if not in same path

# Check if cases.csv.gz exists in the directory
if not glob.glob(f'{directory}/cases.csv.gz'):
    print("File cases.csv.gz not found in the directory.")
    exit()

# Size of each chunk (number of rows)
chunk_size = 5000  # Adjust based on your system's capabilities

# Loop through each .csv.gz file in the directory
for filepath in glob.glob(f'{directory}/*.csv.gz'):
    # Extract the file name without extension to use as table name
    table_name = os.path.basename(filepath).replace('.csv.gz', '')

    # Inform about the process starting for this file
    print(f"Starting to process {filepath} into {table_name}...")

    # Initialize a counter for chunks
    chunk_counter = 0

    try:
        # Establish a connection
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # This basic script does not handle interruptions, so we will delete the table if it exists
        cursor.execute(f'DROP TABLE IF EXISTS {table_name};')
        conn.commit()

        # Read and insert the CSV file in chunks
        for chunk in pd.read_csv(filepath, compression='gzip', chunksize=chunk_size):
            chunk.to_sql(name=table_name, con=conn, if_exists='append', index=False)

            chunk_counter += 1
            row_count = chunk_counter * chunk_size
            print(f"Processed chunk {chunk_counter} ({row_count} rows) for {table_name}")

        # After all chunks are processed, add indexes
        important_indices = ["CaseID", "PatientID", "DataID", "LaboratoryID", "RefID", "DrugID", "Offset", "FieldID"]
        for index in important_indices:
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{index}_{table_name} ON {table_name} ({index});')
                conn.commit()
                print(f"Index for {index} in {table_name} created.")
            except sqlite3.Error as e:
                print(f"An error occurred while creating index for {index}: {e}")

        print(f"Finished adding data and indexes to {table_name}")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure the connection is closed
        conn.close()

    print(f"Finished processing {filepath}.")