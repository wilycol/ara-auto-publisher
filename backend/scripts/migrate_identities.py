import sys
import os
from sqlalchemy import create_engine, text, inspect

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)

def run_migration():
    print("🔄 Running Identity Migration (Safe Mode)...")
    inspector = inspect(engine)
    
    if "functional_identities" not in inspector.get_table_names():
        print("ℹ️ Table 'functional_identities' does not exist. It will be created by auto-migration on restart.")
        return

    columns = [c["name"] for c in inspector.get_columns("functional_identities")]
    print(f"Current columns: {columns}")
    
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            if "purpose" not in columns:
                connection.execute(text("ALTER TABLE functional_identities ADD COLUMN purpose VARCHAR"))
                print("✅ Added 'purpose'")
            
            if "preferred_platforms" not in columns:
                connection.execute(text("ALTER TABLE functional_identities ADD COLUMN preferred_platforms VARCHAR"))
                print("✅ Added 'preferred_platforms'")
                
            if "status" not in columns:
                connection.execute(text("ALTER TABLE functional_identities ADD COLUMN status VARCHAR DEFAULT 'active'"))
                print("✅ Added 'status'")
                
            if "project_id" not in columns:
                connection.execute(text("ALTER TABLE functional_identities ADD COLUMN project_id INTEGER REFERENCES projects(id)"))
                print("✅ Added 'project_id'")
                
            # Make role nullable if it exists
            if "role" in columns:
                connection.execute(text("ALTER TABLE functional_identities ALTER COLUMN role DROP NOT NULL"))
                print("✅ Made 'role' nullable")
                
            trans.commit()
            print("✅ Migration completed successfully.")
        except Exception as e:
            trans.rollback()
            print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    run_migration()
