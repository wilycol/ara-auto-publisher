import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from app.core.database import engine

def run_migration():
    print("Iniciando migración de identidad en campañas...")
    with engine.connect() as conn:
        dialect = engine.dialect.name
        print(f"Motor de base de datos detectado: {dialect}")
        
        try:
            if dialect == 'sqlite':
                conn.execute(text("ALTER TABLE campaigns ADD COLUMN identity_id CHAR(32)"))
            else:
                conn.execute(text("ALTER TABLE campaigns ADD COLUMN identity_id UUID"))
            print("✅ Columna 'identity_id' añadida a tabla 'campaigns'.")
        except Exception as e:
            print(f"ℹ️ Error o columna ya existe: {e}")

        conn.commit()
        print("Migración finalizada.")

if __name__ == "__main__":
    run_migration()
