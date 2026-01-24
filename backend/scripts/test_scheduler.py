import sys
import os
import time
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine
from app.models.domain import Post, Project, Campaign, ContentStatus, ConnectedAccount, Base
from app.services.scheduler import SchedulerService
from app.core.logging import logger

def setup_test_data(db):
    # 1. Project
    project = db.query(Project).filter(Project.name == "Scheduler Test Project").first()
    if not project:
        project = Project(name="Scheduler Test Project")
        db.add(project)
        db.commit()
        db.refresh(project)
        
    # 2. Connected Account (Fake)
    account = db.query(ConnectedAccount).filter(ConnectedAccount.project_id == project.id).first()
    if not account:
        account = ConnectedAccount(
            project_id=project.id,
            provider="linkedin",
            provider_name="Test LinkedIn User",
            external_account_id="urn:li:person:123",
            access_token_encrypted="fake_encrypted_token", # Mock adapter doesn't decrypt really
            active=True
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        
    # 3. Campaign
    campaign = db.query(Campaign).filter(Campaign.project_id == project.id).first()
    if not campaign:
        campaign = Campaign(project_id=project.id, name="Scheduler Campaign")
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
    return project, account, campaign

def create_post(db, project_id, campaign_id, scheduled_for, title="Test Post"):
    post = Post(
        project_id=project_id,
        campaign_id=campaign_id,
        title=title,
        content_text=f"Content for {title}",
        status=ContentStatus.APPROVED,
        scheduled_for=scheduled_for,
        platform="linkedin"
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def test_scheduler():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    scheduler = SchedulerService()
    
    print("\n🚀 Iniciando Test de Scheduler (Fase 2.3)...\n")
    
    try:
        project, account, campaign = setup_test_data(db)
        
        # CASO 1: Post Vencido (Debe publicarse)
        print("🔹 Caso 1: Post Vencido")
        past_date = datetime.utcnow() - timedelta(minutes=10)
        post_past = create_post(db, project.id, campaign.id, past_date, "Past Post")
        print(f"   Creado Post {post_past.id} | Scheduled: {post_past.scheduled_for} | Status: {post_past.status}")
        
        print("   >> Ejecutando Scheduler...")
        scheduler.run_cycle()
        
        db.refresh(post_past)
        print(f"   Resultado: Post {post_past.id} | Status: {post_past.status}")
        if post_past.status == ContentStatus.PUBLISHED:
            print("   ✅ ÉXITO: Post publicado.")
        else:
            print("   ❌ FALLO: Post no publicado.")
            
        # CASO 2: Post Futuro (Debe ignorarse)
        print("\n🔹 Caso 2: Post Futuro")
        future_date = datetime.utcnow() + timedelta(minutes=10)
        post_future = create_post(db, project.id, campaign.id, future_date, "Future Post")
        print(f"   Creado Post {post_future.id} | Scheduled: {post_future.scheduled_for} | Status: {post_future.status}")
        
        print("   >> Ejecutando Scheduler...")
        scheduler.run_cycle()
        
        db.refresh(post_future)
        print(f"   Resultado: Post {post_future.id} | Status: {post_future.status}")
        if post_future.status == ContentStatus.APPROVED:
            print("   ✅ ÉXITO: Post ignorado (sigue APPROVED).")
        else:
            print("   ❌ FALLO: Post modificado incorrectamente.")
            
        # CASO 3: Fallo Simulado (Sin cuenta)
        print("\n🔹 Caso 3: Fallo Simulado (Sin cuenta)")
        # Desactivar cuenta temporalmente
        account.active = False
        db.commit()
        
        post_fail = create_post(db, project.id, campaign.id, past_date, "Fail Post")
        print(f"   Creado Post {post_fail.id} | Status: {post_fail.status}")
        
        print("   >> Ejecutando Scheduler...")
        scheduler.run_cycle()
        
        db.refresh(post_fail)
        print(f"   Resultado: Post {post_fail.id} | Status: {post_fail.status}")
        if post_fail.status == ContentStatus.FAILED:
            print("   ✅ ÉXITO: Post marcado como FAILED.")
        else:
            print("   ❌ FALLO: Estado incorrecto.")
            
        # Restaurar cuenta
        account.active = True
        db.commit()

    except Exception as e:
        print(f"❌ Error fatal en test: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_scheduler()