import sqlite3
import os

# Path to database (ROOT directory)
# __file__ = backend/scripts/migrate_v8_2.py
# dirname = backend/scripts
# .. = backend
# .. = root
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "ara_neuro_post.db")

def migrate():
    print(f"🔌 Connecting to database at {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print("⚠️  Database file not found. Skipping migration (will be created by app).")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get existing columns
        cursor.execute("PRAGMA table_info(content_tracking)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"📊 Existing columns: {columns}")
        
        # Add parent_content_id
        if "parent_content_id" not in columns:
            print("✨ Adding column 'parent_content_id'...")
            cursor.execute("ALTER TABLE content_tracking ADD COLUMN parent_content_id INTEGER DEFAULT NULL")
        else:
            print("✅ Column 'parent_content_id' already exists.")

        # Add version_number
        if "version_number" not in columns:
            print("✨ Adding column 'version_number'...")
            cursor.execute("ALTER TABLE content_tracking ADD COLUMN version_number INTEGER DEFAULT 1")
            # Update existing rows to have version 1
            cursor.execute("UPDATE content_tracking SET version_number = 1 WHERE version_number IS NULL")
        else:
            print("✅ Column 'version_number' already exists.")

        # Add change_reason
        if "change_reason" not in columns:
            print("✨ Adding column 'change_reason'...")
            cursor.execute("ALTER TABLE content_tracking ADD COLUMN change_reason VARCHAR DEFAULT NULL")
        else:
            print("✅ Column 'change_reason' already exists.")

        conn.commit()
        print("🚀 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
