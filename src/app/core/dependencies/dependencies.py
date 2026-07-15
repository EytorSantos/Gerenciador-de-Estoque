from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.database.database import get_db
from app.core.models.models import User, UserRole
from app.core.schemas.schemas import TokenData
from app.core.security.jwt import SECRET_KEY, ALGORITHM
from app.core.services.services import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user_service = UserService(db)
    user = user_service.get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user

def get_current_pharmacist(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.PHARMACIST:
        raise HTTPException(status_code=403, detail="Acesso restrito a farmacêuticos")
    return current_user

def get_current_admin(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return current_user

def get_current_stock_manager(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.STOCK_MANAGER:
        raise HTTPException(status_code=403, detail="Acesso restrito a gerentes de estoque")
    return current_user

def get_current_clerk(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.CLERK:
        raise HTTPException(status_code=403, detail="Acesso restrito a balconistas")
    return current_user
