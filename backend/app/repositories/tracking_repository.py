from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from app.models.tracking import ContentTracking

class TrackingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_entry(self, entry: ContentTracking) -> ContentTracking:
        """Crea un nuevo registro de tracking (Append-only)"""
        self.db.add(entry)
        try:
            self.db.commit()
            self.db.refresh(entry)
            return entry
        except Exception:
            self.db.rollback()
            raise

    def get_filtered(
        self, 
        project_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ContentTracking]:
        """Consulta filtrada para reportes"""
        query = self.db.query(ContentTracking)

        if project_id:
            query = query.filter(ContentTracking.project_id == project_id)
        
        if start_date:
            query = query.filter(ContentTracking.created_at >= start_date)
            
        if end_date:
            query = query.filter(ContentTracking.created_at <= end_date)

        return query.order_by(desc(ContentTracking.created_at)).limit(limit).all()

    def get_by_id(self, tracking_id: int) -> Optional[ContentTracking]:
        return self.db.query(ContentTracking).filter(ContentTracking.tracking_id == tracking_id).first()

    def get_version_history(self, content_id: int) -> List[ContentTracking]:
        """Obtiene historial completo de versiones de un contenido"""
        # Primero encontramos la raíz
        content = self.get_by_id(content_id)
        if not content:
            return []
        
        root_id = content.parent_content_id if content.parent_content_id else content.tracking_id
        
        # Si es un hijo, buscamos el padre para confirmar raíz (simplificación: asumimos 1 nivel o buscamos recursivo si fuera necesario)
        # La regla dice: parent_content_id apunta al padre.
        # Si queremos TODA la cadena, buscamos todos los que tengan mismo parent_content_id O sean el parent.
        
        # Implementación recursiva simple (asumiendo profundidad baja) o búsqueda por correlation_id si se usara para agrupar.
        # Pero aquí usaremos parent_content_id. 
        # Si asumimos estructura de árbol donde cada versión apunta a la anterior:
        # v3 -> v2 -> v1
        # Para obtener toda la lista, necesitamos recorrer.
        
        # O podemos buscar por correlation_id si es constante en versiones? 
        # El prompt dice "Correlation ID reusar si existe".
        # Si todas las versiones comparten correlation_id, es trivial.
        # Si no, tenemos que navegar los parents.
        
        # Asumiremos que el correlation_id SE MANTIENE a través de versiones (es lo lógico).
        if content.correlation_id:
             return self.db.query(ContentTracking)\
                 .filter(ContentTracking.correlation_id == content.correlation_id)\
                 .order_by(ContentTracking.version_number)\
                 .all()
        
        # Fallback: Solo devolver este item si no hay correlation_id
        return [content]

    def update_status(self, tracking_id: int, status: str, notes: str = None) -> Optional[ContentTracking]:
        """Actualiza campos humanos (estado, notas)"""
        entry = self.db.query(ContentTracking).filter(ContentTracking.tracking_id == tracking_id).first()
        if not entry:
            return None
        
        entry.status = status
        if notes:
            entry.notes = notes
        
        if status == "published" and not entry.published_at:
            entry.published_at = datetime.utcnow()
            
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def is_latest_version(self, content_id: int) -> bool:
        """Verifica si el contenido es la última versión de su linaje"""
        content = self.get_by_id(content_id)
        if not content:
            return False
            
        # Si no tiene correlation_id, es único (latest)
        if not content.correlation_id:
            return True
            
        # Buscar el max version_number para este correlation_id
        max_ver = self.db.query(ContentTracking.version_number)\
            .filter(ContentTracking.correlation_id == content.correlation_id)\
            .order_by(desc(ContentTracking.version_number))\
            .first()
            
        if not max_ver:
            return True
            
        return content.version_number == max_ver[0]
