from database.config import db

class Question(db.Model):
    """Modelo para representar uma pergunta em uma sessão de estudo."""
    
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('study_sessions.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    user_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean, default=False)
    difficulty = db.Column(db.String(50), default='medium')
    topic = db.Column(db.String(100))
    
    def __init__(self, session_id, question_text, answer_text, difficulty='medium', topic=None):
        """Inicializa uma nova pergunta."""
        self.session_id = session_id
        self.question_text = question_text
        self.answer_text = answer_text
        self.difficulty = difficulty
        self.topic = topic
    
    def check_answer(self, user_answer):
        """Verifica se a resposta do usuário está correta."""
        self.user_answer = user_answer
        # Comparação simples (pode ser melhorada com IA)
        self.is_correct = user_answer.strip().lower() == self.answer_text.strip().lower()
        return self.is_correct
    
    def to_dict(self):
        """Converte a pergunta para um dicionário (para JSON)."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'question_text': self.question_text,
            'answer_text': self.answer_text,
            'user_answer': self.user_answer,
            'is_correct': self.is_correct,
            'difficulty': self.difficulty,
            'topic': self.topic
        }
    
    def __repr__(self):
        return f'<Question {self.id} - Session {self.session_id}>'

