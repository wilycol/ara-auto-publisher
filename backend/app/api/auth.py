from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.config import get_settings
from app.models.domain import ConnectedAccount, Project
from app.core.security import encrypt_token
from app.core.logging import logger
from app.schemas.common.base import StandardResponse
from pydantic import BaseModel
import httpx
import urllib.parse
from datetime import datetime, timedelta

router = APIRouter()
settings = get_settings()

class ConnectedAccountResponse(BaseModel):
    id: int
    provider: str
    provider_name: str | None
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/accounts", response_model=StandardResponse[List[ConnectedAccountResponse]])
def list_connected_accounts(db: Session = Depends(get_db)):
    """Lista todas las cuentas conectadas"""
    accounts = db.query(ConnectedAccount).filter(ConnectedAccount.active == True).all()
    return StandardResponse(data=accounts)

@router.delete("/accounts/{account_id}", response_model=StandardResponse[bool])
def disconnect_account(account_id: int, db: Session = Depends(get_db)):
    """Desconecta (elimina lógicamente) una cuenta"""
    account = db.query(ConnectedAccount).filter(ConnectedAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Opción A: Hard delete
    # db.delete(account)
    
    # Opción B: Soft delete / Deactivate
    account.active = False
    account.access_token_encrypted = None # Borrar tokens por seguridad
    
    db.commit()
    return StandardResponse(data=True, message="Cuenta desconectada exitosamente")

@router.get("/linkedin/login")
def linkedin_login(project_id: int = 1): # Default to 1 if not provided
    """
    Genera la URL de autorización de LinkedIn
    """
    if not settings.LINKEDIN_CLIENT_ID:
        logger.error("Attempted LinkedIn login but LINKEDIN_CLIENT_ID is missing")
        # Retornamos error controlado para que el frontend pueda mostrar instrucciones
        raise HTTPException(
            status_code=500, 
            detail="LINKEDIN_CLIENT_ID no configurado en el servidor. Revise el archivo .env"
        )

    logger.info(f"Generating LinkedIn OAuth URL for Project ID: {project_id}")

    params = {
        "response_type": "code",
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "state": str(project_id), # Pasamos project_id como state para saber a quién vincular
        "scope": "r_liteprofile w_member_social"
    }
    
    url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"
    return {"url": url}

@router.get("/linkedin/callback")
async def linkedin_callback(
    code: str = None, 
    state: str = None, 
    error: str = None, 
    error_description: str = None, 
    db: Session = Depends(get_db)
):
    """
    Intercambia el código por un token y guarda la cuenta
    """
    # 0. Manejo de Errores devueltos por LinkedIn (ej: usuario cancela)
    if error:
        logger.warning(f"LinkedIn Auth Error: {error} - {error_description}")
        # Retornamos un HTML o JSON amigable, no una excepción cruda
        raise HTTPException(
            status_code=400, 
            detail=f"LinkedIn Authorization Failed: {error_description or error}"
        )

    # 1. Validaciones Básicas
    if not code:
        logger.error("OAuth Callback received without 'code'")
        raise HTTPException(status_code=400, detail="Missing authorization code")
    if not state:
        logger.error("OAuth Callback received without 'state'")
        raise HTTPException(status_code=400, detail="Missing state parameter (security check)")

    try:
        project_id = int(state)
    except ValueError:
        logger.error(f"Invalid state (project_id) received: {state}")
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    logger.info(f"Processing LinkedIn callback for Project ID: {project_id}")

    # 2. Exchange code for access token
    try:
        async with httpx.AsyncClient() as client:
            token_res = await client.post("https://www.linkedin.com/oauth/v2/accessToken", data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "client_secret": settings.LINKEDIN_CLIENT_SECRET
            })
    except httpx.RequestError as e:
        logger.error(f"Network Error during Token Exchange: {str(e)}")
        raise HTTPException(status_code=503, detail="Failed to connect to LinkedIn")

    if token_res.status_code != 200:
        logger.error(f"LinkedIn Token Exchange Failed: {token_res.status_code} - {token_res.text}")
        raise HTTPException(status_code=400, detail="Failed to retrieve access token from LinkedIn")
        
    try:
        token_data = token_res.json()
    except Exception:
        logger.error("Malformed JSON from LinkedIn Token Endpoint")
        raise HTTPException(status_code=502, detail="Invalid response from LinkedIn")

    access_token = token_data.get("access_token")
    expires_in = token_data.get("expires_in", 3600 * 24 * 60) # Default 60 days
    
    if not access_token:
        logger.error("Missing access_token in LinkedIn response")
        raise HTTPException(status_code=400, detail="LinkedIn did not return an access token")

    # 3. Get User Profile (to identify account)
    # Note: 'r_liteprofile' uses /v2/me endpoint
    try:
        async with httpx.AsyncClient() as client:
            profile_res = await client.get("https://api.linkedin.com/v2/me", headers={
                "Authorization": f"Bearer {access_token}"
            })
    except httpx.RequestError as e:
        logger.error(f"Network Error during Profile Fetch: {str(e)}")
        raise HTTPException(status_code=503, detail="Failed to fetch LinkedIn profile")
        
    if profile_res.status_code != 200:
        logger.error(f"LinkedIn Profile Fetch Failed: {profile_res.status_code} - {profile_res.text}")
        raise HTTPException(status_code=400, detail="Failed to verify LinkedIn identity")
        
    profile_data = profile_res.json()
    linkedin_id = profile_data.get("id")
    first_name = profile_data.get("localizedFirstName", "")
    last_name = profile_data.get("localizedLastName", "")
    full_name = f"{first_name} {last_name}".strip()
    
    if not linkedin_id:
        logger.error("Missing ID in LinkedIn Profile response")
        raise HTTPException(status_code=400, detail="Incomplete profile data from LinkedIn")

    # 4. Save/Update Account in DB (Securely)
    account = db.query(ConnectedAccount).filter(
        ConnectedAccount.project_id == project_id,
        ConnectedAccount.provider == "linkedin",
        ConnectedAccount.external_account_id == linkedin_id
    ).first()
    
    if not account:
        account = ConnectedAccount(
            project_id=project_id,
            provider="linkedin",
            external_account_id=linkedin_id
        )
        db.add(account)
    
    account.provider_name = full_name
    account.access_token_encrypted = encrypt_token(access_token)
    
    # Refresh Token (si viene)
    refresh_token = token_data.get("refresh_token")
    if refresh_token:
        account.refresh_token_encrypted = encrypt_token(refresh_token)
        
    # Expires At
    if expires_in:
        account.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
    account.scopes = "r_liteprofile w_member_social"
    account.active = True
    
    db.commit()
    db.refresh(account)
    
    logger.info(f"Successfully connected LinkedIn account: {linkedin_id} ({full_name}) for Project {project_id}")
    
    # Redirigir al frontend
    frontend_url = f"{settings.FRONTEND_URL}/connections?status=success&provider=linkedin"
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=frontend_url)
