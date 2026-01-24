import random
import time
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.domain import AutoPublisherJob, Topic, Post, ContentStatus, Project, EditorialRule
from app.schemas.ai import AIRequest
from app.services.ai_client import AIClientInterface, MockAIClient, OpenAICompatibleClient
from app.services.tracking_service import TrackingService

class AutoPublisherService:
    def __init__(self, ai_client: AIClientInterface = None):
        self.ai_client = ai_client or MockAIClient()

    def run(self, db: Session, job_id: int) -> Post:
        """
        Ejecuta una iteración del Auto Publisher para un Job específico.
        NO realiza la publicación final, solo genera el borrador (DRAFT/GENERATED).
        """
        
        # 1. Validar Job
        job = db.query(AutoPublisherJob).filter(AutoPublisherJob.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if not job.active:
            raise HTTPException(status_code=400, detail="Job is not active")

        # 2. Obtener contexto del proyecto
        project = db.query(Project).filter(Project.id == job.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # 3. Selección de Tema (Topic)
        # Usamos weighted random choice basado en el peso del tema
        topics = db.query(Topic).filter(Topic.project_id == project.id).all()
        
        if not topics:
            # Fallback si no hay temas definidos
            selected_topic_name = "General Updates"
            selected_topic_id = None
            keywords = ""
        else:
            weights = [t.weight for t in topics]
            selected_topic = random.choices(topics, weights=weights, k=1)[0]
            selected_topic_name = selected_topic.name
            selected_topic_id = selected_topic.id
            keywords = selected_topic.keywords

        # 4. Construir AI Request
        # Recopilar reglas editoriales
        rules = db.query(EditorialRule).filter(EditorialRule.project_id == project.id).all()
        tone_rule = next((r.content for r in rules if r.rule_type == "tone"), "Professional and engaging")
        
        prompt = self._build_prompt(selected_topic_name, keywords, rules)
        
        ai_request = AIRequest(
            prompt=prompt,
            tone=tone_rule,
            context=f"Project Description: {project.description}"
        )

        # 5. Llamar al AI Engine (Mock por ahora)
        start_time = time.time()
        ai_response = self.ai_client.generate_content(ai_request)
        end_time = time.time()
        
        generation_time_ms = int((end_time - start_time) * 1000)

        # Determinar nombre del modelo (simple heurística)
        model_name = "unknown"
        if isinstance(self.ai_client, MockAIClient):
            model_name = "mock-v1"
        elif isinstance(self.ai_client, OpenAICompatibleClient):
            model_name = self.ai_client.model

        # 6. Crear Post (Persistencia)
        new_post = Post(
            project_id=project.id,
            topic_id=selected_topic_id,
            title=ai_response.title,
            content_text=ai_response.content,
            status=ContentStatus.GENERATED,
            # Observability
            ai_model=model_name,
            generation_time_ms=generation_time_ms,
            tokens_used=ai_response.tokens_used
        )
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        # 7. Tracking (Audit Log)
        try:
            tracker = TrackingService(db)
            tracker.record_generation({
                "user_id": "auto-publisher-job", # System user
                "project_id": project.id,
                "project_name": project.name,
                "objective": "Auto Generated",
                "topic": selected_topic_name,
                "platform": "linkedin", # TODO: Get from job config
                "content_type": "text",
                "ai_agent": model_name,
                "generated_url": f"/posts/{new_post.id}",
                "status": "generated",
                "correlation_id": f"job-{job_id}-post-{new_post.id}"
            })
        except Exception as e:
            # Non-blocking error
            print(f"Tracking Error: {e}")

        return new_post

    def _build_prompt(self, topic: str, keywords: str, rules: list[EditorialRule]) -> str:
        """Helper para construir el prompt final"""
        rules_text = "\n".join([f"- {r.rule_type}: {r.content}" for r in rules])
        
        return (
            f"Write a social media post about '{topic}'.\n"
            f"Keywords to include: {keywords}.\n"
            f"Editorial Rules:\n{rules_text}\n"
        )
