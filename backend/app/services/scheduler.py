from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import asyncio

from app.core.database import SessionLocal
from app.models.domain import Post, ContentStatus, ConnectedAccount
from app.core.logging import logger
from app.services.publishers.linkedin import LinkedInPublisher
from app.core.config import get_settings

settings = get_settings()

class SchedulerService:
    def __init__(self):
        self.publishers = {
            "linkedin": LinkedInPublisher()
        }
    
    def run_cycle(self):
        """
        Ejecuta un ciclo del scheduler:
        1. Busca posts APPROVED con fecha vencida.
        2. Intenta publicarlos.
        3. Actualiza estados.
        """
        db = SessionLocal()
        try:
            posts_to_publish = self._get_pending_posts(db)
            if posts_to_publish:
                logger.info(f"🔄 Ciclo Scheduler: {len(posts_to_publish)} posts encontrados para publicar.")
            
            for post in posts_to_publish:
                self._process_post(db, post)
                
        except Exception as e:
            logger.error(f"❌ Error crítico en ciclo del scheduler: {str(e)}")
        finally:
            db.close()
            
    def _get_pending_posts(self, db: Session) -> List[Post]:
        now = datetime.utcnow()
        return db.query(Post).filter(
            Post.status.in_([ContentStatus.APPROVED, ContentStatus.SCHEDULED_AUTO]),
            Post.scheduled_for <= now
        ).all()
        
    def _process_post(self, db: Session, post: Post):
        logger.info(f"⚙️ Procesando Post {post.id} | Proyecto {post.project_id} | Plataforma {post.platform}")
        
        # 0. Verificar Feature Flags
        platform = post.platform.lower()
        if platform == "linkedin" and not settings.FEATURE_LINKEDIN_ENABLED:
            logger.warning(f"⚠️  Post {post.id} omitido: LinkedIn desactivado por Feature Flag.")
            # Marcamos como FAILED para evitar bucle infinito, pero con log claro
            post.status = ContentStatus.FAILED_AUTO_MANUAL_AVAILABLE
            # Idealmente agregaríamos una nota de "Razón: Feature Flag disabled"
            db.commit()
            return
            
        # 1. Cambiar a PROCESSING
        post.status = ContentStatus.PROCESSING
        db.commit()
        
        try:
            # 2. Obtener adaptador
            adapter = self.publishers.get(platform)
            if not adapter:
                raise ValueError(f"No hay adaptador para plataforma: {post.platform}")
            
            # 3. Obtener cuenta conectada
            account = db.query(ConnectedAccount).filter(
                ConnectedAccount.project_id == post.project_id,
                ConnectedAccount.provider == platform,
                ConnectedAccount.active == True
            ).first()
            
            if not account:
                # Si no hay cuenta, pasamos a MODO MANUAL ASISTIDO
                # En lugar de fallar, marcamos como listo para publicar manualmente
                logger.info(f"ℹ️  Post {post.id}: No hay cuenta conectada. Cambiando a estado READY_MANUAL (Modo Manual Asistido).")
                post.status = ContentStatus.READY_MANUAL
                # Aquí se podría disparar una notificación (email/push) en el futuro
                db.commit()
                return

            # 4. Publicar (Delegar al adaptador)
            # Usamos el helper asyncio_run para ejecutar la corutina
            result = asyncio_run(adapter.publish(post, account))
            
            # 5. Actualizar a PUBLISHED
            post.status = ContentStatus.PUBLISHED_AUTO
            post.published_at = datetime.utcnow()
            # Si tuviéramos campo metadata, guardaríamos result['external_id']
            
            logger.info(f"✅ Post {post.id} publicado correctamente.")
            
        except Exception as e:
            logger.error(f"❌ Fallo al publicar Post {post.id}: {str(e)}")
            post.status = ContentStatus.FAILED_AUTO_MANUAL_AVAILABLE
            # Podríamos guardar el error en una columna error_message si existiera
            
        finally:
            db.commit()

# Helper para ejecutar async en contexto sincrónico si es necesario
def asyncio_run(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)
