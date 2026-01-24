import sys
import os
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import engine, SessionLocal

def migrate_v10():
    print("🔄 [Migration V10] Applying changes for Autonomy Phase...")
    
    with engine.connect() as conn:
        # 1. Add autonomy_status to campaign_automations
        try:
            print("   👉 Adding 'autonomy_status' column to 'campaign_automations'...")
            conn.execute(text("ALTER TABLE campaign_automations ADD COLUMN autonomy_status VARCHAR DEFAULT 'autonomous_active'"))
            conn.commit()
            print("   ✅ Column added.")
        except OperationalError as e:
            if "duplicate column name" in str(e):
                print("   ⚠️ Column 'autonomy_status' already exists. Skipping.")
            else:
                print(f"   ❌ Error adding column: {e}")

        # 2. Create autonomous_decision_logs table
        # Since Base.metadata.create_all() in the test script handles new tables, 
        # we strictly only need to handle the ALTER TABLE here. 
        # However, let's let the app or test script handle new table creation via create_all.
        pass

    print("✅ [Migration V10] Completed.")

if __name__ == "__main__":
    migrate_v10()
