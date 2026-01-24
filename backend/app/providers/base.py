from abc import ABC, abstractmethod

class ImageProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, resolution: str = "standard") -> dict:
        """Generates an image and returns metadata including URL"""
        pass

class VideoProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, duration: int) -> dict:
        """Generates a video and returns metadata including URL"""
        pass
