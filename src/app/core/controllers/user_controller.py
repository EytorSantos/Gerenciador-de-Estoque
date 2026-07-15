from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database.database import get_db
from app.core.schemas import schemas
from app.core.services.services import UserService
from app.core.security.two_factor_auth import get_totp_provisioning_uri
from app.core.dependencies.dependencies import get_current_active_user, get_current_admin
from app.core.models.models import User, UserRole

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, user_service: UserService = Depends(lambda db=Depends(get_db): UserService(db)), current_user: User = Depends(get_current_admin)):
    db_user = user_service.get_user_by_username(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Nome de usuário já registrado")
    return user_service.create_user(user)

@router.get("/me/", response_model=schemas.UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def read_user(user_id: int, user_service: UserService = Depends(lambda db=Depends(get_db): UserService(db)), current_user: User = Depends(get_current_admin)):
    user = user_service.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.get("/", response_model=List[schemas.UserResponse])
async def read_users(skip: int = 0, limit: int = 100, user_service: UserService = Depends(lambda db=Depends(get_db): UserService(db)), current_user: User = Depends(get_current_admin)):
    users = user_service.get_multi(skip=skip, limit=limit)
    return users

@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(user_id: int, user: schemas.UserUpdate, user_service: UserService = Depends(lambda db=Depends(get_db): UserService(db)), current_user: User = Depends(get_current_active_user)):
    # Se não for admin, só pode atualizar a si mesmo
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    db_user = user_service.get(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user_service.update_user(db_user, user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, user_service: UserService = Depends(lambda db=Depends(get_db): UserService(db)), current_user: User = Depends(get_current_admin)):
    user = user_service.delete(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return

@router.post("/me/2fa/generate-secret", response_model=schemas.TwoFactorAuthSetup)
async def generate_2fa_secret(current_user: User = Depends(get_current_active_user), user_service: UserService = Depends(lambda db=Depends(get_db): UserService(db))):
    if current_user.is_2fa_enabled:
        raise HTTPException(status_code=400, detail="2FA já está habilitado para este usuário.")
    if current_user.two_factor_secret:
        secret = current_user.two_factor_secret
    else:
        secret = user_service.generate_2fa_secret(current_user)
    
    qrcode_uri = get_totp_provisioning_uri(secret, current_user.email, "FarmaciaStock")
    return {"secret": secret, "qrcode_uri": qrcode_uri}

@router.post("/me/2fa/enable", response_model=schemas.UserResponse)
async def enable_2fa(two_fa_verify: schemas.TwoFactorAuthVerify, current_user: User = Depends(get_current_active_user), user_service: UserService = Depends(lambda db=Depends(get_db): UserService(db))):
    if current_user.is_2fa_enabled:
        raise HTTPException(status_code=400, detail="2FA já está habilitado.")
    if not current_user.two_factor_secret:
        raise HTTPException(status_code=400, detail="Segredo 2FA não gerado. Gere um segredo primeiro.")
    
    if user_service.enable_2fa(current_user, two_fa_verify.otp):
        return current_user
    raise HTTPException(status_code=400, detail="Código OTP inválido.")

@router.post("/me/2fa/disable", response_model=schemas.UserResponse)
async def disable_2fa(two_fa_disable: schemas.TwoFactorAuthDisable, current_user: User = Depends(get_current_active_user), user_service: UserService = Depends(lambda db=Depends(get_db): UserService(db))):
    if not current_user.is_2fa_enabled:
        raise HTTPException(status_code=400, detail="2FA não está habilitado.")
    
    if user_service.disable_2fa(current_user, two_fa_disable.otp):
        return current_user
    raise HTTPException(status_code=400, detail="Código OTP inválido.")
