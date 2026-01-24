from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, List
from fastapi import HTTPException
from app.models.tracking import ContentTracking
from app.repositories.tracking_repository import TrackingRepository

class VersioningService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TrackingRepository(db)

    def create_version(self, content_id: int, changes: Dict[str, Any], change_reason: str) -> ContentTracking:
        """
        Crea una nueva versión a partir de un contenido existente.
        changes: Dict con campos a modificar (ej: {"notes": "new note", "generated_url": "new_url"})
        """
        original = self.repo.get_by_id(content_id)
        if not original:
            raise HTTPException(status_code=404, detail="Content not found")

        # Verificar si es la última versión para mantener secuencia limpia (opcional pero recomendado)
        # En este diseño, permitimos ramificar desde cualquier punto, pero el version_number
        # debería ser max(hermanos) + 1.
        # Si usamos correlation_id para agrupar versiones, buscamos el max version_number de ese grupo.
        
        current_versions = self.repo.get_version_history(content_id)
        max_version = max([v.version_number for v in current_versions]) if current_versions else original.version_number
        next_version_num = max_version + 1

        # POLÍTICA FASE 8.3: Versiones previas quedan automáticamente archived.
        # Marcamos la original como archived si no lo está ya.
        # Idealmente marcamos TODAS las previas, pero si seguimos el flujo lineal,
        # basta con marcar la que estamos versionando (si era la activa).
        if original.status != "archived":
            self.repo.update_status(original.tracking_id, "archived", notes="Archived due to new version creation")

        # Clonar objeto (manual copy para control explícito)
        new_version = ContentTracking(
            # Contexto (Inmutable)
            user_id=original.user_id,
            project_id=original.project_id,
            project_name=original.project_name,
            objective=original.objective,
            topic=original.topic,
            subtopic=original.subtopic,
            audience=original.audience,
            platform=original.platform,
            content_type=original.content_type,
            ai_agent=original.ai_agent,
            piece_count=original.piece_count,
            correlation_id=original.correlation_id, # MANTENER Correlation ID

            # Versionado
            parent_content_id=content_id, # Apunta al que originó esta versión
            version_number=next_version_num,
            change_reason=change_reason,
            created_at=datetime.utcnow(),

            # Campos Modificables (Override con changes)
            generated_url=changes.get("generated_url", original.generated_url),
            status=changes.get("status", "generated"), # Reset status a generated por defecto al versionar? O mantener?
            # Si se edita, suele volver a revisión.
            notes=changes.get("notes", original.notes),
            owner=changes.get("owner", original.owner)
        )

        return self.repo.create_entry(new_version)

    def get_versions(self, content_id: int) -> List[ContentTracking]:
        return self.repo.get_version_history(content_id)
