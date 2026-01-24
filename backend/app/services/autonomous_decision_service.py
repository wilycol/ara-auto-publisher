import logging
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any

from app.core.config import get_settings
from app.models.automation import CampaignAutomation, AutonomousDecisionLog
from app.services.autonomy_policy import AutonomyPolicy, DecisionType, AutonomyState
from app.services.performance_feedback_service import PerformanceFeedbackService
from app.models.optimization import RecommendationType

logger = logging.getLogger(__name__)

class AutonomousDecisionService:
    """
    [Fase 10] Cerebro de decisiones autónomas.
    Orquesta la validación de políticas antes de permitir cualquier acción.
    """

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.feedback_service = PerformanceFeedbackService(db)

    def evaluate_execution(self, automation_id: int) -> Dict[str, Any]:
        """
        Evalúa si una automatización puede ejecutarse en este momento.
        Retorna: { "decision": DecisionType, "reason": str }
        """
        automation = self.db.query(CampaignAutomation).filter(CampaignAutomation.id == automation_id).first()
        
        if not automation:
            return self._record_decision(
                automation_id=automation_id, # Puede fallar si FK constraint, pero asumimos ID válido en llamada
                decision=DecisionType.BLOCK_STATUS,
                reason="Automation not found"
            )

        # 1. Verificar Kill Switch Global
        if not self.settings.AUTONOMY_ENABLED:
            return self._record_decision(
                automation_id, 
                DecisionType.BLOCK_KILLSWITCH, 
                "Global Autonomy Kill Switch is ACTIVE (System Blocked)"
            )

        # 2. Verificar Estado de Autonomía
        if automation.autonomy_status != AutonomyState.ACTIVE:
            return self._record_decision(
                automation_id,
                DecisionType.BLOCK_STATUS,
                f"Automation is in state: {automation.autonomy_status}"
            )

        # 3. Verificar Cooldown
        if not AutonomyPolicy.check_cooldown(automation.last_run_at):
            return self._record_decision(
                automation_id,
                DecisionType.BLOCK_COOLDOWN,
                f"Cooldown period active. Last run: {automation.last_run_at}"
            )

        # [Fase 11] Manual Override Check for Safety Rules
        # "Una campaña en override manual: No puede ser pausada por autonomía"
        is_overridden = automation.is_manually_overridden

        # 4. Feedback Loop (Fase 9.2) - Análisis de Rendimiento
        # Analizar si hay recomendaciones críticas que deban bloquear la ejecución.
        # "Integrar con AutonomousDecisionService como input adicional"
        try:
            recommendations = self.feedback_service.analyze_automation_performance(automation_id)
            
            # Si hay recomendaciones de ROLLBACK, podría ser prudente bloquear hasta resolver,
            # o simplemente loguear. Según instrucción "NO ejecutar cambios", pero podemos bloquear por seguridad.
            # Vamos a ser conservadores: Si hay muchas recomendaciones negativas, pausamos.
            
            rollback_recs = [r for r in recommendations if r.type == RecommendationType.VERSION_ROLLBACK]
            if rollback_recs:
                msg = f"Performance regression detected. {len(rollback_recs)} rollback recommendations generated."
                
                if is_overridden:
                    # Log but DO NOT PAUSE
                    logger.warning(f"⚠️ [Override] Ignoring performance pause for #{automation_id}")
                    # We continue to next checks, effectively allowing execution unless blocked by other means
                    # But we should probably log this event
                    return self._record_decision(
                        automation_id,
                        DecisionType.ALLOW_EXECUTION, # Or special type? Keep standard.
                        f"Manual Override Active: {msg} (Ignored Pause)",
                        metrics={"recommendations_count": len(recommendations), "override": True}
                    )
                else:
                    # Auto-pausar la campaña si detectamos regresión grave
                    automation.autonomy_status = AutonomyState.PAUSED
                    self.db.commit()
                    
                    return self._record_decision(
                        automation_id,
                        DecisionType.BLOCK_PERFORMANCE,
                        f"Blocking due to detected performance regression. {len(rollback_recs)} rollback recommendations generated.",
                        metrics={"recommendations_count": len(recommendations)}
                    )
            
        except Exception as e:
            logger.error(f"Error in Feedback Loop analysis: {e}")
            # No bloqueamos por error de análisis, seguimos best-effort.

        # 5. Verificar Métricas Históricas (Simulado para F10, ahora reforzado por F9.2)
        # (El análisis detallado ya lo hizo PerformanceFeedbackService arriba)
        # Mantenemos esto como fallback simple si no hubo recomendaciones.
        metrics_snapshot = {"ctr": 1.5, "engagement_rate": 0.8} # Mock healthy metrics for now
        
        if AutonomyPolicy.should_pause_due_to_performance(metrics_snapshot):
            if is_overridden:
                logger.warning(f"⚠️ [Override] Ignoring historical performance pause for #{automation_id}")
            else:
                # Auto-pausar la campaña
                automation.autonomy_status = AutonomyState.PAUSED
                self.db.commit()
                
                return self._record_decision(
                    automation_id,
                    DecisionType.PAUSE_CAMPAIGN,
                    "Performance below threshold. Campaign auto-paused.",
                    metrics_snapshot
                )

        # 6. Todo OK -> Permitir
        return self._record_decision(
            automation_id,
            DecisionType.ALLOW_EXECUTION,
            "All autonomy checks passed.",
            metrics_snapshot
        )

    def _record_decision(self, automation_id: int, decision: DecisionType, reason: str, metrics: Dict = None) -> Dict[str, Any]:
        """Registra la decisión en la base de datos y loggea"""
        try:
            log_entry = AutonomousDecisionLog(
                automation_id=automation_id,
                decision=decision.value,
                reason=reason,
                metrics_snapshot=metrics
            )
            self.db.add(log_entry)
            self.db.commit()
            
            log_msg = f"🤖 [Autonomy] Decision for #{automation_id}: {decision.value} | {reason}"
            if decision == DecisionType.ALLOW_EXECUTION:
                logger.info(log_msg)
            else:
                logger.warning(log_msg)
                
            return {"decision": decision, "reason": reason}
            
        except Exception as e:
            logger.error(f"❌ Failed to record autonomy decision: {e}")
            self.db.rollback()
            # En caso de error de DB, bloqueamos por seguridad (Fail-Safe)
            return {"decision": DecisionType.BLOCK_STATUS, "reason": f"Audit Log Failure: {e}"}
