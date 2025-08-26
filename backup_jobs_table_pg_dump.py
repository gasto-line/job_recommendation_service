import subprocess
import os
from datetime import datetime
import zipfile

# Use the same database connection as your existing code
DB_PSW = os.getenv("DB_PSW")
if not DB_PSW:
    raise ValueError("Database password (DB_PSW) is not set in environment variables.")

def backup_jobs_table_pg_dump():
    """
    Uses pg_dump to create a proper PostgreSQL backup of the jobs table.
    Returns the backup filename.
    """
    try:
        # Create backups directory if it doesn't exist
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Generate timestamp for the backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"jobs_backup_{timestamp}.sql"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # More readable approach
        host = "aws-0-eu-west-3.pooler.supabase.com"
        username = "postgres.irutkdcynqycaveefmpe"
        
        cmd = [
            "pg_dump",
            f"--host={host}",
            "--port=5432",
            f"--username={username}",
            "--dbname=postgres",
            "--table=jobs",
            f"--file={backup_path}"
        ]
        
        # Set password via environment
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_PSW or ""
        
        # Run the pg_dump command
        result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        
        # Create a compressed version
        zip_filename = f"jobs_backup_{timestamp}.zip"
        zip_path = os.path.join(backup_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_path, backup_filename)
        
        # Remove the uncompressed SQL file to save space
        os.remove(backup_path)
        
        print(f"✅ PostgreSQL backup created successfully: {zip_path}")
        print(f"📊 Backup contains jobs table with proper data types")
        
        return zip_path
        
    except subprocess.CalledProcessError as e:
        print(f"❌ pg_dump failed: {e}")
        print(f"Error output: {e.stderr}")
        return None
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def restore_jobs_table_pg_dump(backup_path):
    """
    Restores jobs table from a pg_dump backup file.
    WARNING: This will replace existing data!
    """
    try:
        # Extract the backup
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            sql_filename = zipf.namelist()[0]
            zipf.extract(sql_filename, "temp_restore")
        
        # Restore path
        restore_path = os.path.join("temp_restore", sql_filename)
        
        # psql command to restore
        host = "aws-0-eu-west-3.pooler.supabase.com"
        username = "postgres.irutkdcynqycaveefmpe"
        
        cmd = [
            "psql",
            f"--host={host}",
            "--port=5432",
            f"--username={username}",
            "--dbname=postgres",
            f"--file={restore_path}"
        ]
        
        # Set password via environment
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_PSW or ""
        
        # Run the restore command
        result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        
        # Clean up temp file
        os.remove(restore_path)
        os.rmdir("temp_restore")
        
        print(f"✅ Restore completed successfully from: {backup_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ psql restore failed: {e}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"❌ Restore failed: {e}")

if __name__ == "__main__":
    # Create a backup
    backup_file = backup_jobs_table_pg_dump()
    
    if backup_file:
        print(f"\n💾 Backup saved to: {backup_file}")
        print("🔧 To restore, use: restore_jobs_table_pg_dump('path_to_backup.zip')") 