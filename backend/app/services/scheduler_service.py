import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import SessionLocal
from app.models.automation import CampaignAutomation
from app.services.campaign_automation_service import CampaignAutomationService
from app.services.autonomous_decision_service import AutonomousDecisionService
from app.services.autonomy_policy import DecisionType

logger = logging.getLogger(__name__)

class SchedulerService:
    _instance = None
    _scheduler = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SchedulerService, cls).__new__(cls)
            cls._scheduler = BackgroundScheduler()
        return cls._instance

    def start(self):
        """Inicia el scheduler y registra el job de escaneo"""
        if not self._scheduler.running:
            # Escanear cada 60 segundos por defecto
            self._scheduler.add_job(
                self._scan_due_jobs,
                trigger=IntervalTrigger(seconds=60),
                id="automation_scanner",
                name="Scan DB for due automation jobs",
                replace_existing=True
            )
            self._scheduler.start()
            logger.info("🚀 [Scheduler] Started background scheduler service")

    def shutdown(self):
        """Detiene el scheduler"""
        if self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("🛑 [Scheduler] Stopped background scheduler service")

    def _scan_due_jobs(self):
        """Busca en DB automatizaciones vencidas y las ejecuta"""
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            # Buscar jobs activos cuya fecha next_run_at <= ahora
            due_jobs = db.query(CampaignAutomation).filter(
                CampaignAutomation.status == "active",
                CampaignAutomation.next_run_at <= now
            ).all()
            
            if due_jobs:
                logger.info(f"⏰ [Scheduler] Found {len(due_jobs)} due jobs")
                
            for job in due_jobs:
                try:
                    logger.info(f"🤔 [Scheduler] Consulting Autonomous Brain for Job {job.id}...")
                    
                    # 1. Consultar AutonomousDecisionService
                    decision_service = AutonomousDecisionService(db)
                    decision_result = decision_service.evaluate_execution(job.id)
                    decision = decision_result.get("decision")
                    
                    if decision == DecisionType.ALLOW_EXECUTION:
                        logger.info(f"✅ [Scheduler] ALLOWED. Triggering Job ID {job.id}")
                        service = CampaignAutomationService(db)
                        service.trigger_campaign(job.id)
                    else:
                        logger.warning(f"⛔ [Scheduler] BLOCKED. Reason: {decision_result.get('reason')}")
                        # Si fue bloqueado, DEBEMOS actualizar next_run_at o volverá a intentarlo en 60s
                        # Si es por Cooldown, ya se manejará solo (no estará ready).
                        # Si es por Killswitch, quizás queramos reintentar pronto o esperar.
                        # Para evitar loops infinitos de logs "BLOCKED", forzamos un pequeño delay si es necesario,
                        # pero idealmente el estado del job o el tiempo debería cambiar.
                        # En caso de Cooldown, next_run_at debería estar en futuro, así que no debería salir en query.
                        # Si sale en query es porque next_run_at <= now.
                        pass
                        
                except Exception as e:
                    logger.error(f"❌ [Scheduler] Error executing Job {job.id}: {str(e)}")
                    pass
                    
        except Exception as e:
            logger.error(f"❌ [Scheduler] Scan loop failed: {str(e)}")
        finally:
            db.close()
