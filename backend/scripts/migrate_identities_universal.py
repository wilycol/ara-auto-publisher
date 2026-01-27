import sys
import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import get_settings

def migrate():
    print("🚀 Starting MVP Final Migration for Identities (Universal)...")
    
    settings = get_settings()
    print(f"📡 Connecting to database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('functional_identities')]
        print(f"🧐 Existing columns: {columns}")
        
        # Add communication_style
        if 'communication_style' not in columns:
            print("➕ Adding column: communication_style")
            try:
                conn.execute(text("ALTER TABLE functional_identities ADD COLUMN communication_style TEXT"))
                conn.commit()
                print("✅ Added communication_style")
            except Exception as e:
                print(f"❌ Failed to add communication_style: {e}")
                conn.rollback()
        else:
            print("✅ Column communication_style already exists")

        # Add content_limits
        if 'content_limits' not in columns:
            print("➕ Adding column: content_limits")
            try:
                conn.execute(text("ALTER TABLE functional_identities ADD COLUMN content_limits TEXT"))
                conn.commit()
                print("✅ Added content_limits")
            except Exception as e:
                print(f"❌ Failed to add content_limits: {e}")
                conn.rollback()
        else:
            print("✅ Column content_limits already exists")

        # MVP PRO Fields
        pro_fields = [
            ('identity_type', 'TEXT'),
            ('campaign_objective', 'TEXT'),
            ('target_audience', 'TEXT'),
            ('language', 'TEXT'),
            ('preferred_cta', 'TEXT'),
            ('frequency', 'TEXT')
        ]

        for field_name, field_type in pro_fields:
            if field_name not in columns:
                print(f"➕ Adding column: {field_name}")
                try:
                    conn.execute(text(f"ALTER TABLE functional_identities ADD COLUMN {field_name} {field_type}"))
                    conn.commit()
                    print(f"✅ Added {field_name}")
                except Exception as e:
                    print(f"❌ Failed to add {field_name}: {e}")
                    conn.rollback()
            else:
                print(f"✅ Column {field_name} already exists")
            
    print("✅ Migration process completed.")

if __name__ == "__main__":
    migrate()
