
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, text
from app.core.config import get_settings

settings = get_settings()

def migrate_v13():
    """
    Fase 13: Agregar campos de error a CampaignAutomation para UX visibility.
    """
    print("🚀 Iniciando migración Fase 13 (UX/Error Visibility)...")
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # 1. Verificar si existe la columna last_error
        result = conn.execute(text("PRAGMA table_info(campaign_automations)"))
        columns = [row[1] for row in result.fetchall()]
        
        if "last_error" not in columns:
            print("   👉 Agregando columna 'last_error'...")
            conn.execute(text("ALTER TABLE campaign_automations ADD COLUMN last_error TEXT"))
        else:
            print("   ✅ Columna 'last_error' ya existe.")

        if "error_at" not in columns:
            print("   👉 Agregando columna 'error_at'...")
            conn.execute(text("ALTER TABLE campaign_automations ADD COLUMN error_at DATETIME"))
        else:
            print("   ✅ Columna 'error_at' ya existe.")
            
        print("✅ Migración Fase 13 completada con éxito.")

if __name__ == "__main__":
    migrate_v13()
