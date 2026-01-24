import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Optional
from datetime import datetime

from app.models.optimization import OptimizationRecommendation, RecommendationType, RecommendationStatus
from app.models.tracking import ContentTracking, ImpactMetric
from app.models.automation import CampaignAutomation
from app.services.impact_service import ImpactService

logger = logging.getLogger(__name__)

class PerformanceFeedbackService:
    """
    [Fase 9.2] Analiza métricas y genera recomendaciones.
    Cierra el ciclo de feedback (Feedback Loop).
    """

    def __init__(self, db: Session):
        self.db = db
        self.impact_service = ImpactService(db)

    def analyze_automation_performance(self, automation_id: int) -> List[OptimizationRecommendation]:
        """
        Punto de entrada principal. Analiza todo el contenido generado por una automatización.
        Genera recomendaciones y las guarda en DB.
        """
        automation = self.db.query(CampaignAutomation).filter(CampaignAutomation.id == automation_id).first()
        if not automation:
            logger.error(f"Automation {automation_id} not found")
            return []

        logger.info(f"🧠 [Feedback] Analyzing performance for Automation #{automation_id}")
        
        recommendations = []
        
        # 1. Analizar regresiones de versiones (Lineage Check)
        # Buscar contenidos generados por esta automatización (asumimos que podemos rastrearlos, 
        # aunque ContentTracking no tiene automation_id directo, usaremos project_id y quizás un tag o asumimos todo el proyecto por ahora para simplificar F9.2)
        # Idealmente ContentTracking debería tener automation_id, pero usaremos project_id.
        
        # Obtener todos los parent_content_ids únicos del proyecto
        # Esto puede ser costoso en prod, pero para MVP está bien.
        contents = self.db.query(ContentTracking).filter(
            ContentTracking.project_id == automation.project_id,
            ContentTracking.parent_content_id.is_(None) # Roots
        ).all()

        for root_content in contents:
            recs = self._analyze_content_lineage(root_content.tracking_id)
            recommendations.extend(recs)

        # 2. Analizar frecuencia global (Simple Mock Logic)
        # Si el CTR promedio de todo el proyecto es muy bajo, sugerir bajar frecuencia.
        # TODO: Implementar lógica global real.
        
        # Guardar recomendaciones
        saved_recs = []
        for rec_data in recommendations:
            saved_rec = self._save_recommendation(automation_id, rec_data)
            if saved_rec:
                saved_recs.append(saved_rec)
                
        return saved_recs

    def _analyze_content_lineage(self, root_content_id: int) -> List[Dict]:
        """Analiza la evolución de métricas entre versiones de un mismo contenido"""
        # Obtener todas las versiones ordenadas
        versions = self.db.query(ContentTracking).filter(
            (ContentTracking.tracking_id == root_content_id) | (ContentTracking.parent_content_id == root_content_id)
        ).order_by(ContentTracking.version_number.asc()).all()

        if len(versions) < 2:
            return [] # Nada que comparar

        recommendations = []
        
        # Comparar V_last con V_prev
        last_ver = versions[-1]
        prev_ver = versions[-2]
        
        # Obtener métricas agregadas
        metrics_last = self.impact_service.get_aggregated_metrics(last_ver.tracking_id)
        metrics_prev = self.impact_service.get_aggregated_metrics(prev_ver.tracking_id)
        
        # Calcular Scores (CTR weight 0.7, Engagement 0.3)
        score_last = self._calculate_score(metrics_last)
        score_prev = self._calculate_score(metrics_prev)
        
        if score_prev == 0:
            return [] # Evitar división por cero o datos insuficientes
            
        ratio = score_last / score_prev
        
        # Regla: Si cae más del 20% -> Regresión
        if ratio < 0.8:
            logger.warning(f"📉 [Feedback] Regression detected in Content {last_ver.tracking_id} (V{last_ver.version_number}) vs V{prev_ver.version_number}")
            recommendations.append({
                "type": RecommendationType.VERSION_ROLLBACK,
                "content_id": last_ver.tracking_id,
                "suggested_value": {"rollback_to_version": prev_ver.version_number},
                "reasoning": f"Performance dropped by {((1-ratio)*100):.1f}%. Score V{last_ver.version_number}: {score_last:.2f} vs V{prev_ver.version_number}: {score_prev:.2f}"
            })
            
        # Regla: Si mejora más del 20% -> Lock/Success
        elif ratio > 1.2:
            logger.info(f"📈 [Feedback] Improvement detected in Content {last_ver.tracking_id}")
            recommendations.append({
                "type": RecommendationType.STYLE_LOCK,
                "content_id": last_ver.tracking_id,
                "suggested_value": {"keep_elements": ["tone", "hashtags"]},
                "reasoning": f"Performance improved by {((ratio-1)*100):.1f}%. Winning formula."
            })
            
        return recommendations

    def _calculate_score(self, metrics: Dict) -> float:
        """Calcula un score normalizado de 0 a 100 (aprox)"""
        ctr = metrics.get("ctr", 0.0) # % (e.g. 1.5)
        engagement = metrics.get("engagement_rate", 0.0) # % (e.g. 0.5)
        
        # Peso arbitrario para MVP
        return (ctr * 0.7) + (engagement * 0.3)

    def _save_recommendation(self, automation_id: int, data: Dict) -> Optional[OptimizationRecommendation]:
        """Guarda la recomendación si no existe una pendiente similar"""
        # Evitar duplicados pendientes
        exists = self.db.query(OptimizationRecommendation).filter(
            OptimizationRecommendation.automation_id == automation_id,
            OptimizationRecommendation.content_id == data.get("content_id"),
            OptimizationRecommendation.type == data["type"],
            OptimizationRecommendation.status == RecommendationStatus.PENDING
        ).first()
        
        if exists:
            return None
            
        rec = OptimizationRecommendation(
            automation_id=automation_id,
            content_id=data.get("content_id"),
            type=data["type"],
            suggested_value=data["suggested_value"],
            reasoning=data["reasoning"],
            status=RecommendationStatus.PENDING
        )
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec
