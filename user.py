from database.config import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    """Modelo para representar um usuário da plataforma de estudos."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    study_sessions = db.relationship('StudySession', backref='user', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('Progress', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, username, email, password):
        """Inicializa um novo usuário."""
        self.username = username
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        """Define a senha do usuário (hash)."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha fornecida está correta."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Converte o usuário para um dicionário (para JSON)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

