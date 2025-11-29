from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine, Base
from app.models import user, course, student, class_model, enrollment, certificate
from app.services.cleanup_service import CleanupService
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Inicializar scheduler para tarefas automáticas
scheduler = BackgroundScheduler()

try:
    Base.metadata.create_all(bind=engine)
    
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
except Exception as e:

    raise

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="""
## 🎓 CertifyAPI - Sistema de Gerenciamento de Certificados

API completa para instituições de ensino gerenciarem cursos, turmas, inscrições 
e emissão de certificados digitais com sistema anti-fraude baseado em UUID.
    """,
    version="0.0.5",
    contact={
        "name": "Equipe CertifyAPI",
        "url": "https://github.com/ualcz/CertifyAPI",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Informações"])
def read_root():
    """
    Endpoint raiz da API - Informações gerais.
    
    Retorna mensagem de boas-vindas e links úteis para navegação.
    """
    return {
        "message": "Bem-vindo à CertifyAPI! 🎓",
        "version": "0.0.5",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "test_interface": "/static/index.html"
        },
        "endpoints": {
            "api": "/api/v1"
        }
    }

@app.on_event("startup")
def startup_event():
    """
    Tarefas executadas na inicialização da aplicação.
    """
    logger.info("Iniciando CertifyAPI...")
    
    # Configurar limpeza automática diária às 3h da manhã
    scheduler.add_job(
        func=lambda: CleanupService.cleanup_old_files(max_age_hours=24),
        trigger="cron",
        hour=3,
        minute=0,
        id="daily_cleanup",
        name="Limpeza diária de arquivos antigos",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler de limpeza automática iniciado (execução diária às 3h)")
  
    try:
        result = CleanupService.cleanup_old_files(max_age_hours=24)
        logger.info(f"Limpeza inicial: {result['deleted_files']} arquivos removidos, "
                   f"{result['freed_space_mb']} MB liberados")
    except Exception as e:
        logger.error(f"Erro na limpeza inicial: {str(e)}")

@app.on_event("shutdown")
def shutdown_event():
    """
    Tarefas executadas no encerramento da aplicação.
    """
    logger.info("Encerrando CertifyAPI...")
    scheduler.shutdown()
    logger.info("Scheduler encerrado")
