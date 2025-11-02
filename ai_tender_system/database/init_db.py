import os
import sqlite3
import logging

# Basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Initializes the database by creating tables from schema files.
    It reads the database path from the DATABASE_PATH environment variable.
    """
    # Get database path from environment variable. The .env file should be loaded by the calling process.
    db_path = os.getenv('DATABASE_PATH')
    
    if not db_path:
        logging.error("FATAL: DATABASE_PATH environment variable is not set.")
        logging.error("Please ensure you have a .env file in the project root and its variables are loaded.")
        return

    # Prevent re-initialization if the file already has data
    if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
        logging.info(f"Database at {db_path} already exists and is not empty. Initialization skipped.")
        return

    logging.info(f"Starting database initialization for: {db_path}")

    try:
        # Ensure the directory for the database file exists
        db_dir = os.path.dirname(db_path)
        os.makedirs(db_dir, exist_ok=True)
        
        # Connect to the database (this will create the file if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # The directory of this script is where the .sql files are located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # List of schema files to execute. Order matters.
        schema_files = [
            'knowledge_base_schema.sql',
            'case_library_schema.sql',
            'company_qualifications_schema.sql',
            'resume_library_schema.sql',
            'tender_processing_schema.sql',
            'tender_processing_hitl_schema.sql',
            'initial_data.sql'
        ]

        for schema_file in schema_files:
            schema_path = os.path.join(script_dir, schema_file)
            if not os.path.exists(schema_path):
                logging.warning(f"Schema file not found, skipping: {schema_path}")
                continue

            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
                logging.info(f"Executing: {schema_file}...")
                cursor.executescript(sql_script)

        conn.commit()
        logging.info("Database initialization complete. All schemas and initial data loaded.")

    except sqlite3.Error as e:
        logging.error(f"An error occurred during database initialization: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    main()
