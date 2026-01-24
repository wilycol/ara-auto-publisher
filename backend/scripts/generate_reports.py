import sys
import os
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from app.core.database import SessionLocal
from app.models.domain import Project, Campaign
from app.models.automation import CampaignAutomation, AutonomousDecisionLog
from app.models.optimization import OptimizationRecommendation
from app.models.tracking import ContentTracking

def generate_reports():
    print("📊 Generando reportes ejecutivos...")
    db = SessionLocal()
    
    output_dir = os.path.join(os.path.dirname(__file__), '../reports')
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # ==========================================
    # 1. REPORTE EJECUTIVO (Executive Summary)
    # ==========================================
    print("   1️⃣  Extrayendo datos de Campañas y Autonomía...")
    
    automations = db.query(CampaignAutomation).all()
    exec_data = []
    
    for auto in automations:
        project_name = "Unknown"
        project = db.query(Project).filter(Project.id == auto.project_id).first()
        if project:
            project_name = project.name
            
        # Stats
        decision_count = db.query(AutonomousDecisionLog).filter(AutonomousDecisionLog.automation_id == auto.id).count()
        rec_count = db.query(OptimizationRecommendation).filter(OptimizationRecommendation.automation_id == auto.id).count()
        
        exec_data.append({
            "ID Automatización": auto.id,
            "Proyecto": project_name,
            "Nombre Campaña": auto.name,
            "Estado": auto.status,
            "Estado Autonomía": auto.autonomy_status,
            "Manual Override": "SÍ" if auto.is_manually_overridden else "NO",
            "Última Ejecución": auto.last_run_at,
            "Próxima Ejecución": auto.next_run_at,
            "Total Decisiones Tomadas": decision_count,
            "Total Recomendaciones": rec_count
        })
        
    df_exec = pd.DataFrame(exec_data)
    exec_file = os.path.join(output_dir, f"reporte_ejecutivo_{timestamp}.xlsx")
    df_exec.to_excel(exec_file, index=False)
    print(f"      ✅ Guardado en: {exec_file}")
    
    # ==========================================
    # 2. REPORTE DE SEGUIMIENTO (URL Tracking)
    # ==========================================
    print("   2️⃣  Extrayendo historial de URLs generadas...")
    
    # Definir columnas explícitas para asegurar que aparezcan aunque no haya datos
    tracking_columns = [
        "Tracking ID", "Fecha Generación", "Proyecto", "Plataforma", 
        "Tipo Contenido", "Estado Actual", "URL Generada (Sistema)", "Objetivo",
        "Link Real (Publicado)", "Fecha Publicación", "Likes", "Comentarios", 
        "Shares", "Notas / Observaciones"
    ]

    contents = db.query(ContentTracking).order_by(ContentTracking.created_at.desc()).all()
    track_data = []
    
    for c in contents:
        track_data.append({
            "Tracking ID": c.tracking_id,
            "Fecha Generación": c.created_at,
            "Proyecto": c.project_name or f"Project {c.project_id}",
            "Plataforma": c.platform,
            "Tipo Contenido": c.content_type,
            "Estado Actual": c.status,
            "URL Generada (Sistema)": c.generated_url,
            "Objetivo": c.objective,
            # Columnas para llenado manual
            "Link Real (Publicado)": "",
            "Fecha Publicación": "",
            "Likes": "",
            "Comentarios": "",
            "Shares": "",
            "Notas / Observaciones": ""
        })
        
    if not track_data:
        # Si no hay datos, creamos el DataFrame solo con las columnas
        print("      ⚠️ No se encontraron registros de tracking. Generando plantilla vacía.")
        df_track = pd.DataFrame(columns=tracking_columns)
    else:
        df_track = pd.DataFrame(track_data)
        # Asegurar orden de columnas
        df_track = df_track[tracking_columns]
    
    track_file = os.path.join(output_dir, f"reporte_seguimiento_urls_{timestamp}.xlsx")
    
    # Ajustar ancho de columnas (básico con writer) - Opcional, pero pandas to_excel directo es más simple.
    # Usaremos simple export.
    df_track.to_excel(track_file, index=False)
    print(f"      ✅ Guardado en: {track_file}")
    
    db.close()
    print("\n✨ Proceso completado exitosamente.")
    print(f"📂 Ubicación: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    generate_reports()
