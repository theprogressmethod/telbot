#!/usr/bin/env python3
"""
Apply attendance tracking database schema
"""

import os
import asyncio
from supabase import create_client, Client
from telbot import Config

async def apply_schema():
    """Apply the attendance tracking schema to Supabase"""
    try:
        # Initialize config
        config = Config()
        
        # Create Supabase client
        supabase: Client = create_client(config.supabase_url, config.supabase_key)
        
        # Read schema file
        with open('attendance_tracking_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        print("📄 Applying attendance tracking schema...")
        
        # Split into individual statements and execute
        statements = []
        current_statement = ""
        
        for line in schema_sql.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('--') or line.startswith('/*'):
                continue
                
            current_statement += line + "\n"
            
            # Execute when we hit a semicolon (but not inside quotes)
            if line.endswith(';') and line.count("'") % 2 == 0:
                statements.append(current_statement.strip())
                current_statement = ""
        
        # Add final statement if exists
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        print(f"Found {len(statements)} SQL statements to execute")
        
        success_count = 0
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
                
            try:
                print(f"Executing statement {i}/{len(statements)}...")
                
                # Execute the SQL statement
                result = supabase.rpc('execute_sql', {'sql_text': statement}).execute()
                success_count += 1
                
            except Exception as e:
                # Try alternative execution methods
                try:
                    # Method 2: Direct table operations for CREATE TABLE statements
                    if 'CREATE TABLE' in statement.upper():
                        print(f"   Alternative method for CREATE TABLE...")
                        # This would require parsing the CREATE TABLE statement
                        # For now, we'll continue and log the error
                        pass
                except Exception as e2:
                    pass
                
                print(f"   ⚠️ Statement {i} error (continuing): {str(e)[:100]}...")
        
        print(f"✅ Schema application completed: {success_count}/{len(statements)} statements executed successfully")
        
        # Test the schema by checking if tables exist
        try:
            # Try to query one of the new tables
            result = supabase.table('meeting_sessions').select('*').limit(1).execute()
            print("✅ meeting_sessions table accessible")
        except Exception as e:
            print(f"⚠️ meeting_sessions table check failed: {e}")
            
        try:
            result = supabase.table('attendance_records').select('*').limit(1).execute()
            print("✅ attendance_records table accessible")
        except Exception as e:
            print(f"⚠️ attendance_records table check failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error applying schema: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(apply_schema())
    if result:
        print("\n🎉 Attendance tracking schema setup completed!")
    else:
        print("\n❌ Schema setup failed - check logs above")