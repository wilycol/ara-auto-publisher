import sys
import os
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import engine

def migrate_v11():
    print("🔄 [Migration V11] Applying changes for Human Control...")
    
    with engine.connect() as conn:
        # 1. Add columns to campaign_automations
        try:
            conn.execute(text("ALTER TABLE campaign_automations ADD COLUMN is_manually_overridden BOOLEAN DEFAULT 0"))
            print("   ✅ Added 'is_manually_overridden' to campaign_automations")
        except OperationalError:
            print("   ⚠️ Column 'is_manually_overridden' already exists or error.")

        try:
            conn.execute(text("ALTER TABLE campaign_automations ADD COLUMN override_reason TEXT"))
            print("   ✅ Added 'override_reason' to campaign_automations")
        except OperationalError:
            print("   ⚠️ Column 'override_reason' already exists.")

        try:
            conn.execute(text("ALTER TABLE campaign_automations ADD COLUMN style_locked BOOLEAN DEFAULT 0"))
            print("   ✅ Added 'style_locked' to campaign_automations")
        except OperationalError:
            print("   ⚠️ Column 'style_locked' already exists.")

        # 2. Add columns to optimization_recommendations
        try:
            conn.execute(text("ALTER TABLE optimization_recommendations ADD COLUMN handled_at DATETIME"))
            print("   ✅ Added 'handled_at' to optimization_recommendations")
        except OperationalError:
            print("   ⚠️ Column 'handled_at' already exists.")

        try:
            conn.execute(text("ALTER TABLE optimization_recommendations ADD COLUMN handled_by TEXT"))
            print("   ✅ Added 'handled_by' to optimization_recommendations")
        except OperationalError:
            print("   ⚠️ Column 'handled_by' already exists.")
            
        conn.commit()

    print("✅ [Migration V11] Completed.")

if __name__ == "__main__":
    migrate_v11()
