import os
import sys
from sqlalchemy import create_engine, text, inspect

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)

def run_migration():
    print("Iniciando migración de columnas faltantes en tabla 'posts'...")
    
    with engine.connect() as conn:
        dialect = engine.dialect.name
        print(f"Motor de base de datos detectado: {dialect}")
        
        inspector = inspect(engine)
        columns = [c['name'] for c in inspector.get_columns('posts')]
        print(f"Columnas actuales: {columns}")
        
        # 1. ai_model
        if 'ai_model' not in columns:
            try:
                print("Añadiendo 'ai_model'...")
                conn.execute(text("ALTER TABLE posts ADD COLUMN ai_model VARCHAR"))
                print("✅ 'ai_model' añadida.")
            except Exception as e:
                print(f"❌ Error añadiendo 'ai_model': {e}")
        else:
            print("ℹ️ 'ai_model' ya existe.")

        # 2. generation_time_ms
        if 'generation_time_ms' not in columns:
            try:
                print("Añadiendo 'generation_time_ms'...")
                conn.execute(text("ALTER TABLE posts ADD COLUMN generation_time_ms INTEGER"))
                print("✅ 'generation_time_ms' añadida.")
            except Exception as e:
                print(f"❌ Error añadiendo 'generation_time_ms': {e}")
        else:
            print("ℹ️ 'generation_time_ms' ya existe.")

        # 3. tokens_used
        if 'tokens_used' not in columns:
            try:
                print("Añadiendo 'tokens_used'...")
                conn.execute(text("ALTER TABLE posts ADD COLUMN tokens_used INTEGER"))
                print("✅ 'tokens_used' añadida.")
            except Exception as e:
                print(f"❌ Error añadiendo 'tokens_used': {e}")
        else:
            print("ℹ️ 'tokens_used' ya existe.")

        # 4. identity_id
        if 'identity_id' not in columns:
            try:
                print("Añadiendo 'identity_id'...")
                if dialect == 'sqlite':
                    conn.execute(text("ALTER TABLE posts ADD COLUMN identity_id CHAR(32)"))
                else:
                    conn.execute(text("ALTER TABLE posts ADD COLUMN identity_id UUID"))
                print("✅ 'identity_id' añadida.")
            except Exception as e:
                print(f"❌ Error añadiendo 'identity_id': {e}")
        else:
            print("ℹ️ 'identity_id' ya existe.")
            
        conn.commit()
        print("Migración de posts finalizada.")

if __name__ == "__main__":
    run_migration()
