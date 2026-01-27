import sys
import os
from sqlalchemy import create_engine, text

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings

def migrate():
    print("🚀 Starting Migration: FunctionalIdentity MVP PRO Fields...")
    
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if columns exist
        result = conn.execute(text("PRAGMA table_info(functional_identities)"))
        columns = [row[1] for row in result.fetchall()]
        
        # New fields to add:
        # identity_type (marca, persona, etc.)
        # campaign_objective (engagement, leads, etc.)
        # target_audience (text)
        # language (es, en)
        # preferred_cta (text)
        # frequency (low, medium, high)
        # MISSING FIELDS (Fix)
        # project_id, purpose, preferred_platforms, status
        
        new_columns = {
            "project_id": "INTEGER DEFAULT 1",
            "purpose": "VARCHAR",
            "preferred_platforms": "VARCHAR",
            "status": "VARCHAR DEFAULT 'active'",
            "identity_type": "VARCHAR",
            "campaign_objective": "VARCHAR",
            "target_audience": "TEXT",
            "language": "VARCHAR DEFAULT 'es'",
            "preferred_cta": "VARCHAR",
            "frequency": "VARCHAR DEFAULT 'medium'"
        }
        
        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                print(f"➕ Adding column: {col_name} ({col_type})")
                try:
                    conn.execute(text(f"ALTER TABLE functional_identities ADD COLUMN {col_name} {col_type}"))
                    print(f"✅ Added {col_name}")
                except Exception as e:
                    print(f"❌ Error adding {col_name}: {e}")
            else:
                print(f"ℹ️ Column {col_name} already exists.")
                
        conn.commit()
        print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()
