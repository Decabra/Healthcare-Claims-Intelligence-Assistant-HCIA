"""
Script to ingest raw CSV data into Postgres
Run this to load generated data into database
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ingestion.loaders.postgres_loader import PostgresLoader
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer()
    ]
)

logger = structlog.get_logger()


def main():
    """Main ingestion function"""
    logger.info("Starting raw data ingestion")
    
    # Get data directory
    data_dir = project_root / "data" / "raw"
    
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        print(f"Error: Data directory not found: {data_dir}")
        print("Please run data generation first: python generate_data.py")
        sys.exit(1)
    
    # Initialize loader
    loader = PostgresLoader()
    
    try:
        # Load all raw data
        results = loader.load_all_raw_data(data_dir)
        
        # Print summary
        print("\n" + "=" * 60)
        print("Raw Data Ingestion Summary")
        print("=" * 60)
        
        for table, result in results.items():
            if result["status"] == "success":
                print(f"✓ {table}: {result['rows_loaded']} rows loaded")
            elif result["status"] == "error":
                print(f"✗ {table}: ERROR - {result.get('error', 'Unknown error')}")
            else:
                print(f"- {table}: SKIPPED - {result.get('reason', 'Unknown')}")
        
        # Verify load
        print("\n" + "=" * 60)
        print("Verification")
        print("=" * 60)
        verification = loader.verify_load()
        for table, count in verification.items():
            print(f"  {table}: {count:,} rows")
        
        print("\n✓ Raw data ingestion completed successfully!")
        
    except Exception as e:
        logger.error("Ingestion failed", error=str(e))
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

