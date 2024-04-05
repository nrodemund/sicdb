import pandas as pd
from sqlalchemy import create_engine,text
from sqlalchemy.exc import SQLAlchemyError
import glob
import os

# MySQL database connection string
connection_string = 'mysql+mysqlconnector://your_user:your_password@localhost/your_database'

# Create the engine
engine = create_engine(connection_string)

# Directory where your .csv.gz files are located
directory = os.path.dirname(os.path.realpath(__file__)) # Replace with your directory if not in same path

# Check if cases.csv.gz exists in the directory
if not glob.glob(f'{directory}/cases.csv.gz'):
    print("File cases.csv.gz not found in the directory.")
    exit()

# Size of each chunk (number of rows)
chunk_size = 1000  # Adjust based on your system's capabilities

# Loop through each .csv.gz file in the directory
for filepath in glob.glob(f'{directory}/*.csv.gz'):
    # Extract the file name without extension to use as table name
    table_name = os.path.basename(filepath).replace('.csv.gz', '')
    
    # Inform about the process starting for this file
    print(f"Starting to process {filepath} into {table_name}...")
    
    # Initialize a counter for chunks
    chunk_counter = 0
    
    primary_key = None


    try:
      
        # Establish a connection
        conn = engine.connect()
        # Begin a transaction
        trans = conn.begin()

        # Read and insert the CSV file in chunks
        for chunk in pd.read_csv(filepath, compression='gzip', chunksize=chunk_size):
            if primary_key is None: 
                primary_key = chunk.columns[0]

                # This basic script does not handle interruptions, so we will delete the table if it exists
                
                conn.execute(text(f'DROP TABLE IF EXISTS {table_name};'))



            chunk.to_sql(name=table_name, con=conn, if_exists='append', index=False)
            chunk_counter += 1
            row_count=chunk_counter*chunk_size
            print(f"Processed chunk {chunk_counter} ({row_count} rows) for {table_name}")

        print(f"Finished adding data to {table_name}, setting primary key.")

        # SQL to alter the table and add a primary key
        alter_table_sql = text(f'ALTER TABLE {table_name} ADD PRIMARY KEY ({primary_key});')

    
        conn.execute(alter_table_sql)
        # Commit the transaction
        trans.commit()
    except SQLAlchemyError as e:
        # Roll back the transaction on error
        trans.rollback()
        print(f"An error occurred: {e}")
    finally:
        # Ensure the connection is closed
        conn.close()


    print(f"Finished processing {filepath}.")

