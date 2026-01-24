from abc import ABC, abstractmethod
from app.models.domain import Post, ConnectedAccount

class PublisherAdapter(ABC):
    """
    Interface base para adaptadores de publicación (LinkedIn, TikTok, etc.)
    """
    
    @abstractmethod
    async def publish(self, post: Post, account: ConnectedAccount) -> dict:
        """
        Publica el post en la plataforma correspondiente.
        Debe retornar un dict con metadatos de la publicación (ej: external_id, url).
        Si falla, debe lanzar una excepción.
        """
        pass
