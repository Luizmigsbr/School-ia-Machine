import os
from flask_sqlalchemy import SQLAlchemy

# Instância global do SQLAlchemy
db = SQLAlchemy()

class DatabaseConfig:
    """Configurações do banco de dados."""
    
    # Configuração para SQLite (desenvolvimento)
    SQLITE_DATABASE_URI = 'sqlite:///platforma_estudos.db'
    
    # Configuração para PostgreSQL (produção)
    POSTGRES_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:password@localhost/platforma_estudos'
    
    # Configuração padrão
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or SQLITE_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def init_app(app):
        """Inicializa a configuração do banco de dados na aplicação Flask."""
        app.config['SQLALCHEMY_DATABASE_URI'] = DatabaseConfig.SQLALCHEMY_DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = DatabaseConfig.SQLALCHEMY_TRACK_MODIFICATIONS
        
        # Inicializa o SQLAlchemy com a aplicação
        db.init_app(app)
        
        return db

def create_tables(app):
    """Cria todas as tabelas do banco de dados."""
    with app.app_context():
        # Importa todos os modelos para garantir que sejam registrados
        from models import User, StudySession, Question, Progress
        
        # Cria todas as tabelas
        db.create_all()
        print("Tabelas do banco de dados criadas com sucesso!")

def drop_tables(app):
    """Remove todas as tabelas do banco de dados."""
    with app.app_context():
        db.drop_all()
        print("Tabelas do banco de dados removidas!")

def reset_database(app):
    """Reseta o banco de dados (remove e recria as tabelas)."""
    drop_tables(app)
    create_tables(app)

