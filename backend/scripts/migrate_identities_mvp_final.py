import sys
import os
import sqlite3

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import get_settings

def migrate():
    print("🚀 Starting MVP Final Migration for Identities...")
    
    settings = get_settings()
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(functional_identities)")
        columns = [info[1] for info in cursor.fetchall()]
        
        # Add communication_style
        if 'communication_style' not in columns:
            print("➕ Adding column: communication_style")
            cursor.execute("ALTER TABLE functional_identities ADD COLUMN communication_style TEXT")
        else:
            print("✅ Column communication_style already exists")

        # Add content_limits
        if 'content_limits' not in columns:
            print("➕ Adding column: content_limits")
            cursor.execute("ALTER TABLE functional_identities ADD COLUMN content_limits TEXT")
        else:
            print("✅ Column content_limits already exists")
            
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
