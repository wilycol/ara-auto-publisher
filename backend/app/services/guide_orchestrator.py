import json
import asyncio
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from app.models.domain import UserProfile as DBUserProfile, Campaign, Post, ContentStatus, FunctionalIdentity
from app.schemas.guide import UserProfile as SchemaUserProfile
from app.schemas.guide import GuideNextRequest, GuideNextResponse, GuideOption, GuideMode, IdentityDraft
from app.services.ai_provider_service import ai_provider_service
from app.services.ai_generator import AIGeneratorService
from app.core.logging import logger

class GuideOrchestratorService:
    def __init__(self):
        self.ai_service = ai_provider_service

    async def process_next_step(self, request: GuideNextRequest, db: Session = None) -> GuideNextResponse:
        """
        Orquesta el siguiente paso de la guía conversacional.
        Ahora soporta 3 modos: GUIDED (secuencial), COLLABORATOR (inferencia), EXPERT (directo).
        """
        current_step = request.current_step
        
        # 0. Cargar Perfil Persistente (si existe y no está en state)
        # ⚠️ FIX CRÍTICO DE PRIVACIDAD (ANTI-CHISME):
        # Deshabilitamos la carga automática del perfil global (Project ID 1).
        # Razón: En modo colaborativo, esto causa que sesiones nuevas "hereden" datos de sesiones previas
        # o del usuario "dueño" del local, violando el aislamiento de sesión.
        # Solo se debe cargar perfil si hay una autenticación explícita (que se implementará vía User ID en el futuro).
        
        # if db and not request.state.user_profile:
        #     try:
        #         # Asumimos Project ID 1 para Single Tenant Local
        #         db_profile = db.query(DBUserProfile).filter_by(project_id=1).first()
        #         if db_profile:
        #             request.state.user_profile = SchemaUserProfile(
        #                 profession=db_profile.profession,
        #                 specialty=db_profile.specialty,
        #                 bio_summary=db_profile.bio_summary,
        #                 target_audience_profile=db_profile.target_audience
        #             )
        #     except Exception as e:
        #         logger.error(f"Error loading user profile: {e}")

        # Contexto de Logging
        log_context = {
            "event": "guide_step",
            "mode": request.mode,
            "guide_session_id": request.guide_session_id,
            "step": request.current_step,
            "user_input": request.user_input,
            "guide_state_snapshot": request.state.model_dump(),
            "timestamp": datetime.utcnow().isoformat(),
            "ai_used": False,
            "fallback_used": False,
            "ai_model": None
        }

        # Fetch Identities for Context
        identities_list = []
        if db:
            try:
                # Asumimos Project ID 1
                identities = db.query(FunctionalIdentity).filter_by(project_id=1).all()
                identities_list = [{
                    "id": str(i.id), 
                    "name": i.name, 
                    "role": i.role,
                    "purpose": i.purpose,
                    "tone": i.tone,
                    "communication_style": i.communication_style,
                    "content_limits": i.content_limits
                } for i in identities]
            except Exception as e:
                logger.error(f"Error fetching identities for guide: {e}")

        try:
            response: GuideNextResponse = None

            if request.mode == GuideMode.COLLABORATOR:
                response = await self._process_collaborator_mode(request, log_context, identities_list, db)
            elif request.mode == GuideMode.EXPERT:
                response = await self._process_expert_mode(request, log_context, db)
            elif request.mode == GuideMode.IDENTITY_CREATION:
                response = await self._process_identity_creation_mode(request, log_context, db)
            else:
                # Default to Guided (Legacy/Standard)
                response = await self._process_guided_mode(request, log_context)


            # Enriquecer log con resultado
            log_context["assistant_message"] = response.assistant_message
            log_context["options_returned"] = [opt.model_dump() for opt in response.options]
            log_context["next_step"] = response.next_step
            
            # 📝 Log Estructurado Final
            logger.info(json.dumps(log_context, default=str))

            return response

        except Exception as e:
            # Log de error estructurado
            error_log = {
                "event": "guide_ai_error",
                "guide_session_id": request.guide_session_id,
                "step": request.current_step,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.error(json.dumps(error_log))
            
            # Fallback seguro
            return self._fallback_response(request.current_step)

    # -------------------------------------------------------------------------
    # 🟢 MODO 1: GUIDED (Secuencial, Seguro, Step-by-Step)
    # -------------------------------------------------------------------------
    async def _process_guided_mode(self, request: GuideNextRequest, log_ctx: dict) -> GuideNextResponse:
        current_step = request.current_step
        next_step = current_step + 1
        
        # Casos especiales
        if current_step == 6:
            return GuideNextResponse(
                assistant_message="Campaña lista para crear.",
                next_step=6,
                state_patch={}
            )

        # Lógica de transición de estado (Legacy Flow)
        if current_step == 1:
            return await self._step_audience(request, next_step, log_ctx)
        elif current_step == 2:
            return await self._step_platform(request, next_step, log_ctx)
        elif current_step == 3:
            return await self._step_strategy(request, next_step, log_ctx)
        elif current_step == 4:
            return await self._step_topics(request, next_step, log_ctx)
        elif current_step == 5:
            return await self._step_confirmation(request, next_step, log_ctx)
        else:
            log_ctx["fallback_used"] = True
            return self._fallback_response(current_step)

    # -------------------------------------------------------------------------
    # 🔵 MODO 2: COLLABORATOR (Conversacional, Inferencia, Flexible)
    # -------------------------------------------------------------------------
    async def _process_collaborator_mode(self, request: GuideNextRequest, log_ctx: dict, identities: list, db: Session = None) -> GuideNextResponse:
        """
        El corazón del producto (Modo Colaborador Adaptativo).
        Implementa la arquitectura de "Reglas Suaves" e Identidad como Capa.
        """
        state = request.state
        user_input = request.user_input or ""
        user_value = request.user_value or ""
        summary = state.conversation_summary or "Inicio de conversación."

        # ⚡ PRE-PROCESSING: Aplicar elecciones explícitas
        if user_value:
            if user_value.startswith("audience:"):
                state.audience = user_value.replace("audience:", "").strip()
            elif user_value.startswith("platform:"):
                state.platform = user_value.replace("platform:", "").strip()
            elif user_value.startswith("objective:"):
                state.objective = user_value.replace("objective:", "").strip()
            elif user_value.startswith("tone:"):
                state.tone = user_value.replace("tone:", "").strip()

        # 🎭 CONTEXTO DE IDENTIDAD ACTIVA (CAPA)
        active_identity_instruction = ""
        identity_context = ""
        if state.identity_id:
            found_id = next((i for i in identities if i["id"] == state.identity_id), None)
            if found_id:
                active_identity_instruction = f"""
                ⚠️ CAPA DE IDENTIDAD ACTIVA:
                No hables como "ARA" genérico. ADOPTA LA PERSPECTIVA DE: {found_id['name']}
                Rol: {found_id['role']}
                Tono: {found_id['tone']}
                Estilo: {found_id['communication_style']}
                
                NOTA: Esta identidad es un LENTE para enfocar la solución, no una restricción para tu inteligencia.
                Usa el vocabulario y prioridades de este rol.
                """
                identity_context = f"Identidad Activa: {found_id['name']} ({found_id['role']})"

        # 🧠 PROMPT MAESTRO ADAPTATIVO (REFACTORIZADO V2)
        # Enfoque: Inicio Limpio, Escucha Activa, Cero Asunciones.
        
        identities_str = json.dumps(identities, indent=2)
        
        # Validación de perfil para el prompt
        has_profile_data = state.user_profile and (state.user_profile.profession or state.user_profile.bio_summary)
        profile_str = f"{state.user_profile.profession} | {state.user_profile.specialty}" if has_profile_data else "DESCONOCIDO (Usuario Nuevo/No Autenticado)"

        prompt = f"""
        Eres ARA, una IA Colaborativa diseñada para interactuar como un humano, no como un sistema ni un formulario.
        
        {active_identity_instruction}

        🛡️ REGLA DE SEGURIDAD CRÍTICA (OBLIGATORIA):
        Nunca infieras, recuerdes o reutilices datos personales del usuario (profesión, experiencia, proyectos, identidad, historial) de conversaciones previas, otros usuarios o contexto implícito.
        
        Si un dato no fue:
        1. Declarado explícitamente por el usuario en esta sesión, o
        2. Cargado desde un perfil autenticado (Ver "Perfil Usuario" abajo)
        
        ENTONCES debes tratarlo como DESCONOCIDO.
        Esto es hard rule, no sugerencia.

        CONTEXTO GLOBAL (AISLADO):
        - Perfil Usuario: {profile_str}
        - Estado Actual: {state.model_dump_json(exclude={'conversation_summary'})}
        - Identidades Disponibles: {identities_str}
        - Resumen Conversación Actual: "{summary}"
        
        INPUT ACTUAL:
        - Texto: "{user_input}"
        - Selección Técnica: "{user_value}"

        📜 REGLAS DE COMPORTAMIENTO (ESTRICTAS):

        1. INICIO LIMPIO (TABULA RASA):
           - No asumas nada. No conoces al usuario.
           - Si el resumen de conversación está vacío o es el inicio: Tu única misión es ESCUCHAR.
           - Pregunta base: "¿Qué necesitas ahora?" (o variante natural según contexto).

        2. ESCUCHA ACTIVA + REFLEJO:
           - Cuando el usuario te dé información suficiente, responde con este esquema (breve y humano):
             a) "Esto es lo que dijiste..." (Hechos puros).
             b) "Esto es lo que interpreto..." (Tus inferencias).
             c) "Esto es lo que falta por aclarar..." (Dudas para avanzar).
           - Si falta información, solo pregunta o aclara.

        3. PROPUESTA SIN JERGA:
           - Propón hasta 3 caminos concretos si corresponde.
           - Lenguaje simple, cero marketing, cero tecnicismos innecesarios.
           - Ningún camino es obligatorio.

        4. GESTIÓN DE DUDA:
           - Si el usuario duda: Explica corto y vuelve a proponer.
           - Nunca fuerces decisiones.
           - Nunca reinicies la conversación bruscamente.

        5. 🚫 LENGUAJE PROHIBIDO (HARD RULES):
           - JAMÁS digas: "Te voy a ayudar", "Estoy aquí para asistirte", "Recuerdo que...", "Como ya sabes...", "Hola [Nombre]".
           - PREFIERE: "Dime y vemos", "Vamos por partes", "Si quieres, probamos esto".
           - La Identidad Funcional (si hay activa) es solo un LENTE de tono, no un historial de vida.

        TU TAREA AHORA:
        1. Analiza el input. ¿Tienes suficiente para reflejar (Hechos/Inferencias/Faltantes)?
        2. Genera una respuesta natural siguiendo las REGLAS DE COMPORTAMIENTO.
        3. Define si hay cambios en el estado (state_patch).
        4. Actualiza el resumen de la conversación.

        FORMATO DE RESPUESTA (JSON PURO):
        {{
            "message": "Tu respuesta conversacional...",
            "options": [
                {{"label": "Opción Corta", "value": "valor_tecnico"}}
            ],
            "state_patch": {{
                "user_profile": {{ "profession": "...", "bio_summary": "..." }},
                "objective": "...",
                "audience": "...",
                "platform": "...",
                "identity_id": "uuid..."
            }},
            "updated_summary": "Resumen actualizado...",
            "user_level_detected": "principiante|intermedio|experto"
        }}
        """

        # 🚀 LÓGICA DE EJECUCIÓN (CREACIÓN DE CAMPAÑA)
        # Se activa si el usuario confirma explícitamente
        is_create_intent = (user_value in ['create', 'confirm_create']) or ('crear campaña' in user_input.lower() and request.current_step > 2)
        has_minimum_data = state.objective and state.audience and state.platform
        
        if user_value == 'confirm_create' and has_minimum_data:
             # --- LOGICA DE CREACION REAL (Mantenemos la existente) ---
            if not db:
                return GuideNextResponse(
                    assistant_message="Error: No hay conexión a base de datos para guardar la campaña.",
                    options=[], next_step=request.current_step, state_patch={}
                )
            
            try:
                # 1. Crear Campaña
                identity_uuid = None
                if state.identity_id:
                    try:
                        identity_uuid = uuid.UUID(state.identity_id)
                    except:
                        pass 

                new_campaign = Campaign(
                    project_id=1,
                    name=f"Campaña: {state.objective[:40]}",
                    objective=state.objective,
                    tone=state.tone or "Professional",
                    identity_id=identity_uuid,
                    status="active"
                )
                db.add(new_campaign)
                db.commit()
                db.refresh(new_campaign)
                
                if new_campaign.identity_id:
                    identity_chk = db.query(FunctionalIdentity).get(new_campaign.identity_id)
                    new_campaign.identity = identity_chk

                # 2. Generar Contenido
                generator = AIGeneratorService()
                target_platform = state.platform or "linkedin"
                generated_posts = await generator.generate_posts(new_campaign, count=1, platform=target_platform)
                
                created_posts_count = 0
                for post_data in generated_posts:
                    new_post = Post(
                        project_id=1,
                        campaign_id=new_campaign.id,
                        identity_id=new_campaign.identity_id,
                        title=post_data.get("title", "Untitled Post"),
                        content_text=post_data.get("content", ""),
                        hashtags=post_data.get("hashtags", ""),
                        cta=post_data.get("cta", ""),
                        platform=target_platform,
                        status=ContentStatus.GENERATED,
                        scheduled_for=datetime.utcnow() + timedelta(days=1)
                    )
                    db.add(new_post)
                    created_posts_count += 1
                    
                db.commit()
                
                return GuideNextResponse(
                    assistant_message=f"¡Excelente! He creado la campaña **'{new_campaign.name}'** y generado **{created_posts_count} borrador(es)** listos para revisión.\n\nPuedes verlos en la lista de Posts.",
                    options=[
                        GuideOption(label="✨ Crear otra campaña", value="new_campaign")
                    ],
                    next_step=6, 
                    state_patch={}
                )
                
            except Exception as e:
                logger.error(f"Error creating campaign via chat: {e}")
                return GuideNextResponse(
                    assistant_message=f"Hubo un problema técnico al crear la campaña: {str(e)}",
                    options=[GuideOption(label="Intentar de nuevo", value="confirm_create")],
                    next_step=request.current_step,
                    state_patch={}
                )

        def fallback():
            return GuideNextResponse(
                assistant_message="Entiendo. ¿Podrías darme más detalles para asegurarme de captar bien tu idea?",
                options=[GuideOption(label="Continuar", value="continue")],
                next_step=request.current_step,
                state_patch={}
            )

        try:
            # Ejecutar IA con el prompt unificado
            response = await self._execute_ai_step_flexible(prompt, log_ctx, request.current_step, fallback, skip_ai_fallback=False)

            # PERSISTENCIA DE PERFIL (DB)
            if db and response.state_patch and "user_profile" in response.state_patch:
                profile_data = response.state_patch["user_profile"]
                if profile_data and isinstance(profile_data, dict):
                    try:
                        # Asumimos Project ID 1
                        db_profile = db.query(DBUserProfile).filter_by(project_id=1).first()
                        if not db_profile:
                            db_profile = DBUserProfile(project_id=1)
                            db.add(db_profile)
                        
                        if "profession" in profile_data: db_profile.profession = profile_data["profession"]
                        if "specialty" in profile_data: db_profile.specialty = profile_data["specialty"]
                        if "bio_summary" in profile_data: db_profile.bio_summary = profile_data["bio_summary"]
                        if "target_audience_profile" in profile_data: db_profile.target_audience = profile_data["target_audience_profile"]
                        
                        db.commit()
                        logger.info(f"✅ User Profile persisted to DB for Project 1: {profile_data.get('profession')}")
                    except Exception as e:
                        db.rollback()
                        logger.error(f"Failed to persist User Profile: {e}")

            return response
            
        except Exception as e:
            logger.warning(f"⚠️ Error inicial en Collaborator Mode: {e}. Reintentando...")
            try:
                # Reintento único por si fue un error estocástico (hallucination, JSON malformado)
                # También permitimos fallback en el reintento
                return await self._execute_ai_step_flexible(prompt, log_ctx, request.current_step, fallback, skip_ai_fallback=False)
            except Exception as e2:
                # Si llegamos aquí, es porque la IA Real falló dos veces
                logger.warning(f"🚫 MODO COLABORADOR BLOQUEADO: Error en ejecución de IA Real (Reintento fallido): {e2}")
                return self._create_blocked_response(request.current_step)

    def _create_blocked_response(self, step: int) -> GuideNextResponse:
        # Log estructurado de bloqueo
        error_log = {
            "event": "COLLABORATOR_MODE_BLOCKED",
            "reason": "AI_PROVIDER_UNAVAILABLE",
            "provider": "LocalFallbackProvider (Avoided)", 
            "timestamp": datetime.utcnow().isoformat(),
            "environment": "development" 
        }
        logger.error(json.dumps(error_log))
        
        return GuideNextResponse(
            assistant_message="El Modo Colaborador no está disponible en este momento.\nPara que no pierdas tiempo, elige cómo quieres continuar.",
            options=[
                GuideOption(label="🧭 Ir al Modo Guía", value="switch_guide"),
                GuideOption(label="⚙️ Ir al Modo Experto", value="switch_expert")
            ],
            next_step=step,
            state_patch={},
            status="blocked"
        )

    # -------------------------------------------------------------------------
    # ⚫ MODO 3: EXPERT (Directo, Eficiente, Sin Charla)
    # -------------------------------------------------------------------------
    async def _process_expert_mode(self, request: GuideNextRequest, log_ctx: dict, db: Session = None) -> GuideNextResponse:
        """
        Modo interrogatorio eficiente.
        Usa IA para extraer datos y preguntar lo siguiente de forma directa.
        """
        state = request.state
        user_input = request.user_input or ""
        user_value = request.user_value or ""

        # 🛑 REGLA 1: FASE DE DESCUBRIMIENTO OBLIGATORIA
        # Incluso el Experto necesita saber quién eres.
        has_profile = state.user_profile and (state.user_profile.profession or state.user_profile.bio_summary)
        
        if not has_profile:
            # Prompt de descubrimiento versión "Expert" (Directo)
            prompt = f"""
            Eres ARA Post Manager (Modo EXPERTO).
            Necesitas el PERFIL del usuario antes de cualquier estrategia.
            
            INPUT: "{user_input}"
            
            TAREA:
            1. Si no hay datos de profesión/especialidad, PREGUNTA: "¿Cuál es tu profesión y especialidad?" (Sé breve).
            2. Si hay datos (o adjuntos simulados), extráelos en JSON.
            
            RESPUESTA JSON:
            {{
                "message": "Pregunta corta...",
                "state_patch": {{
                    "user_profile": {{
                        "profession": "...",
                        "specialty": "...",
                        "bio_summary": "..."
                    }}
                }}
            }}
            """
            try:
                ai_response = await self.ai_service.generate(prompt)
                data = self._parse_json(ai_response)
                patch = data.get("state_patch", {})
                message = data.get("message", "¿Profesión y especialidad?")
                
                # PERSISTENCIA DE PERFIL (DB) - Reutilizamos lógica
                if db and patch and "user_profile" in patch:
                    profile_data = patch["user_profile"]
                    if profile_data:
                        try:
                            db_profile = db.query(DBUserProfile).filter_by(project_id=1).first()
                            if not db_profile:
                                db_profile = DBUserProfile(project_id=1)
                                db.add(db_profile)
                            
                            if "profession" in profile_data: db_profile.profession = profile_data["profession"]
                            if "specialty" in profile_data: db_profile.specialty = profile_data["specialty"]
                            if "bio_summary" in profile_data: db_profile.bio_summary = profile_data["bio_summary"]
                            
                            db.commit()
                        except Exception as e:
                            db.rollback()
                            logger.error(f"Failed to persist User Profile (Expert): {e}")

                return GuideNextResponse(
                    assistant_message=message,
                    options=[],
                    next_step=request.current_step,
                    state_patch=patch
                )
            except Exception as e:
                logger.error(f"Expert Discovery Error: {e}")
                return GuideNextResponse(assistant_message="¿Cuál es tu profesión?", options=[], next_step=request.current_step, state_patch={})

        # --- MODO EXPERTO ESTÁNDAR (Ya tenemos perfil) ---
        
        # 🛑 REGLA 4: CONFIRMACIÓN ANTES DE CREAR
        if user_value == 'confirm_create':
             return GuideNextResponse(
                assistant_message=f"Generando campaña...",
                options=[],
                next_step=6, 
                state_patch={}
            )

        # Prompt enfocado en extracción y brevedad
        prompt = f"""
        Eres un asistente experto (Modo EXPERTO). Eficiente, directo, sin saludos.
        
        PERFIL USUARIO:
        {state.user_profile.profession} | {state.user_profile.specialty}
        
        ESTADO ACTUAL:
        {state.model_dump_json(exclude={'conversation_summary'})}
        
        INPUT USUARIO:
        "{user_input}"
        
        CAMPOS REQUERIDOS: objective, audience, platform (linkedin/twitter/instagram/facebook), tone, topics (lista).
        
        TAREA:
        1. Extrae datos del INPUT para llenar los campos vacíos.
        2. Identifica el SIGUIENTE campo vacío prioritario.
        3. Genera una pregunta de 2-4 palabras para pedir ese campo.
        4. Si TODOS los campos están llenos (incluyendo los extraídos), tu mensaje debe ser "CONFIRMAR".
        
        RESPUESTA JSON:
        {{
            "message": "Pregunta corta o CONFIRMAR",
            "state_patch": {{ "campo": "valor" }}
        }}
        """

        try:
            # Ejecutar IA
            ai_response = await self.ai_service.generate(prompt)
            data = self._parse_json(ai_response)
            
            patch = data.get("state_patch", {})
            message = data.get("message", "")
            
            # Verificar si completamos todo
            temp_state = state.model_copy(update=patch)
            is_complete = all([
                temp_state.objective, 
                temp_state.audience, 
                temp_state.platform, 
                temp_state.tone, 
                temp_state.topics
            ])
            
            if is_complete or "CONFIRMAR" in message.upper():
                # Preparar confirmación detallada
                topics_str = ", ".join(temp_state.topics or ["General"])
                confirmation_msg = (
                    f"Resumen Final:\n"
                    f"👤 {state.user_profile.profession}\n"
                    f"🎯 {temp_state.objective}\n"
                    f"👥 {temp_state.audience}\n"
                    f"📢 {temp_state.platform}\n"
                    f"📝 {topics_str}\n\n"
                    f"¿Procedemos?"
                )
                
                return GuideNextResponse(
                    assistant_message=confirmation_msg,
                    options=[
                        GuideOption(label="🚀 Sí, Crear", value="confirm_create"),
                        GuideOption(label="🔄 Reiniciar", value="restart")
                    ],
                    next_step=request.current_step, # Mantenemos paso hasta confirmar
                    state_patch=patch
                )
            
            # Si falta algo, devolvemos la pregunta corta
            return GuideNextResponse(
                assistant_message=message,
                options=[], # Expert no sugiere opciones, espera texto
                next_step=request.current_step,
                state_patch=patch
            )

        except Exception as e:
            logger.error(f"Expert Mode Error: {e}")
            # Fallback simple
            return GuideNextResponse(
                assistant_message="¿Siguiente dato?",
                options=[],
                next_step=request.current_step,
                state_patch={}
            )

    # -------------------------------------------------------------------------
    # 🆕 MODO 4: IDENTITY CREATION (Chat Wizard)
    # -------------------------------------------------------------------------
    async def _process_identity_creation_mode(self, request: GuideNextRequest, log_ctx: dict, db: Session = None) -> GuideNextResponse:
        step = request.current_step
        state = request.state
        draft = state.identity_draft or IdentityDraft()
        user_input = request.user_input
        user_value = request.user_value
        
        # 1. Start -> Name
        if step == 1:
            return GuideNextResponse(
                assistant_message="Hola, vamos a configurar una nueva **Identidad Funcional**. \n\nEsta identidad será una 'máscara' que Ara usará para crear contenido específico.\n\nPara empezar, **¿qué nombre le ponemos?** (Ej. 'Experto Técnico', 'Marca Personal', 'Ventas Agresivas')",
                options=[],
                next_step=2,
                state_patch={"identity_draft": draft.model_dump()}
            )

        # 2. Name -> Type (NEW)
        if step == 2:
            draft.name = user_input
            return GuideNextResponse(
                assistant_message=f"Genial, llamaremos a esta identidad **'{draft.name}'**.\n\n¿Qué **tipo de identidad** es?",
                options=[
                    GuideOption(label="👤 Marca Personal", value="personal_brand"),
                    GuideOption(label="🏢 Corporativa / Marca", value="corporate"),
                    GuideOption(label="🤝 Ventas / Comercial", value="sales"),
                    GuideOption(label="🎧 Soporte / Atención", value="support")
                ],
                next_step=3,
                state_patch={"identity_draft": draft.model_dump()}
            )

        # 3. Type -> Purpose (Modified)
        if step == 3:
            draft.identity_type = user_value or "personal_brand"
            return GuideNextResponse(
                assistant_message=f"Tipo definido: **{draft.identity_type}**.\n\n¿Cuál es su **propósito principal**? (Ej. 'Posicionarme como experto', 'Generar leads cualificados')",
                options=[
                    GuideOption(label="🎓 Educar / Divulgar", value="Educar a mi audiencia"),
                    GuideOption(label="💰 Vender / Convertir", value="Generar leads y ventas"),
                    GuideOption(label="🌟 Branding / Posicionamiento", value="Mejorar marca personal")
                ],
                next_step=4,
                state_patch={"identity_draft": draft.model_dump()}
            )
            
        # 4. Purpose -> Audience (NEW)
        if step == 4:
            draft.purpose = user_value or user_input
            return GuideNextResponse(
                assistant_message=f"Entendido: *{draft.purpose}*.\n\n¿A quién le hablamos? Describe tu **público objetivo** brevemente.",
                options=[], # Free text
                next_step=5,
                state_patch={"identity_draft": draft.model_dump()}
            )

        # 5. Audience -> Tone (Modified)
        if step == 5:
            draft.target_audience = user_input
            return GuideNextResponse(
                assistant_message=f"Audiencia clara. 🎯\n\n¿Qué **tono de voz** debe usar esta identidad?",
                options=[
                    GuideOption(label="👔 Profesional / Serio", value="Profesional, directo y con autoridad"),
                    GuideOption(label="😊 Amigable / Cercano", value="Cercano, uso de emojis, primera persona"),
                    GuideOption(label="🔥 Provocador / Disruptivo", value="Disruptivo, polémico, desafiante")
                ],
                next_step=6,
                state_patch={"identity_draft": draft.model_dump()}
            )
            
        # 6. Tone -> Platforms (Modified)
        if step == 6:
            draft.tone = user_value or user_input
            return GuideNextResponse(
                assistant_message="¿En qué **plataformas** se enfocará principalmente esta identidad?",
                options=[
                    GuideOption(label="LinkedIn (Texto/PDF)", value="linkedin"),
                    GuideOption(label="Twitter/X (Hilos)", value="twitter"),
                    GuideOption(label="Ambas", value="linkedin,twitter")
                ],
                next_step=7,
                state_patch={"identity_draft": draft.model_dump()}
            )

        # 7. Platforms -> Operational Details (NEW)
        if step == 7:
            val = user_value or user_input
            draft.platforms = val.split(",") if "," in val else [val]
            return GuideNextResponse(
                assistant_message="Últimos detalles operativos. ⚙️\n\nDefine un **Call to Action (CTA)** por defecto (Ej. 'Sígueme para más', 'Agenda una llamada').\n(El idioma será Español y frecuencia Media por defecto)",
                options=[
                    GuideOption(label="👇 'Sígueme para más'", value="Sígueme para más contenido"),
                    GuideOption(label="📅 'Agenda una cita'", value="Agenda una cita en el link"),
                    GuideOption(label="💬 'Comenta abajo'", value="Déjame tu opinión en comentarios")
                ],
                next_step=8,
                state_patch={"identity_draft": draft.model_dump()}
            )
            
        # 8. Operational -> Confirmation
        if step == 8:
            draft.preferred_cta = user_value or user_input
            draft.language = "es" # Default
            draft.frequency = "medium" # Default
            draft.campaign_objective = "engagement" # Default
            
            summary = (
                f"**Resumen de Identidad**\n\n"
                f"📌 **Nombre:** {draft.name} ({draft.identity_type})\n"
                f"🎯 **Propósito:** {draft.purpose}\n"
                f"👥 **Audiencia:** {draft.target_audience}\n"
                f"🗣️ **Tono:** {draft.tone}\n"
                f"📢 **Plataformas:** {', '.join(draft.platforms or [])}\n"
                f"🔚 **CTA:** {draft.preferred_cta}\n\n"
                f"¿Creamos esta identidad?"
            )
            
            return GuideNextResponse(
                assistant_message=summary,
                options=[
                    GuideOption(label="✅ Sí, Crear Identidad", value="confirm_create"),
                    GuideOption(label="✏️ Corregir (Reiniciar)", value="restart")
                ],
                next_step=9,
                state_patch={"identity_draft": draft.model_dump()}
            )

        # 9. Action
        if step == 9:
            if user_value == "confirm_create":
                if db:
                    try:
                        platforms_json = json.dumps(draft.platforms)

                        if state.identity_id:
                            existing = db.query(FunctionalIdentity).filter_by(id=state.identity_id).first()
                            if existing:
                                existing.name = draft.name
                                existing.purpose = draft.purpose
                                existing.tone = draft.tone
                                existing.preferred_platforms = platforms_json
                                # Update MVP PRO Fields
                                existing.identity_type = draft.identity_type
                                existing.campaign_objective = draft.campaign_objective
                                existing.target_audience = draft.target_audience
                                existing.language = draft.language
                                existing.preferred_cta = draft.preferred_cta
                                existing.frequency = draft.frequency
                                
                                if not existing.status:
                                    existing.status = "active"
                                db.commit()

                                return GuideNextResponse(
                                    assistant_message=f"Identidad **{draft.name}** actualizada exitosamente. ✅\n\nTus futuros contenidos usarán esta configuración.",
                                    options=[GuideOption(label="🏁 Finalizar", value="close_wizard")],
                                    next_step=10,
                                    state_patch={},
                                    status="success"
                                )

                        new_identity = FunctionalIdentity(
                            project_id=1,
                            name=draft.name,
                            role="custom", # Legacy field requirement
                            purpose=draft.purpose,
                            tone=draft.tone,
                            preferred_platforms=platforms_json,
                            status="active",
                            # MVP PRO Fields
                            identity_type=draft.identity_type,
                            campaign_objective=draft.campaign_objective,
                            target_audience=draft.target_audience,
                            language=draft.language,
                            preferred_cta=draft.preferred_cta,
                            frequency=draft.frequency
                        )
                        db.add(new_identity)
                        db.commit()
                        
                        return GuideNextResponse(
                            assistant_message=f"¡Identidad **{draft.name}** creada exitosamente! 🚀\n\nYa puedes seleccionarla cuando crees nuevas campañas o posts.",
                            options=[GuideOption(label="🏁 Finalizar", value="close_wizard")],
                            next_step=10,
                            state_patch={},
                            status="success"
                        )
                    except Exception as e:
                        logger.error(f"Failed to create identity: {e}")
                        return GuideNextResponse(
                            assistant_message=f"Hubo un error guardando la identidad: {str(e)}",
                            options=[GuideOption(label="Reintentar", value="confirm_create")],
                            next_step=9,
                            state_patch={},
                            status="error"
                        )
            
            if user_value == "restart":
                 return GuideNextResponse(
                    assistant_message="Reiniciando el asistente...",
                    options=[],
                    next_step=1,
                    state_patch={"identity_draft": {}}
                )
                
            # Default fallthrough
            return GuideNextResponse(
                assistant_message="Por favor confirma si quieres crear la identidad.",
                options=[GuideOption(label="✅ Sí, Crear Identidad", value="confirm_create")],
                next_step=9,
                state_patch={}
            )

        return GuideNextResponse(assistant_message="Estado desconocido.", options=[], next_step=1, state_patch={})

    # -------------------------------------------------------------------------
    # STEPS (Reused for Guided & Underlying Logic)
    # -------------------------------------------------------------------------

    async def _step_audience(self, request: GuideNextRequest, next_step: int, log_ctx: dict) -> GuideNextResponse:
        # Step 1 -> 2
        objective = request.user_input
        prompt = f"""
        Actúa como AraPost Manager (Modo Guía).
        Objetivo usuario: "{objective}".
        
        1. Valida el objetivo con empatía (1 frase).
        2. Sugiere 4 audiencias distintas.
        
        JSON: {{ "message": "...", "options": [{{"label": "Audiencia X", "value": "audience_x"}}] }}
        """
        return await self._execute_ai_step(prompt, log_ctx, next_step, {"objective": objective}, lambda: self._fallback_response(next_step))

    async def _step_platform(self, request: GuideNextRequest, next_step: int, log_ctx: dict) -> GuideNextResponse:
        audience = request.user_value or request.user_input
        prompt = f"""
        Objetivo: {request.state.objective}, Audiencia: {audience}.
        Recomienda 1 plataforma ideal y explica por qué en 1 frase.
        JSON: {{ "message": "...", "options": [{{"label": "LinkedIn", "value": "linkedin"}}] }}
        """
        return await self._execute_ai_step(prompt, log_ctx, next_step, {"audience": audience}, lambda: self._fallback_response(next_step))

    async def _step_strategy(self, request: GuideNextRequest, next_step: int, log_ctx: dict) -> GuideNextResponse:
        platform = request.user_value or "linkedin"
        prompt = f"""
        Plataforma: {platform}, Objetivo: {request.state.objective}.
        Propón estrategia (frecuencia/tono).
        JSON: {{ "message": "Propuesta: ...", "options": [{{"label": "OK", "value": "ok"}}, {{"label": "Ajustar", "value": "adjust"}}] }}
        """
        return await self._execute_ai_step(prompt, log_ctx, next_step, {"platform": platform}, lambda: self._fallback_response(next_step))

    async def _step_topics(self, request: GuideNextRequest, next_step: int, log_ctx: dict) -> GuideNextResponse:
        # Lógica legacy de strategy patch
        strategy_patch = {"postsPerDay": 1, "tone": "Profesional"}
        if request.user_value == 'accept_strategy':
            strategy_patch["scheduleStrategy"] = "distributed"
        
        prompt = f"""
        Objetivo: {request.state.objective}. Sugiere 4 temas.
        JSON: {{ "message": "Temas sugeridos:", "options": [{{"label": "Tema 1", "value": "topic_1"}}] }}
        """
        return await self._execute_ai_step(prompt, log_ctx, next_step, strategy_patch, lambda: self._fallback_response(next_step))

    async def _step_confirmation(self, request: GuideNextRequest, next_step: int, log_ctx: dict) -> GuideNextResponse:
        topics = [request.user_value] if request.user_value else ["General"]
        return GuideNextResponse(
            assistant_message=f"Resumen:\n🎯 {request.state.objective}\n👥 {request.state.audience}\n📢 {request.state.platform}\n📝 {topics[0]}\n\n¿Creamos?",
            options=[
                GuideOption(label="🚀 Crear", value="create"),
                GuideOption(label="🔄 Reiniciar", value="restart")
            ],
            next_step=6,
            state_patch={"topics": topics}
        )

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------
    
    async def _execute_ai_step(self, prompt: str, log_ctx: dict, next_step: int, state_patch: dict, fallback_func) -> GuideNextResponse:
        """Wrapper legacy para Guided Mode"""
        return await self._execute_ai_general(prompt, log_ctx, next_step, state_patch, fallback_func)

    async def _execute_ai_step_flexible(self, prompt: str, log_ctx: dict, current_step: int, fallback_func, skip_ai_fallback: bool = False) -> GuideNextResponse:
        """Wrapper para Collaborator Mode (maneja updated_summary y patch flexible)"""
        
        async def logic():
            response_text = await self.ai_service.generate(prompt, skip_fallback=skip_ai_fallback)
            data = self._parse_json(response_text)
            
            # Extraer summary y patch
            updated_summary = data.get("updated_summary", "")
            patch = data.get("state_patch", {})
            if updated_summary:
                patch["conversation_summary"] = updated_summary
            
            # Parsing robusto de opciones (igual que en _execute_ai_general)
            raw_options = data.get("options", [])
            valid_options = []
            for opt in raw_options:
                label = opt.get("label") or opt.get("title") or opt.get("text")
                value = opt.get("value") or label
                
                if label and value:
                    valid_options.append(GuideOption(label=str(label), value=str(value)))

            return GuideNextResponse(
                assistant_message=data.get("message", ""),
                options=valid_options,
                next_step=current_step, # En collaborator no avanzamos steps numéricos necesariamente
                state_patch=patch
            )

        try:
            return await logic()
        except Exception as e:
            if skip_ai_fallback:
                 # Re-raise exception to be handled by caller (who knows how to block)
                 raise e
            logger.error(f"Collaborator AI Error: {e}")
            return fallback_func()

    async def _execute_ai_general(self, prompt: str, log_ctx: dict, next_step: int, state_patch: dict, fallback_func) -> GuideNextResponse:
        """Core AI execution logic"""
        log_ctx["prompt_sent"] = prompt
        log_ctx["ai_used"] = True
        
        try:
            ai_response = await asyncio.wait_for(self.ai_service.generate(prompt), timeout=10.0)
            data = self._parse_json(ai_response)
            
            # Robust options parsing
            raw_options = data.get("options", [])
            valid_options = []
            for opt in raw_options:
                # Handle cases where AI uses "title" instead of "label"
                label = opt.get("label") or opt.get("title") or opt.get("text")
                value = opt.get("value") or label # Fallback value to label if missing
                
                # Normalización forzada para detectar intención de crear
                if label and any(x in str(label).lower() for x in ['opción', 'option', 'crear', 'create', 'propuesta']):
                    if value and value.lower() not in ['retry', 'continue']:
                        value = "create"

                if label and value:
                    valid_options.append(GuideOption(label=str(label), value=str(value)))

            return GuideNextResponse(
                assistant_message=data["message"],
                options=valid_options,
                next_step=next_step,
                state_patch=state_patch
            )
        except Exception as e:
            logger.warning(f"AI Execution Failed: {e}")
            return fallback_func()

    def _parse_json(self, text: str) -> dict:
        original_text = text
        try:
            text = text.strip()
            # Regex robusto para encontrar el primer bloque JSON válido { ... }
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                text = json_match.group(0)
            
            # Limpieza de Trailing Commas (comas al final de arrays/objetos) que rompen json.loads
            # Reemplaza ", ]" por "]" y ", }" por "}"
            text = re.sub(r',\s*([\]}])', r'\1', text)

            return json.loads(text, strict=False)
        except Exception as e:
            logger.error(f"JSON Parse Error. Raw text: '{original_text}'. Error: {e}")
            raise e

    def _fallback_response(self, current_step: int) -> GuideNextResponse:
        return GuideNextResponse(
            assistant_message="Lo siento, hubo un error técnico. ¿Podemos reintentar?",
            options=[GuideOption(label="Reintentar", value="retry")],
            next_step=current_step,
            state_patch={}
        )
