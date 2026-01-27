import sys
import os
from sqlalchemy import create_engine, text

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings

def migrate():
    print("🚀 Starting Migration: Campaigns and Posts Fields...")
    
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # --- CAMPAIGNS ---
        print("\nChecking table 'campaigns'...")
        result = conn.execute(text("PRAGMA table_info(campaigns)"))
        columns = [row[1] for row in result.fetchall()]
        
        new_columns_campaigns = {
            "identity_id": "VARCHAR", # UUID stored as string in SQLite usually or special type
        }
        
        for col_name, col_type in new_columns_campaigns.items():
            if col_name not in columns:
                print(f"➕ Adding column to campaigns: {col_name} ({col_type})")
                try:
                    conn.execute(text(f"ALTER TABLE campaigns ADD COLUMN {col_name} {col_type}"))
                    print(f"✅ Added {col_name}")
                except Exception as e:
                    print(f"❌ Error adding {col_name}: {e}")
            else:
                print(f"ℹ️ Column {col_name} already exists.")

        # --- POSTS ---
        print("\nChecking table 'posts'...")
        result = conn.execute(text("PRAGMA table_info(posts)"))
        columns = [row[1] for row in result.fetchall()]
        
        new_columns_posts = {
            "identity_id": "VARCHAR",
            "scheduled_for": "DATETIME",
            "cta": "VARCHAR",
            "hashtags": "VARCHAR"
        }
        
        for col_name, col_type in new_columns_posts.items():
            if col_name not in columns:
                print(f"➕ Adding column to posts: {col_name} ({col_type})")
                try:
                    conn.execute(text(f"ALTER TABLE posts ADD COLUMN {col_name} {col_type}"))
                    print(f"✅ Added {col_name}")
                except Exception as e:
                    print(f"❌ Error adding {col_name}: {e}")
            else:
                print(f"ℹ️ Column {col_name} already exists.")
                
        conn.commit()
        print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()
