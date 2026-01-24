import csv
import json
import io
import openpyxl
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.tracking_repository import TrackingRepository
from app.models.tracking import ContentTracking

class TrackingService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TrackingRepository(db)

    def record_generation(self, data: dict) -> ContentTracking:
        """
        Registra un nuevo contenido generado.
        Data debe coincidir con los campos de ContentTracking.
        """
        entry = ContentTracking(**data)
        return self.repo.create_entry(entry)

    def publish_content(self, content_id: int) -> ContentTracking:
        """
        Intenta publicar un contenido.
        Aplica política de versionado: Solo la última versión puede ser publicada.
        """
        if not self.repo.is_latest_version(content_id):
            raise ValueError(f"Content {content_id} is not the latest version. Cannot publish obsolete versions.")
            
        entry = self.repo.update_status(content_id, "published")
        if not entry:
            raise ValueError(f"Content {content_id} not found")
            
        return entry

    def get_report_data(
        self, 
        project_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[ContentTracking]:
        return self.repo.get_filtered(project_id, start_date, end_date, limit=1000)

    def export_data(self, format: str, project_id: int = None) -> (io.BytesIO, str):
        """
        Exporta datos en el formato solicitado.
        Retorna (buffer, filename).
        """
        data = self.get_report_data(project_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        if format == "json":
            return self._export_json(data), f"tracking_{timestamp}.json"
        elif format == "csv":
            return self._export_csv(data), f"tracking_{timestamp}.csv"
        elif format == "xlsx":
            return self._export_xlsx(data), f"tracking_{timestamp}.xlsx"
        else:
            raise ValueError(f"Format {format} not supported")

    def _to_dict(self, entry: ContentTracking) -> dict:
        """Helper para serializar"""
        return {
            "id": entry.tracking_id,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
            "project_name": entry.project_name,
            "platform": entry.platform,
            "type": entry.content_type,
            "url": entry.generated_url,
            "status": entry.status,
            "objective": entry.objective,
            "notes": entry.notes
        }

    def _export_json(self, data: List[ContentTracking]) -> io.BytesIO:
        output = [self._to_dict(item) for item in data]
        buffer = io.BytesIO()
        buffer.write(json.dumps(output, indent=2).encode('utf-8'))
        buffer.seek(0)
        return buffer

    def _export_csv(self, data: List[ContentTracking]) -> io.BytesIO:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        
        # Headers
        headers = ["ID", "Date", "Project", "Platform", "Type", "URL", "Status", "Objective", "Notes"]
        writer.writerow(headers)
        
        for item in data:
            writer.writerow([
                item.tracking_id,
                item.created_at,
                item.project_name,
                item.platform,
                item.content_type,
                item.generated_url,
                item.status,
                item.objective,
                item.notes
            ])
            
        byte_buffer = io.BytesIO()
        byte_buffer.write(buffer.getvalue().encode('utf-8-sig')) # BOM for Excel compat
        byte_buffer.seek(0)
        return byte_buffer

    def _export_xlsx(self, data: List[ContentTracking]) -> io.BytesIO:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Content Tracking"
        
        # Headers
        headers = ["ID", "Date", "Project", "Platform", "Type", "URL", "Status", "Objective", "Notes"]
        ws.append(headers)
        
        for item in data:
            ws.append([
                item.tracking_id,
                item.created_at,
                item.project_name,
                item.platform,
                item.content_type,
                item.generated_url,
                item.status,
                item.objective,
                item.notes
            ])
            
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
