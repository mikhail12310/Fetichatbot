import os
import pandas as pd
from sqlalchemy import create_engine
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_PATH = os.path.join(os.path.dirname(__file__), "database.sqlite")
engine = create_engine(f"sqlite:///{DB_PATH}")

def sanitize_table_name(filename):
    """Convert filename to a valid and clean SQL table name."""
    name, _ = os.path.splitext(filename)
    # Replace non-alphanumeric characters with underscores
    clean_name = re.sub(r'\W+', '_', name).strip('_')
    # Prepend 't_' if it starts with a number
    if clean_name[0].isdigit():
        clean_name = f"t_{clean_name}"
    return clean_name.lower()

import inspect
from sqlalchemy import inspect as sqla_inspect, text

def load_file_to_db(filepath, is_temp=False):
    """Load a single file into the SQLite database."""
    filename = os.path.basename(filepath)
    table_name = sanitize_table_name(filename)
    
    if is_temp:
        table_name = f"temp_{table_name}"
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filepath)
        elif filename.endswith('.parquet'):
            df = pd.read_parquet(filepath)
        else:
            print(f"Unsupported file format: {filename}")
            return False, f"Unsupported file format: {filename}"
            
        # Clean column names
        df.columns = [re.sub(r'\W+', '_', str(col)).strip('_').lower() for col in df.columns]
        
        # Write to SQLite
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Successfully loaded {filename} into table '{table_name}'")
        return True, f"Loaded {filename} into table '{table_name}'"
    except Exception as e:
        print(f"Error loading {filename}: {str(e)}")
        return False, str(e)

def rebuild_database(clean_temp=True):
    """Scan data directory and sync with DB. Only loads new/missing files."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    inspector = sqla_inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # 1. Identify which files should be in the DB
    data_files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f)) and not f.startswith('.')]
    required_tables = {sanitize_table_name(f): f for f in data_files}
    
    # 2. Cleanup: Drop tables that are not in data/ and are not persistent
    with engine.connect() as conn:
        for table in existing_tables:
            if table not in required_tables:
                # If it's a temp table or an old example table like 'employees'
                if clean_temp or table == "employees":
                    print(f"Cleaning up table: {table}")
                    conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    conn.commit()

    # 3. Load missing files from data/
    # Re-inspect after cleanup
    existing_tables = sqla_inspect(engine).get_table_names()
    for table_name, filename in required_tables.items():
        if table_name not in existing_tables:
            print(f"Table '{table_name}' missing. Loading from {filename}...")
            load_file_to_db(os.path.join(DATA_DIR, filename))
        else:
            print(f"Table '{table_name}' already exists. Skipping load.")

if __name__ == "__main__":
    print("Syncing database...")
    rebuild_database()
    print("Done.")
