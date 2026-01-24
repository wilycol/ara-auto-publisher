from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.services.tracking_service import TrackingService

router = APIRouter()

@router.get("/")
def get_tracking_report(
    project_id: Optional[int] = None,
    format: Optional[str] = None, # json, csv, xlsx
    db: Session = Depends(get_db)
):
    """
    Obtiene reporte de tracking.
    Si se especifica 'format', descarga el archivo.
    Si no, devuelve JSON para frontend.
    """
    service = TrackingService(db)
    
    if format:
        buffer, filename = service.export_data(format, project_id)
        media_type = "application/json"
        if format == "csv": media_type = "text/csv"
        if format == "xlsx": media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        return StreamingResponse(
            buffer, 
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        # JSON standard response
        data = service.get_report_data(project_id)
        return {"count": len(data), "data": [service._to_dict(x) for x in data]}
