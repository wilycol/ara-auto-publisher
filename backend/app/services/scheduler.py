from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.core.database import SessionLocal
from app.models.domain import Post, ContentStatus, ConnectedAccount
from app.core.logging import logger
from app.services.publishers.linkedin import LinkedInPublisher

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
            Post.status == ContentStatus.APPROVED,
            Post.scheduled_for <= now
        ).all()
        
    def _process_post(self, db: Session, post: Post):
        logger.info(f"⚙️ Procesando Post {post.id} | Proyecto {post.project_id} | Plataforma {post.platform}")
        
        # 1. Cambiar a PROCESSING
        post.status = ContentStatus.PROCESSING
        db.commit()
        
        try:
            # 2. Obtener adaptador
            adapter = self.publishers.get(post.platform.lower())
            if not adapter:
                raise ValueError(f"No hay adaptador para plataforma: {post.platform}")
            
            # 3. Obtener cuenta conectada
            account = db.query(ConnectedAccount).filter(
                ConnectedAccount.project_id == post.project_id,
                ConnectedAccount.provider == post.platform.lower(),
                ConnectedAccount.active == True
            ).first()
            
            # NOTA: En F2.3, si no hay cuenta, podríamos fallar. 
            # Pero como es Mock, tal vez queramos permitir probar sin cuenta real?
            # El prompt dice "Mock LinkedIn... Simula publicación".
            # Pero el adapter mock valida la cuenta: "if not account... raise ValueError".
            # Así que necesitamos una cuenta conectada (aunque sea fake) o ajustar el mock.
            # Para facilitar pruebas F2.3 sin cuenta real, voy a crear un objeto dummy si no existe, 
            # SOLO si estamos en modo desarrollo/test. 
            # Mejor: El script de prueba debería crear una cuenta fake.
            
            if not account:
                raise ValueError(f"No hay cuenta conectada activa para {post.platform}")
                
            # 4. Publicar (Delegar al adaptador)
            result = asyncio_run(adapter.publish(post, account))
            
            # 5. Actualizar a PUBLISHED
            post.status = ContentStatus.PUBLISHED
            post.published_at = datetime.utcnow()
            # Si tuviéramos campo metadata, guardaríamos result['external_id']
            
            logger.info(f"✅ Post {post.id} publicado correctamente.")
            
        except Exception as e:
            logger.error(f"❌ Fallo al publicar Post {post.id}: {str(e)}")
            post.status = ContentStatus.FAILED
            # Podríamos guardar el error en una columna error_message si existiera
            
        finally:
            db.commit()

# Helper para ejecutar async en contexto sincrónico si es necesario
import asyncio
def asyncio_run(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)
