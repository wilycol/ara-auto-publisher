import json
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.domain import UserProfile as DBUserProfile
from app.schemas.guide import UserProfile as SchemaUserProfile
from app.schemas.guide import GuideNextRequest, GuideNextResponse, GuideOption, GuideMode
from app.services.ai_provider_service import AIProviderService
from app.core.logging import logger

class GuideOrchestratorService:
    def __init__(self):
        self.ai_service = AIProviderService()

    async def process_next_step(self, request: GuideNextRequest, db: Session = None) -> GuideNextResponse:
        """
        Orquesta el siguiente paso de la guía conversacional.
        Ahora soporta 3 modos: GUIDED (secuencial), COLLABORATOR (inferencia), EXPERT (directo).
        """
        
        # 0. Cargar Perfil Persistente (si existe y no está en state)
        if db and not request.state.user_profile:
            try:
                # Asumimos Project ID 1 para Single Tenant Local
                db_profile = db.query(DBUserProfile).filter_by(project_id=1).first()
                if db_profile:
                    request.state.user_profile = SchemaUserProfile(
                        profession=db_profile.profession,
                        specialty=db_profile.specialty,
                        bio_summary=db_profile.bio_summary,
                        target_audience_profile=db_profile.target_audience
                    )
            except Exception as e:
                logger.error(f"Error loading user profile: {e}")

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

        try:
            response: GuideNextResponse = None

            if request.mode == GuideMode.COLLABORATOR:
                response = await self._process_collaborator_mode(request, log_context, db)
            elif request.mode == GuideMode.EXPERT:
                response = await self._process_expert_mode(request, log_context, db)
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
    async def _process_collaborator_mode(self, request: GuideNextRequest, log_ctx: dict, db: Session = None) -> GuideNextResponse:
        """
        El corazón del producto (Modo Colaborador).
        Implementa la identidad de ARA Post Manager: directo, propositivo y enfocado en cerrar campañas.
        """
        # 🛡️ PRINCIPIO FUNDAMENTAL: SIN IA REAL = NO HAY MODO COLABORADOR
        # Verificación inicial: ¿Tenemos al menos un proveedor real configurado?
        if not self.ai_service.is_real_ai_available():
            return self._create_blocked_response(request.current_step)

        state = request.state
        user_input = request.user_input or ""
        user_value = request.user_value or ""
        summary = state.conversation_summary or "Inicio de conversación."

        # 🚀 DETECCIÓN DE INTENCIÓN DE CIERRE EXPLÍCITA
        is_create_intent = (user_value == 'create') or ('crear campaña' in user_input.lower())
        
        # Validar si tenemos lo mínimo necesario
        has_minimum_data = state.objective and state.audience and state.platform
        
        # 🕵️ FASE DE DESCUBRIMIENTO (REGLA 1: CONTRATO DE INTELIGENCIA)
        # Si no tenemos perfil de usuario, entramos en modo "Entrevistador"
        has_profile = state.user_profile and (state.user_profile.profession or state.user_profile.bio_summary)
        
        if not has_profile:
            prompt = f"""
            Eres ARA Post Manager. Tu prioridad #1 ahora es CONOCER AL USUARIO (Fase de Descubrimiento).
            NO intentes crear campañas todavía.
            NO asumas nada.

            ESTADO ACTUAL (JSON):
            {state.model_dump_json(exclude={'conversation_summary'})}

            RESUMEN CONTEXTO PREVIO:
            "{summary}"

            INPUT USUARIO:
            "{user_input}"

            TU TAREA:
            Actuar como un estratega senior que está entrevistando a un nuevo cliente.
            
            1. Si es el primer mensaje: Preséntate y explica que necesitas conocerlo para generar buen contenido.
               Pregunta: "¿A qué te dedicas y cuál es tu especialidad principal?"
            
            2. Si ya respondió sobre su profesión:
               Pregunta sobre su audiencia ideal o si tiene material previo (CV, web, etc).
               
            3. Si el usuario subió un archivo (simulado en texto como "[ATTACHMENT: CV.pdf]"):
               Reconoce el archivo y extrae info clave para el perfil.

            OBJETIVO:
            Llenar el objeto 'user_profile' con:
            - profession (e.g. "Consultor de Marketing")
            - specialty (e.g. "B2B SaaS")
            - bio_summary (Resumen de 1 linea)

            FORMATO RESPUESTA FINAL (JSON PURO):
            {{
                "message": "Tu respuesta conversacional aquí...",
                "options": [
                    {{"label": "Soy Coach", "value": "Coach"}},
                    {{"label": "Soy Consultor", "value": "Consultor"}}
                ],
                "state_patch": {{
                    "user_profile": {{
                        "profession": "...",
                        "specialty": "...",
                        "bio_summary": "..."
                    }}
                }},
                "updated_summary": "..."
            }}
            """
        else:
            # MODO ESTÁNDAR (Ya tenemos perfil)
            prompt = f"""
            Eres ARA Post Manager (Modo Colaborador).
            
            PERFIL DEL USUARIO (CONTEXTO CRÍTICO):
            Profesión: {state.user_profile.profession}
            Especialidad: {state.user_profile.specialty}
            Bio: {state.user_profile.bio_summary}

            TU MISIÓN:
            Transformar la intención del usuario en campañas listas para publicar, BASADAS EN SU PERFIL.
            
            ESTADO ACTUAL (JSON):
            {state.model_dump_json(exclude={'conversation_summary'})}
            
            RESUMEN CONTEXTO PREVIO:
            "{summary}"
            
            INPUT USUARIO:
            "{user_input}"
            
            REGLA DE ORO:
            - Usa el perfil del usuario para personalizar TODAS tus sugerencias.
            - Si propone algo fuera de su especialidad, advierte sutilmente.
            - ANTES DE CREAR: Confirma explícitamente el entendimiento (Regla 4).
              "Entiendo que eres [Profesión] y buscas [Objetivo] para [Audiencia]. ¿Correcto?"

            SALIDA ESPERADA (Cuando tengas info suficiente):
            Debes entregar 2-3 opciones de campaña.
            CADA OPCIÓN DEBE INCLUIR AL MENOS 1 POST COMPLETO (Título + Copy).

            FORMATO DEL MENSAJE (Markdown):
            "Aquí tienes [2-3] estrategias listas para publicar (basadas en tu perfil de {state.user_profile.profession}):

            ### Opción A: [Nombre Estrategia]
            **Objetivo:** ...
            **Post Propuesto:**
            > **[Título del Post]**
            > [Cuerpo del post completo...]
            
            ---
            
            ### Opción B: [Nombre Estrategia]
            ...
            
            Elige una opción y la programo ahora mismo."

            OPCIONES DE RESPUESTA (JSON):
            - Si faltan datos críticos: 
              options: [
                 {{"label": "[Respuesta sugerida 1]", "value": "..."}}, 
                 {{"label": "[Respuesta sugerida 2]", "value": "..."}}
              ]
            - Si propones campañas (ESTADO FINAL):
              options: [
                 {{"label": "Opción A (Crear)", "value": "create"}}, 
                 {{"label": "Opción B (Crear)", "value": "create"}},
                 {{"label": "Generar más opciones", "value": "retry"}}
              ]

            FORMATO RESPUESTA FINAL (JSON PURO):
            {{
                "message": "...",
                "options": [...],
                "state_patch": {{ "campo": "valor_inferido" }},
                "updated_summary": "..."
            }}
            
            IMPORTANTE: TU RESPUESTA DEBE SER ÚNICAMENTE EL OBJETO JSON.
            """

        if is_create_intent and has_minimum_data and has_profile:
            # 🛑 REGLA 4: CONFIRMACIÓN ANTES DE CREAR
            # Si el usuario ya confirmó explícitamente (botón "Sí, crear")
            if user_value == 'confirm_create':
                return GuideNextResponse(
                    assistant_message=f"¡Excelente! Generando la campaña para {state.user_profile.profession} ahora mismo...",
                    options=[],
                    next_step=6, 
                    state_patch={}
                )
            
            # Si solo manifestó intención ("crear campaña") pero falta confirmar el resumen
            topics_str = ", ".join(state.topics or ["General"])
            confirmation_msg = (
                f"Entiendo que:\n"
                f"👤 **Perfil:** {state.user_profile.profession} ({state.user_profile.specialty})\n"
                f"🎯 **Objetivo:** {state.objective}\n"
                f"👥 **Audiencia:** {state.audience}\n"
                f"📝 **Temas:** {topics_str}\n\n"
                f"¿Confirmamos esto antes de crear la campaña?"
            )
            
            return GuideNextResponse(
                assistant_message=confirmation_msg,
                options=[
                    GuideOption(label="✅ Sí, crear campaña", value="confirm_create"),
                    GuideOption(label="✏️ Modificar algo", value="modify")
                ],
                next_step=request.current_step, # Nos quedamos aquí hasta confirmar
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
            # Usamos skip_ai_fallback=True para asegurar que NO usamos el LocalFallbackProvider
            response = await self._execute_ai_step_flexible(prompt, log_ctx, request.current_step, fallback, skip_ai_fallback=True)

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
                return await self._execute_ai_step_flexible(prompt, log_ctx, request.current_step, fallback, skip_ai_fallback=True)
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
