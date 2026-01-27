
from sqlalchemy import create_engine, text
from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)

def check_latest_identity():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name, communication_style, content_limits FROM functional_identities ORDER BY created_at DESC LIMIT 1"))
        row = result.fetchone()
        if row:
            print(f"\n✅ LATEST IDENTITY FOUND:")
            print(f"ID: {row[0]}")
            print(f"Name: {row[1]}")
            print(f"Style: {row[2]}")
            print(f"Limits: {row[3]}")
            
            if row[2] and row[3]:
                print("\n🎉 PASS: Both 'communication_style' and 'content_limits' are present.")
            else:
                print("\n❌ FAIL: One or both new fields are empty.")
        else:
            print("\n❌ No identities found.")

if __name__ == "__main__":
    check_latest_identity()
