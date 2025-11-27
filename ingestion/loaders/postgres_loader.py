"""
PostgreSQL data loader
Loads CSV files into raw Postgres tables
"""

import pandas as pd
from pathlib import Path
from typing import List, Optional
import structlog
from sqlalchemy import text, inspect

from database.connection import db_manager

logger = structlog.get_logger()


class PostgresLoader:
    """Loads data from CSV files into Postgres raw tables"""
    
    def __init__(self):
        self.engine = db_manager.get_engine()
    
    def create_raw_tables(self):
        """Create raw layer tables if they don't exist"""
        logger.info("Creating raw layer tables")
        
        create_tables_sql = """
        -- Raw Patients Table
        CREATE TABLE IF NOT EXISTS raw_patients (
            patient_id VARCHAR(50) PRIMARY KEY,
            date_of_birth DATE,
            gender VARCHAR(1),
            zip_code VARCHAR(10),
            state VARCHAR(2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Raw Providers Table
        CREATE TABLE IF NOT EXISTS raw_providers (
            provider_id VARCHAR(50) PRIMARY KEY,
            npi VARCHAR(10),
            provider_name VARCHAR(255),
            provider_type VARCHAR(50),
            specialty VARCHAR(100),
            address VARCHAR(255),
            city VARCHAR(100),
            state VARCHAR(2),
            zip_code VARCHAR(10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Raw Claims Table
        CREATE TABLE IF NOT EXISTS raw_claims (
            claim_id VARCHAR(50) PRIMARY KEY,
            patient_id VARCHAR(50),
            provider_id VARCHAR(50),
            claim_date DATE,
            admission_date DATE,
            discharge_date DATE,
            claim_type VARCHAR(50),
            total_charge DECIMAL(12, 2),
            total_paid DECIMAL(12, 2),
            claim_status VARCHAR(50),
            denial_reason VARCHAR(100),
            primary_diagnosis_code VARCHAR(20),
            primary_procedure_code VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES raw_patients(patient_id),
            FOREIGN KEY (provider_id) REFERENCES raw_providers(provider_id)
        );
        
        -- Raw Notes Table
        CREATE TABLE IF NOT EXISTS raw_notes (
            note_id VARCHAR(50) PRIMARY KEY,
            claim_id VARCHAR(50),
            note_type VARCHAR(50),
            note_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (claim_id) REFERENCES raw_claims(claim_id)
        );
        
        -- Raw ICD-10 Lookup Table
        CREATE TABLE IF NOT EXISTS raw_icd10 (
            code VARCHAR(20) PRIMARY KEY,
            description TEXT,
            category VARCHAR(100),
            is_valid BOOLEAN DEFAULT TRUE
        );
        
        -- Raw CPT Lookup Table
        CREATE TABLE IF NOT EXISTS raw_cpt (
            code VARCHAR(20) PRIMARY KEY,
            description TEXT,
            category VARCHAR(100),
            is_valid BOOLEAN DEFAULT TRUE
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_claims_patient ON raw_claims(patient_id);
        CREATE INDEX IF NOT EXISTS idx_claims_provider ON raw_claims(provider_id);
        CREATE INDEX IF NOT EXISTS idx_claims_status ON raw_claims(claim_status);
        CREATE INDEX IF NOT EXISTS idx_notes_claim ON raw_notes(claim_id);
        """
        
        with self.engine.connect() as conn:
            conn.execute(text(create_tables_sql))
            conn.commit()
        
        logger.info("Raw layer tables created successfully")
    
    def load_csv_to_table(
        self,
        csv_path: Path,
        table_name: str,
        if_exists: str = "replace",
        chunk_size: int = 10000
    ) -> int:
        """
        Load CSV file into Postgres table
        
        Args:
            csv_path: Path to CSV file
            table_name: Target table name
            if_exists: What to do if table exists ('replace', 'append', 'fail')
            chunk_size: Number of rows to process at a time
            
        Returns:
            Number of rows loaded
        """
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        logger.info(f"Loading {csv_path.name} into {table_name}", if_exists=if_exists)
        
        total_rows = 0
        
        # Read CSV in chunks for large files
        for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
            chunk_rows = len(chunk)
            
            # Convert date columns
            date_columns = ['date_of_birth', 'claim_date', 'admission_date', 'discharge_date', 'created_at']
            for col in date_columns:
                if col in chunk.columns:
                    chunk[col] = pd.to_datetime(chunk[col], errors='coerce')
            
            # Load chunk to database
            chunk.to_sql(
                name=table_name,
                con=self.engine,
                if_exists=if_exists,
                index=False,
                method='multi'
            )
            
            total_rows += chunk_rows
            logger.debug(f"Loaded {chunk_rows} rows (total: {total_rows})")
            
            # After first chunk, append mode
            if_exists = "append"
        
        logger.info(f"Successfully loaded {total_rows} rows into {table_name}")
        return total_rows
    
    def load_all_raw_data(self, data_dir: Path = Path("data/raw")) -> dict:
        """
        Load all raw CSV files into database
        
        Args:
            data_dir: Directory containing CSV files
            
        Returns:
            Dictionary with load statistics
        """
        logger.info("Starting raw data ingestion", data_dir=str(data_dir))
        
        # Create tables first
        self.create_raw_tables()
        
        # Mapping of CSV files to table names
        file_mapping = {
            "raw_patients.csv": "raw_patients",
            "raw_providers.csv": "raw_providers",
            "raw_claims.csv": "raw_claims",
            "raw_notes.csv": "raw_notes",
            "raw_icd10.csv": "raw_icd10",
            "raw_cpt.csv": "raw_cpt",
        }
        
        results = {}
        
        for filename, table_name in file_mapping.items():
            csv_path = data_dir / filename
            
            if csv_path.exists():
                try:
                    rows_loaded = self.load_csv_to_table(csv_path, table_name, if_exists="replace")
                    results[table_name] = {
                        "status": "success",
                        "rows_loaded": rows_loaded
                    }
                except Exception as e:
                    logger.error(f"Failed to load {filename}", error=str(e))
                    results[table_name] = {
                        "status": "error",
                        "error": str(e)
                    }
            else:
                logger.warning(f"CSV file not found: {filename}")
                results[table_name] = {
                    "status": "skipped",
                    "reason": "file_not_found"
                }
        
        logger.info("Raw data ingestion completed", results=results)
        return results
    
    def verify_load(self) -> dict:
        """Verify data was loaded correctly"""
        logger.info("Verifying data load")
        
        tables = [
            "raw_patients",
            "raw_providers",
            "raw_claims",
            "raw_notes",
            "raw_icd10",
            "raw_cpt"
        ]
        
        verification = {}
        
        with self.engine.connect() as conn:
            for table in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                verification[table] = count
                logger.info(f"Table {table}: {count} rows")
        
        return verification


if __name__ == "__main__":
    # Test loader
    loader = PostgresLoader()
    results = loader.load_all_raw_data()
    print("\nLoad Results:")
    for table, result in results.items():
        print(f"  {table}: {result}")
    
    print("\nVerification:")
    verification = loader.verify_load()
    for table, count in verification.items():
        print(f"  {table}: {count} rows")

