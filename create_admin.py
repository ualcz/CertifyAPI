"""
Script para criar usuário administrador padrão no banco de dados
Executa: python create_admin.py
"""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash

def create_admin_user():
    """Cria usuário administrador padrão se não existir"""
    
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    # Criar sessão
    db: Session = SessionLocal()
    
    try:
        # Verificar se admin já existe
        admin_email = "admin@example.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if existing_admin:
            print(f"✓ Usuário admin já existe: {admin_email}")
            print(f"  ID: {existing_admin.id}")
            print(f"  Ativo: {existing_admin.is_active}")
            print(f"  Superuser: {existing_admin.is_superuser}")
            return
        
        # Criar novo admin
        admin_password = "admin123"
        hashed_password = get_password_hash(admin_password)
        
        admin_user = User(
            email=admin_email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("=" * 60)
        print("✓ Usuário administrador criado com sucesso!")
        print("=" * 60)
        print(f"Email:    {admin_email}")
        print(f"Senha:    {admin_password}")
        print(f"ID:       {admin_user.id}")
        print(f"Ativo:    {admin_user.is_active}")
        print(f"Admin:    {admin_user.is_superuser}")
        print("=" * 60)
        print("\nVocê pode fazer login com estas credenciais em:")
        print("http://localhost:8000/static/index.html")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Erro ao criar admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
