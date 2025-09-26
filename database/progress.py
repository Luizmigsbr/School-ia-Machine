from database.config import db
from datetime import datetime

class Progress(db.Model):
    """Modelo para representar o progresso de um usuário em um tópico."""
    
    __tablename__ = 'progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, topic, score=0):
        """Inicializa um novo registro de progresso."""
        self.user_id = user_id
        self.topic = topic
        self.score = score
        self.last_updated = datetime.utcnow()
    
    def update_score(self, new_score):
        """Atualiza o score do progresso."""
        self.score = new_score
        self.last_updated = datetime.utcnow()
    
    def to_dict(self):
        """Converte o progresso para um dicionário (para JSON)."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topic': self.topic,
            'score': self.score,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    @staticmethod
    def get_user_progress(user_id):
        """Retorna todo o progresso de um usuário."""
        return Progress.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_or_create_progress(user_id, topic):
        """Retorna o progresso existente ou cria um novo."""
        progress = Progress.query.filter_by(user_id=user_id, topic=topic).first()
        if not progress:
            progress = Progress(user_id=user_id, topic=topic)
            db.session.add(progress)
            db.session.commit()
        return progress
    
    def __repr__(self):
        return f'<Progress User {self.user_id} - Topic {self.topic}>'

