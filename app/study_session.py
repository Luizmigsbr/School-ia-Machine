from database.config import db
from datetime import datetime

class StudySession(db.Model):
    """Modelo para representar uma sessão de estudo."""
    
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # em segundos
    score = db.Column(db.Integer, default=0)
    
    # Relacionamentos
    questions = db.relationship('Question', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, user_id):
        """Inicializa uma nova sessão de estudo."""
        self.user_id = user_id
        self.start_time = datetime.utcnow()
    
    def end_session(self):
        """Finaliza a sessão de estudo e calcula a duração."""
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.duration = int((self.end_time - self.start_time).total_seconds())
    
    def calculate_score(self):
        """Calcula o score da sessão baseado nas perguntas corretas."""
        if not self.questions:
            return 0
        
        correct_answers = sum(1 for q in self.questions if q.is_correct)
        total_questions = len(self.questions)
        
        if total_questions > 0:
            self.score = int((correct_answers / total_questions) * 100)
        else:
            self.score = 0
        
        return self.score
    
    def to_dict(self):
        """Converte a sessão para um dicionário (para JSON)."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'score': self.score,
            'questions_count': len(self.questions) if self.questions else 0
        }
    
    def __repr__(self):
        return f'<StudySession {self.id} - User {self.user_id}>'

