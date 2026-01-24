from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.domain import Post, ContentStatus, ConnectedAccount
from app.schemas.posts.post import PostRead, PostUpdate
from app.schemas.common.base import StandardResponse
from app.core.logging import logger
from app.services.publishers.linkedin import LinkedInPublisher
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=StandardResponse[List[PostRead]])
def list_posts(
    project_id: int = None, 
    status: str = None, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    query = db.query(Post)
    
    if project_id:
        query = query.filter(Post.project_id == project_id)
    if status:
        query = query.filter(Post.status == status)
        
    posts = query.order_by(Post.created_at.desc()).limit(limit).all()
    return StandardResponse(data=posts)

@router.put("/{post_id}", response_model=StandardResponse[PostRead])
def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un post existente.
    - Permite editar contenido solo si NO está APPROVED.
    - Para aprobar (status=APPROVED), DEBE tener fecha de programación (scheduled_for).
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Detectar si hay cambios de contenido
    content_fields = ["title", "content_text", "hashtags", "cta"]
    is_content_edit = any(
        getattr(post_update, field) is not None 
        for field in content_fields
    )
    
    current_status = db_post.status
    new_status = post_update.status or current_status
    
    # Regla: APPROVED es read-only para contenido
    # Si ya está aprobado, y se intenta editar contenido SIN volver a pending/rejected... error.
    if current_status == ContentStatus.APPROVED and is_content_edit:
        if new_status == ContentStatus.APPROVED:
             logger.warning(f"Intento de editar post aprobado {post_id} sin revertir estado")
             raise HTTPException(
                status_code=400, 
                detail="No se puede editar el contenido de un post APROBADO. Cámbielo a PENDING primero."
            )

    # Regla: Para aprobar, se requiere fecha
    if new_status == ContentStatus.APPROVED:
        final_scheduled_for = post_update.scheduled_for or db_post.scheduled_for
        if not final_scheduled_for:
            logger.warning(f"Intento de aprobar post {post_id} sin fecha programada")
            raise HTTPException(
                status_code=400, 
                detail="El post debe tener fecha de publicación antes de aprobarse"
            )

    # Aplicar cambios
    update_data = post_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_post, field, value)

    try:
        db.commit()
        db.refresh(db_post)
        logger.info(f"Post {post_id} actualizado. Status: {db_post.status}")
        return StandardResponse(data=db_post)
    except Exception as e:
        db.rollback()
        logger.error(f"Error actualizando post {post_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar post")

@router.post("/{post_id}/publish", response_model=StandardResponse[PostRead])
async def publish_post_now(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    Publica inmediatamente un post aprobado.
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    if db_post.status != ContentStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Solo se pueden publicar posts APROBADOS")
        
    # Obtener cuenta conectada (Mock logic: si no hay, creamos una dummy en memoria para el publisher)
    account = db.query(ConnectedAccount).filter(ConnectedAccount.project_id == db_post.project_id).first()
    
    # Para facilitar la demo, si no hay cuenta, usamos una fake
    if not account:
        logger.info("No connected account found. Using Mock Account for Demo.")
        account = ConnectedAccount(
            provider="linkedin", 
            provider_name="Demo Account",
            access_token_encrypted="mock_token"
        )
        
    publisher = LinkedInPublisher()
    try:
        logger.info(f"Publishing Post {post_id} to {account.provider_name}...")
        result = await publisher.publish(db_post, account)
        
        # Actualizar post
        db_post.status = ContentStatus.PUBLISHED
        db_post.published_at = datetime.utcnow()
        # db_post.external_id = result.get("external_id") # Si tuviera ese campo en modelo
        
        db.commit()
        db.refresh(db_post)
        return StandardResponse(data=db_post, message="Post publicado exitosamente")
        
    except Exception as e:
        logger.error(f"Error publicando post {post_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al publicar: {str(e)}")
