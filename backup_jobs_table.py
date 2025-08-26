import pandas as pd
from sqlalchemy import create_engine, text
import os
from datetime import datetime
import zipfile

# Use the same database connection as your existing code
DB_PSW = os.getenv("DB_PSW")
if not DB_PSW:
    raise ValueError("Database password (DB_PSW) is not set in environment variables.")

SUPABASE_DB_URL = (
    "postgresql://postgres.irutkdcynqycaveefmpe:" + DB_PSW + "@aws-0-eu-west-3.pooler.supabase.com:5432/postgres"
)

engine = create_engine(SUPABASE_DB_URL, pool_pre_ping=True)

def backup_jobs_table():
    """
    Creates a timestamped backup of the jobs table.
    Returns the backup filename.
    """
    try:
        # Create backups directory if it doesn't exist
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Generate timestamp for the backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"jobs_backup_{timestamp}.csv"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Extract all data from jobs table
        with engine.connect() as conn:
            query = text("SELECT * FROM jobs ORDER BY retrieved_date DESC")
            jobs_df = pd.read_sql(query, conn)
        
        # Save to CSV
        jobs_df.to_csv(backup_path, index=False)
        
        # Create a compressed version
        zip_filename = f"jobs_backup_{timestamp}.zip"
        zip_path = os.path.join(backup_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_path, backup_filename)
        
        # Remove the uncompressed CSV file to save space
        os.remove(backup_path)
        
        print(f"✅ Backup created successfully: {zip_path}")
        print(f"📊 Total jobs backed up: {len(jobs_df)}")
        print(f"📅 Date range: {jobs_df['retrieved_date'].min()} to {jobs_df['retrieved_date'].max()}")
        
        return zip_path
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def restore_jobs_table(backup_path):
    """
    Restores jobs table from a backup file.
    WARNING: This will replace existing data!
    """
    try:
        # Extract the backup
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            csv_filename = zipf.namelist()[0]
            zipf.extract(csv_filename, "temp_restore")
        
        # Read the backup data
        restore_path = os.path.join("temp_restore", csv_filename)
        jobs_df = pd.read_csv(restore_path)
        
        # Clean up temp file
        os.remove(restore_path)
        os.rmdir("temp_restore")
        
        # Insert into database (replace existing data)
        with engine.begin() as conn:
            # Clear existing data
            conn.execute(text("DELETE FROM jobs"))
            
            # Insert backup data
            jobs_df.to_sql(
                "jobs",
                conn,
                if_exists="append",
                index=False,
                dtype={
                    'area_json': 'json',
                    'posted_date': 'date',
                    'retrieved_date': 'date',
                    'raw_payload': 'json',
                    'applied': 'boolean',
                }
            )
        
        print(f"✅ Restore completed successfully from: {backup_path}")
        print(f"📊 Total jobs restored: {len(jobs_df)}")
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")

if __name__ == "__main__":
    # Create a backup
    backup_file = backup_jobs_table()
    
    if backup_file:
        print(f"\n�� Backup saved to: {backup_file}")
        print("🔧 To restore, use: restore_jobs_table('path_to_backup.zip')") 