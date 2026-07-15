from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database.database import get_db, engine, Base
from app.core.models import models
from app.core.schemas import schemas
from app.core.services.services import UserService
from app.core.controllers import user_controller, medication_controller, batch_controller, movement_controller, prescription_controller, quick_search_controller, dashboard_controller
from app.core.security.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from fastapi.staticfiles import StaticFiles
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sistema de Gestão de Estoque para Farmácias",
    description="API para gerenciamento de estoque de medicamentos, incluindo controle de lotes, validades e medicamentos controlados.",
    version="0.1.0"
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

app.include_router(user_controller.router, prefix="/api/v1")
app.include_router(medication_controller.router, prefix="/api/v1")
app.include_router(batch_controller.router, prefix="/api/v1")
app.include_router(movement_controller.router, prefix="/api/v1")
app.include_router(prescription_controller.router, prefix="/api/v1")
app.include_router(quick_search_controller.router, prefix="/api/v1")
app.include_router(dashboard_controller.router, prefix="/api/v1")

# Cria as tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="app/templates")

# Dependências
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

# Rotas de Autenticação
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), user_service: UserService = Depends(get_user_service)): 
    logger.info(f"Recebido no /token: username={form_data.username}, password={'*' * len(form_data.password)}")
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_2fa_enabled:
        return {"message": "2FA necessário", "username": user.username}

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token/2fa", response_model=schemas.Token)
async def login_for_access_token_2fa(form_data: OAuth2PasswordRequestForm = Depends(), otp: str = Form(...), user_service: UserService = Depends(get_user_service)):
    logger.info(f"Recebido no /token/2fa: username={form_data.username}, password={'*' * len(form_data.password)}, otp={'*' * len(otp)}")
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_2fa_enabled or not user_service.verify_2fa_code(user, otp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código 2FA inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Tratamento global de exceções
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Ocorreu um erro interno no servidor."}
    )

# ─── Rotas de Frontend (Templates HTML) ───────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login.html", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard.html", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/medications.html", response_class=HTMLResponse)
async def medications_page(request: Request):
    return templates.TemplateResponse("medications.html", {"request": request})

@app.get("/new-medication.html", response_class=HTMLResponse)
async def new_medication_page(request: Request):
    return templates.TemplateResponse("new-medication.html", {"request": request})

@app.get("/edit-medication.html", response_class=HTMLResponse)
async def edit_medication_page(request: Request):
    return templates.TemplateResponse("edit-medication.html", {"request": request})

@app.get("/movements.html", response_class=HTMLResponse)
async def movements_page(request: Request):
    return templates.TemplateResponse("movements.html", {"request": request})

@app.get("/new-movement.html", response_class=HTMLResponse)
async def new_movement_page(request: Request):
    return templates.TemplateResponse("new-movement.html", {"request": request})

@app.get("/quick-search.html", response_class=HTMLResponse)
async def quick_search_page(request: Request):
    return templates.TemplateResponse("quick-search.html", {"request": request})

@app.get("/profile.html", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/2fa-setup.html", response_class=HTMLResponse)
async def two_fa_setup_page(request: Request):
    return templates.TemplateResponse("2fa-setup.html", {"request": request})
