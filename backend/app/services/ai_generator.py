import json
import re
from typing import List, Dict, Any
from app.models.domain import Campaign
from app.services.ai_provider_service import ai_provider_service
from app.core.logging import logger

class AIGeneratorService:
    def __init__(self):
        pass

    def _build_prompt(self, campaign: Campaign, platform: str) -> str:
        """
        Construye el Prompt Maestro basado en la campaña y la identidad funcional (si existe).
        """
        # Base Persona
        persona_instructions = "Eres un estratega de contenido profesional especializado en redes sociales."
        
        # Identity Overlay
        if campaign.identity:
            id_name = campaign.identity.name
            id_role = campaign.identity.role or "experto"
            id_purpose = campaign.identity.purpose or ""
            id_tone = campaign.identity.tone or campaign.tone
            id_style = getattr(campaign.identity, 'communication_style', '') or "profesional y directo"
            id_limits = getattr(campaign.identity, 'content_limits', '') or "No uses clickbait. No inventes datos."
            
            persona_instructions = f"""
Eres {id_name}.
Tu propósito principal es: {id_purpose}.
Tu tono de voz debe ser: {id_tone}.
Estilo de comunicación: {id_style}.

LÍMITES (Lo que NO debes hacer):
{id_limits}
"""
        
        return f"""
Sistema
{persona_instructions}
Tu tarea es generar publicaciones alineadas a un objetivo y temática.
Responde EXCLUSIVAMENTE en JSON válido.

Usuario
Objetivo de la campaña: {campaign.objective}
Tono (Override campaña): {campaign.tone}
Plataforma: {platform}

Instrucciones
- Mantén el texto claro, útil y humano
- Devuelve solo JSON válido con la siguiente estructura:
{{
  "title": "string",
  "content": "string",
  "hashtags": ["string", "string"],
  "cta": "string",
  "platform": "{platform}"
}}
"""

    async def generate_posts(self, campaign: Campaign, count: int = 1, platform: str = "linkedin") -> List[Dict[str, Any]]:
        """
        Genera X borradores de posts para una campaña usando el servicio Multi-IA.
        """
        generated_posts = []
        prompt = self._build_prompt(campaign, platform)
        
        for i in range(count):
            try:
                # Llamada al orquestador Multi-IA
                raw_response = await ai_provider_service.generate(prompt)
                
                # Intentar limpiar bloques de código markdown
                clean_json = raw_response.replace("```json", "").replace("```", "").strip()
                
                # Extracción robusta de JSON usando Regex si la limpieza simple falla
                try:
                    post_data = json.loads(clean_json)
                except json.JSONDecodeError:
                    # Buscar el primer '{' y el último '}'
                    match = re.search(r'\{.*\}', clean_json, re.DOTALL)
                    if match:
                        clean_json = match.group(0)
                        post_data = json.loads(clean_json)
                    else:
                        raise ValueError("No se encontró un objeto JSON válido en la respuesta")

                # Normalizar hashtags si vienen como lista
                if isinstance(post_data.get("hashtags"), list):
                    post_data["hashtags"] = json.dumps(post_data["hashtags"]) # Guardar como string para DB simple o procesar luego
                    
                generated_posts.append(post_data)
                
            except json.JSONDecodeError:
                logger.error(f"❌ La IA devolvió un JSON inválido: {raw_response[:200]}...")
                continue
            except Exception as e:
                logger.error(f"❌ Error generando post {i+1}: {str(e)} | Respuesta raw: {raw_response[:200]}...")
                continue
            
        return generated_posts
