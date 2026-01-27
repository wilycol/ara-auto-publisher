import sys
import os
from sqlalchemy import create_engine, text

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings

def check_schema():
    print("🚀 Checking Database Schema...")
    
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(functional_identities)"))
        columns = [row[1] for row in result.fetchall()]
        print(f"Columns in functional_identities: {columns}")

if __name__ == "__main__":
    check_schema()