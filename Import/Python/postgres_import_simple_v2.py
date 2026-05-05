###############################################################################
# Usage:                                                                      #
# 1) Edit CONNECTION_STRING                                                   #
# 2) Place .csv.gz files in the same directory as this script or set working  #
#  directory to this folder                                                   #
# 3) Run the script. It will create tables with the same name as the files,   #
#    add primary keys, and create important indices.                          #
# Note: No other indices or constraints will be created, set as needed.       #
###############################################################################


import os
import glob
import io
import csv
import pandas as pd
import psycopg
from psycopg import sql

CONNECTION_STRING = "postgresql://postgres:password@localhost/sicdb" # change to correct connection string

# Tune these
READ_CHUNK_SIZE = 50_000     # pandas read chunk
# COPY doesn't use "insert_batch_size" (it streams), chunk size controls memory

IMPORTANT_INDICES = ["CaseID","PatientID","DataID","LaboratoryID","RefID","DrugID","Offset","FieldID"]


def pg_type_from_series(s: pd.Series) -> str:
    """Best-effort dtype mapping from pandas Series to PostgreSQL column type."""
    if pd.api.types.is_bool_dtype(s):
        return "BOOLEAN"
    if pd.api.types.is_integer_dtype(s):
        return "BIGINT"
    if pd.api.types.is_float_dtype(s):
        return "DOUBLE PRECISION"
    if pd.api.types.is_datetime64_any_dtype(s):
        return "TIMESTAMP"
    return "TEXT"


def quote_ident(name: str) -> sql.Identifier:
    return sql.Identifier(name)


def create_table(conn: psycopg.Connection, table_name: str, first_chunk: pd.DataFrame) -> None:
    cols = []
    for col in first_chunk.columns:
        col_type = pg_type_from_series(first_chunk[col])
        cols.append(sql.SQL("{} {}").format(quote_ident(col), sql.SQL(col_type)))

    q = sql.SQL("CREATE TABLE {} ({});").format(
        quote_ident(table_name),
        sql.SQL(", ").join(cols),
    )
    with conn.cursor() as cur:
        cur.execute(q)


def copy_dataframe(conn: psycopg.Connection, table_name: str, df: pd.DataFrame) -> int:
    """
    Stream a dataframe into PostgreSQL using COPY FROM STDIN (CSV).
    NaN/NaT are written as empty fields; COPY uses NULL '' so empty fields become NULL.
    """
    buf = io.StringIO()
    df.to_csv(
        buf,
        index=False,
        header=False,
        quoting=csv.QUOTE_MINIMAL,
        na_rep="",               # NaN -> empty
        lineterminator="\n",
    )
    buf.seek(0)

    columns_sql = sql.SQL(", ").join(quote_ident(c) for c in df.columns)

    copy_cmd = sql.SQL(
        "COPY {} ({}) FROM STDIN WITH (FORMAT CSV, NULL '')"
    ).format(quote_ident(table_name), columns_sql)

    with conn.cursor() as cur:
        with cur.copy(copy_cmd) as copy:
            copy.write(buf.getvalue())

    return len(df)


def add_pk_and_indexes(conn: psycopg.Connection, table_name: str, primary_key: str, all_columns: list[str]) -> None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL('ALTER TABLE {} ADD PRIMARY KEY ({});').format(
                quote_ident(table_name),
                quote_ident(primary_key),
            )
        )

        for col in IMPORTANT_INDICES:
            if col in all_columns and col != primary_key:
                cur.execute(
                    sql.SQL('CREATE INDEX ON {} ({});').format(
                        quote_ident(table_name),
                        quote_ident(col),
                    )
                )


def main() -> None:
    directory = os.path.dirname(os.path.realpath(__file__))
    files = glob.glob(os.path.join(directory, "*.csv.gz"))
    if not files:
        raise FileNotFoundError("No .csv.gz files found in directory.")

    # One connection for the whole run; commit per table
    with psycopg.connect(CONNECTION_STRING) as conn:
        # Optional: make bulk loads faster (and still safe enough for dev)
        # with conn.cursor() as cur:
        #     cur.execute("SET synchronous_commit TO OFF;")

        for filepath in files:
            table_name = os.path.basename(filepath).replace(".csv.gz", "")
            print(f"Loading {filepath} -> {table_name}", flush=True)

            rows_loaded = 0

            # NOTE: dtype_backend helps keep integer columns as integer even with nulls (pandas>=2.0)
            reader = pd.read_csv(
                filepath,
                compression="gzip",
                chunksize=READ_CHUNK_SIZE,
                low_memory=False,
                dtype_backend="numpy_nullable",
            )

            try:
                first = next(reader)
            except StopIteration:
                print(f"Skipping empty file: {filepath}", flush=True)
                continue

            if first.shape[1] == 0:
                print(f"Skipping no-column file: {filepath}", flush=True)
                continue

            primary_key = first.columns[0]
            all_columns = list(first.columns)

            # Drop + create table once
            with conn.cursor() as cur:
                cur.execute(sql.SQL("DROP TABLE IF EXISTS {};").format(quote_ident(table_name)))
            create_table(conn, table_name, first)
            conn.commit()

            # COPY first chunk + remaining chunks
            rows_loaded += copy_dataframe(conn, table_name, first)
            print(f"Loaded {rows_loaded} rows into {table_name}", flush=True)

            for chunk in reader:
                rows_loaded += copy_dataframe(conn, table_name, chunk)
                print(f"Loaded {rows_loaded} rows into {table_name}", flush=True)

            # Add PK + indexes after load
            add_pk_and_indexes(conn, table_name, primary_key, all_columns)
            conn.commit()

            print(f"Finished {table_name}: {rows_loaded} rows", flush=True)


if __name__ == "__main__":
    main()
