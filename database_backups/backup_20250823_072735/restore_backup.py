#!/usr/bin/env python3
'''
RESTORE SCRIPT for backup 20250823_072735
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
    
    backup_dir = "database_backups/backup_20250823_072735"
    
    print("⚠️  WARNING: This will DELETE current data and restore from backup!")
    confirm = input("Type 'RESTORE' to continue: ")
    
    if confirm != 'RESTORE':
        print("❌ Restore cancelled")
        return
        
    tables = ['users', 'commitments', 'pods', 'pod_memberships', 'user_roles', 'nurture_sequences', 'user_sequence_state', 'meeting_attendance']
    
    for table in tables:
        print(f"\nRestoring {table}...")
        
        # Delete existing data (BE CAREFUL!)
        try:
            supabase.table(table).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        except:
            pass
            
        # Load backup data
        filename = f"{backup_dir}/{table}.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                
            if data:
                # Insert in batches of 50
                for i in range(0, len(data), 50):
                    batch = data[i:i+50]
                    supabase.table(table).insert(batch).execute()
                print(f"   ✅ Restored {len(data)} records")
        else:
            print(f"   ⚠️ No backup file found")
            
    print("\n✅ Restore complete!")

if __name__ == "__main__":
    restore()
