#!/usr/bin/env python3
"""
Run database migrations programmatically
"""

import os
import logging
from supabase import create_client
from dotenv import load_dotenv

# Load environment
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run database migrations"""
    try:
        # Read migrations file
        with open('database_migrations.sql', 'r') as f:
            migrations = f.read()
        
        # Split migrations into individual statements
        statements = [stmt.strip() for stmt in migrations.split(';') if stmt.strip()]
        
        # Initialize Supabase
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        logger.info(f"Running {len(statements)} migration statements...")
        
        for i, statement in enumerate(statements):
            if not statement or statement.startswith('--'):
                continue
                
            try:
                logger.info(f"Executing statement {i+1}...")
                # Use the RPC function to execute raw SQL
                result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                logger.info(f"  ✅ Statement {i+1} executed successfully")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"  ⚠️ Statement {i+1}: Already exists, skipping")
                else:
                    logger.error(f"  ❌ Statement {i+1} failed: {e}")
        
        logger.info("✅ Migrations completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    run_migrations()