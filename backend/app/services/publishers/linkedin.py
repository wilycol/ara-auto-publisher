from app.services.publishers.base import PublisherAdapter
from app.models.domain import Post, ConnectedAccount
from app.core.logging import logger
import uuid

class LinkedInPublisher(PublisherAdapter):
    """
    Implementación Mock para LinkedIn.
    En Fase 2.3 solo loguea, no llama a la API real.
    """
    
    async def publish(self, post: Post, account: ConnectedAccount) -> dict:
        # Simulación de validación
        if not account or not account.access_token_encrypted:
            raise ValueError("Cuenta de LinkedIn no conectada o inválida")
            
        logger.info(f"🚀 [MOCK] Publicando en LinkedIn | Post ID: {post.id} | Account: {account.provider_name}")
        logger.info(f"📄 Contenido: {post.content_text[:50]}...")
        
        # Simulación de éxito
        mock_external_id = f"urn:li:share:{uuid.uuid4()}"
        mock_url = f"https://www.linkedin.com/feed/update/{mock_external_id}"
        
        logger.info(f"✅ [MOCK] Publicación exitosa. ID: {mock_external_id}")
        
        return {
            "external_id": mock_external_id,
            "url": mock_url,
            "platform_response": {"status": "success", "mock": True}
        }
