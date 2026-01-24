from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum
import uuid

Base = declarative_base()

# -----------------------------------------------------------------------------
# 🆕 CORE PIVOT: FORUMS & FUNCTIONAL IDENTITIES (2026-01-24)
# -----------------------------------------------------------------------------

class Forum(Base):
    """Fuente de contenido externo (Reddit, Discourse, etc)"""
    __tablename__ = "forums"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    platform = Column(String, nullable=False) # reddit, discourse, custom
    base_url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    threads = relationship("ForumThread", back_populates="forum")

class ForumThread(Base):
    """Hilos específicos extraídos de un foro"""
    __tablename__ = "forum_threads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forum_id = Column(UUID(as_uuid=True), ForeignKey("forums.id"))
    
    title = Column(String, nullable=False)
    thread_url = Column(String, nullable=False)
    extracted_at = Column(DateTime, nullable=True)
    status = Column(String, default="pending") # pending | processed | ignored
    created_at = Column(DateTime, default=datetime.utcnow)
    
    forum = relationship("Forum", back_populates="threads")

class FunctionalIdentity(Base):
    """Identidad funcional que reemplaza a LinkedIn como 'persona'"""
    __tablename__ = "functional_identities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False) # founder, dev, marketer
    tone = Column(String, nullable=True) # analytical, bold
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reports = relationship("ExecutiveReport", back_populates="identity")

class ReportedUrl(Base):
    """URLs relevantes detectadas manualmente o por crawler"""
    __tablename__ = "reported_urls"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String, nullable=False) # forum, manual, crawler
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    relevance_score = Column(Numeric, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ExecutiveReport(Base):
    """El producto final: Resumen ejecutivo para la identidad"""
    __tablename__ = "executive_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identity_id = Column(UUID(as_uuid=True), ForeignKey("functional_identities.id"))
    
    summary = Column(Text, nullable=False)
    recommendations = Column(Text, nullable=True)
    source_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    identity = relationship("FunctionalIdentity", back_populates="reports")

# -----------------------------------------------------------------------------
# LEGACY / SUPPORT MODELS
# -----------------------------------------------------------------------------

class ContentStatus(str, enum.Enum):
    PENDING = "pending" # Replaces DRAFT
    GENERATED = "generated"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    FAILED_AI = "failed_ai" # Replaces FAILED
    FAILED = "failed"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"

class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"

class Project(Base):
    """Configuración por Cliente/Proyecto"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    owner_id = Column(String, index=True, nullable=True) # Link to Supabase Auth UUID
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    topics = relationship("Topic", back_populates="project")
    editorial_rules = relationship("EditorialRule", back_populates="project")
    posts = relationship("Post", back_populates="project")
    jobs = relationship("AutoPublisherJob", back_populates="project")
    connected_accounts = relationship("ConnectedAccount", back_populates="project")
    campaigns = relationship("Campaign", back_populates="project")
    user_profile = relationship("UserProfile", back_populates="project", uselist=False)

class UserProfile(Base):
    """Perfil del Usuario (Identidad y Contexto)"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True)
    
    profession = Column(String, nullable=True)
    specialty = Column(String, nullable=True)
    bio_summary = Column(Text, nullable=True)
    target_audience = Column(String, nullable=True)
    
    # Futuro: Support for vectors or embeddings link
    
    project = relationship("Project", back_populates="user_profile")

class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class Campaign(Base):
    """Agrupador lógico de publicaciones con estrategia definida"""
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    name = Column(String, index=True)
    objective = Column(String) # educar, vender, posicionar
    tone = Column(String) # formal, didáctico, ácido
    # topics = Column(String) # Removed to match Supabase schema
    
    # posts_per_day = Column(Integer, default=1) # Removed
    # schedule_strategy = Column(String) # Removed
    
    status = Column(String, default=CampaignStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    project = relationship("Project", back_populates="campaigns")
    posts = relationship("Post", back_populates="campaign")

class Topic(Base):
    """Temas sobre los que hablar"""
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, index=True)
    keywords = Column(String) # Comma separated
    weight = Column(Integer, default=1) # Probabilidad de selección
    
    project = relationship("Project", back_populates="topics")
    # posts = relationship("Post", back_populates="topic") # Removed relationship

class EditorialRule(Base):
    """Instrucciones de tono y estilo"""
    __tablename__ = "editorial_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    rule_type = Column(String) # e.g., "tone", "length", "forbidden_words"
    content = Column(Text)
    
    project = relationship("Project", back_populates="editorial_rules")

class Post(Base):
    """El contenido generado"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    # topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True) # Removed to match Supabase schema
    
    title = Column(String, nullable=True)
    content_text = Column(Text)
    hashtags = Column(String, nullable=True) # JSON string or comma-separated
    # cta = Column(String, nullable=True) # Removed
    platform = Column(String, default="linkedin")
    status = Column(String, default=ContentStatus.PENDING) # Enum como string para compatibilidad
    
    # Observability / AI Metadata
    # ai_model = Column(String, nullable=True) # Removed
    # generation_time_ms = Column(Integer, nullable=True) # Removed
    # tokens_used = Column(Integer, nullable=True) # Removed
    # generated_at = Column(DateTime, default=datetime.utcnow) # Removed

    scheduled_for = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    project = relationship("Project", back_populates="posts")
    campaign = relationship("Campaign", back_populates="posts")
    media = relationship("Media", back_populates="post")

class Media(Base):
    """Archivos multimedia asociados"""
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    media_type = Column(String, default=MediaType.IMAGE)
    local_path = Column(String) # Path en storage local
    public_url = Column(String, nullable=True) # URL si se sube a S3
    
    post = relationship("Post", back_populates="media")

class AutoPublisherJob(Base):
    """Configuración del publicador automático"""
    __tablename__ = "auto_publisher_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    name = Column(String)
    active = Column(Boolean, default=False)
    posts_per_day = Column(Integer, default=1)
    time_window_start = Column(String, default="09:00")
    time_window_end = Column(String, default="18:00")
    
    last_run = Column(DateTime, nullable=True)
    
    project = relationship("Project", back_populates="jobs")

class ConnectedAccount(Base):
    """Cuentas sociales vinculadas (OAuth)"""
    __tablename__ = "connected_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    provider = Column(String, default="linkedin")
    external_account_id = Column(String) # ID único en la plataforma
    provider_name = Column(String, nullable=True) # Nombre para mostrar
    
    access_token_encrypted = Column(String)
    refresh_token_encrypted = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    scopes = Column(String, nullable=True)
    
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="connected_accounts")

class MediaUsage(Base):
    """Registro de consumo diario por usuario/tipo"""
    __tablename__ = "media_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True) # ID externo o interno
    media_type = Column(String, index=True) # image, video
    date = Column(DateTime, index=True) # Fecha truncada al día
    count = Column(Integer, default=0)
    
    # Índice único compuesto para evitar duplicados por día
    # En SQLite se puede manejar a nivel de aplicación o con UniqueConstraint explícito
    # __table_args__ = (UniqueConstraint('user_id', 'media_type', 'date', name='_user_media_date_uc'),)
