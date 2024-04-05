# Importing SICdb to a MySQL, PostgreSql or sqlite3

The scripts help importing SICdb into a relational DBMS. 

- These scripts are kept simple and do not allow for interruption

# Quick Start

- Place the script into the SICdb folder
- Install the used python libraries
- Change the connection string within the file
- Run

# Troubleshooting

## Lost Connection

If the connection is lost during the insert of data_float_h, reduce chunk_size

## Import stops at "processing data_float_h", but no process is shown

This issue occurs when data_float_h is already propagated and dropping it takes too much time. Drop the table manually and restart. You may need to restart the SQL server or stop the hanging subprocess.