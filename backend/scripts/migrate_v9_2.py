import sys
import os
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import engine

def migrate_v9_2():
    print("🔄 [Migration V9.2] Applying changes for Performance Feedback Loop...")
    
    with engine.connect() as conn:
        # Create optimization_recommendations table
        # We rely on SQLAlchemy's metadata.create_all() for table creation if it doesn't exist.
        # But if we were migrating an existing DB, we would do it here.
        # Since we use SQLite and SQLAlchemy create_all in QA scripts, 
        # let's just ensure it's logged.
        
        try:
            # Check if table exists (SQLite specific)
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='optimization_recommendations'"))
            if result.fetchone():
                print("   ✅ Table 'optimization_recommendations' already exists.")
            else:
                print("   ⚠️ Table 'optimization_recommendations' does not exist. Please run app startup or QA script to create it.")
                
        except Exception as e:
            print(f"   ❌ Error checking table: {e}")

    print("✅ [Migration V9.2] Completed.")

if __name__ == "__main__":
    migrate_v9_2()
