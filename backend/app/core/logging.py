import logging
import sys

def setup_logging():
    """
    Configura el logging central de la aplicación.
    Asegura formato consistente y nivel adecuado.
    """
    # Formato de log: Timestamp | Nivel | Logger | Mensaje
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    
    # Configuración base
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Ajustar niveles de librerías ruidosas si fuera necesario
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    
    # Logger raíz
    logger = logging.getLogger("ara_neuro_post")
    logger.info("Sistema de logging inicializado correctamente.")
    
    return logger

# Instancia global para importar
logger = logging.getLogger("ara_neuro_post")
