import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from app.core.database import engine

def run_migration():
    print("Iniciando migración manual de esquema...")
    with engine.connect() as conn:
        # Verificar si es SQLite o Postgres
        dialect = engine.dialect.name
        print(f"Motor de base de datos detectado: {dialect}")
        
        # 1. Añadir columna cta a posts
        try:
            if dialect == 'sqlite':
                conn.execute(text("ALTER TABLE posts ADD COLUMN cta TEXT"))
            else:
                conn.execute(text("ALTER TABLE posts ADD COLUMN cta TEXT"))
            print("✅ Columna 'cta' añadida a tabla 'posts'.")
        except Exception as e:
            print(f"ℹ️ Columna 'cta' ya existe o error: {e}")
            
        # 2. Añadir columna identity_id a posts
        try:
            if dialect == 'sqlite':
                # SQLite no tiene tipo UUID nativo, usa CHAR(32) o BLOB. SQLAlchemy suele usar CHAR(32) para UUID as_uuid=True
                conn.execute(text("ALTER TABLE posts ADD COLUMN identity_id CHAR(32)")) 
            else:
                conn.execute(text("ALTER TABLE posts ADD COLUMN identity_id UUID"))
            print("✅ Columna 'identity_id' añadida a tabla 'posts'.")
        except Exception as e:
            print(f"ℹ️ Columna 'identity_id' ya existe o error: {e}")

        conn.commit()
        print("Migración finalizada.")

if __name__ == "__main__":
    run_migration()
