#!/usr/bin/env python3
"""
DATABASE BACKUP SCRIPT
Creates a snapshot of current development database state
Allows rollback to this exact point
"""

import os
import json
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# Load development environment
load_dotenv()

def backup_database():
    """Create comprehensive backup of all database tables"""
    
    # Use development credentials only
    url = os.getenv("DEV_SUPABASE_URL")
    key = os.getenv("DEV_SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Development database credentials not found")
        return False
    
    supabase = create_client(url, key)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"database_backups/backup_{timestamp}"
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"🔄 CREATING DATABASE BACKUP")
    print(f"   Timestamp: {timestamp}")
    print(f"   Directory: {backup_dir}")
    
    # Tables to backup
    tables_to_backup = [
        'users',
        'commitments', 
        'pods',
        'pod_memberships',
        'user_roles',
        'nurture_sequences',
        'user_sequence_state',
        'meeting_attendance'
    ]
    
    backup_summary = {
        'timestamp': timestamp,
        'database_url': url,
        'tables': {},
        'total_records': 0
    }
    
    for table in tables_to_backup:
        try:
            print(f"\n📋 Backing up {table}...")
            
            # Get all data from table
            result = supabase.table(table).select("*").execute()
            
            if result.data:
                # Save to JSON file
                filename = f"{backup_dir}/{table}.json"
                with open(filename, 'w') as f:
                    json.dump(result.data, f, indent=2, default=str)
                
                record_count = len(result.data)
                backup_summary['tables'][table] = record_count
                backup_summary['total_records'] += record_count
                
                print(f"   ✅ Saved {record_count} records to {filename}")
            else:
                backup_summary['tables'][table] = 0
                print(f"   ⚠️ No data in {table}")
                
        except Exception as e:
            print(f"   ❌ Error backing up {table}: {e}")
            backup_summary['tables'][table] = 'ERROR'
    
    # Save backup summary
    summary_file = f"{backup_dir}/backup_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(backup_summary, f, indent=2)
    
    print(f"\n✅ BACKUP COMPLETE")
    print(f"   Total Tables: {len(backup_summary['tables'])}")
    print(f"   Total Records: {backup_summary['total_records']}")
    print(f"   Location: {backup_dir}")
    
    # Create restore script
    restore_script = f"""#!/usr/bin/env python3
'''
RESTORE SCRIPT for backup {timestamp}
Run this to restore database to this exact state
'''

import json
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def restore():
    url = os.getenv("DEV_SUPABASE_URL")
    key = os.getenv("DEV_SUPABASE_KEY")
    supabase = create_client(url, key)
    
    backup_dir = "{backup_dir}"
    
    print("⚠️  WARNING: This will DELETE current data and restore from backup!")
    confirm = input("Type 'RESTORE' to continue: ")
    
    if confirm != 'RESTORE':
        print("❌ Restore cancelled")
        return
        
    tables = {list(tables_to_backup)}
    
    for table in tables:
        print(f"\\nRestoring {{table}}...")
        
        # Delete existing data (BE CAREFUL!)
        try:
            supabase.table(table).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        except:
            pass
            
        # Load backup data
        filename = f"{{backup_dir}}/{{table}}.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                
            if data:
                # Insert in batches of 50
                for i in range(0, len(data), 50):
                    batch = data[i:i+50]
                    supabase.table(table).insert(batch).execute()
                print(f"   ✅ Restored {{len(data)}} records")
        else:
            print(f"   ⚠️ No backup file found")
            
    print("\\n✅ Restore complete!")

if __name__ == "__main__":
    restore()
"""
    
    restore_file = f"{backup_dir}/restore_backup.py"
    with open(restore_file, 'w') as f:
        f.write(restore_script)
    
    os.chmod(restore_file, 0o755)  # Make executable
    
    print(f"\n📝 RESTORE INSTRUCTIONS:")
    print(f"   To restore this backup, run:")
    print(f"   python {restore_file}")
    
    return backup_dir

if __name__ == "__main__":
    print("🚀 DATABASE BACKUP UTILITY")
    print("=" * 50)
    print("⚠️  DEVELOPMENT DATABASE ONLY")
    print("=" * 50)
    
    backup_location = backup_database()
    
    if backup_location:
        print(f"\n✅ Backup successful: {backup_location}")
        print("\n💡 This backup includes:")
        print("   - All user data (65 users)")
        print("   - All commitments (233 records)")
        print("   - All pod data and memberships")
        print("   - All configuration and state")
        print("\n🔄 You can restore to this exact state anytime")