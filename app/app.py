from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import logging
import os
import sys

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos locais
from database.config import DatabaseConfig, db, create_tables
from models import User, StudySession, Question, Progress
from services import get_ai_response, get_ai_service_status, EducationalMLPipeline

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Factory function para criar a aplicação Flask."""
    app = Flask(__name__)
    from services import get_ai_response, get_ai_service_status
    # Configurações
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Configurar banco de dados
    DatabaseConfig.init_app(app)
    
    # Configurar JWT
    jwt = JWTManager(app)
    
    # Configurar CORS
    CORS(app, origins="*")
    
    # Registrar blueprints/rotas
    register_routes(app)
    
    # Criar tabelas do banco de dados
    with app.app_context():
        create_tables(app)
        logger.info("Aplicação Flask inicializada com sucesso!")
    
    return app

def register_routes(app):
    """Registra todas as rotas da aplicação."""
    
    # Rota principal
    @app.route('/')
    def index():
        """Página inicial."""
        return render_template('index.html')
    
    # Rotas de autenticação
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """Registrar novo usuário."""
        try:
            data = request.get_json()
            
            # Validar dados
            if not data or not data.get('username') or not data.get('email') or not data.get('password'):
                return jsonify({'error': 'Username, email e password são obrigatórios'}), 400
            
            # Verificar se usuário já existe
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'error': 'Username já existe'}), 400
            
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email já existe'}), 400
            
            # Criar novo usuário
            user = User(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"Novo usuário registrado: {user.username}")
            
            return jsonify({
                'message': 'Usuário registrado com sucesso',
                'user': user.to_dict()
            }), 201
            
        except Exception as e:
            logger.error(f"Erro no registro: {e}")
            db.session.rollback()
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Login de usuário."""
        try:
            data = request.get_json()
            
            if not data or not data.get('username') or not data.get('password'):
                return jsonify({'error': 'Username e password são obrigatórios'}), 400
            
            # Buscar usuário
            user = User.query.filter_by(username=data['username']).first()
            
            if not user or not user.check_password(data['password']):
                return jsonify({'error': 'Credenciais inválidas'}), 401
            
            # Criar token JWT
            access_token = create_access_token(identity=user.id)
            
            logger.info(f"Login realizado: {user.username}")
            
            return jsonify({
                'access_token': access_token,
                'user': user.to_dict()
            }), 200
            
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    # Rotas de sessões de estudo
    @app.route('/api/sessions', methods=['GET'])
    @jwt_required()
    def get_sessions():
        """Obter sessões de estudo do usuário."""
        try:
            user_id = get_jwt_identity()
            sessions = StudySession.query.filter_by(user_id=user_id).order_by(StudySession.start_time.desc()).all()
            
            return jsonify({
                'sessions': [session.to_dict() for session in sessions]
            }), 200
            
        except Exception as e:
            logger.error(f"Erro ao obter sessões: {e}")
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/api/sessions', methods=['POST'])
    @jwt_required()
    def create_session():
        """Criar nova sessão de estudo."""
        try:
            user_id = get_jwt_identity()
            
            session = StudySession(user_id=user_id)
            db.session.add(session)
            db.session.commit()
            
            logger.info(f"Nova sessão criada para usuário {user_id}")
            
            return jsonify({
                'message': 'Sessão criada com sucesso',
                'session': session.to_dict()
            }), 201
            
        except Exception as e:
            logger.error(f"Erro ao criar sessão: {e}")
            db.session.rollback()
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/api/sessions/<int:session_id>/end', methods=['PUT'])
    @jwt_required()
    def end_session(session_id):
        """Finalizar sessão de estudo."""
        try:
            user_id = get_jwt_identity()
            session = StudySession.query.filter_by(id=session_id, user_id=user_id).first()
            
            if not session:
                return jsonify({'error': 'Sessão não encontrada'}), 404
            
            session.end_session()
            session.calculate_score()
            db.session.commit()
            
            logger.info(f"Sessão {session_id} finalizada")
            
            return jsonify({
                'message': 'Sessão finalizada com sucesso',
                'session': session.to_dict()
            }), 200
            
        except Exception as e:
            logger.error(f"Erro ao finalizar sessão: {e}")
            db.session.rollback()
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    # Rotas de perguntas
    @app.route('/api/sessions/<int:session_id>/questions', methods=['POST'])
    @jwt_required()
    def add_question(session_id):
        """Adicionar pergunta à sessão."""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            # Verificar se a sessão pertence ao usuário
            session = StudySession.query.filter_by(id=session_id, user_id=user_id).first()
            if not session:
                return jsonify({'error': 'Sessão não encontrada'}), 404
            
            if not data or not data.get('question_text') or not data.get('answer_text'):
                return jsonify({'error': 'question_text e answer_text são obrigatórios'}), 400
            
            question = Question(
                session_id=session_id,
                question_text=data['question_text'],
                answer_text=data['answer_text'],
                difficulty=data.get('difficulty', 'medium'),
                topic=data.get('topic')
            )
            
            # Se há resposta do usuário, verificar se está correta
            if data.get('user_answer'):
                question.check_answer(data['user_answer'])
            
            db.session.add(question)
            db.session.commit()
            
            return jsonify({
                'message': 'Pergunta adicionada com sucesso',
                'question': question.to_dict()
            }), 201
            
        except Exception as e:
            logger.error(f"Erro ao adicionar pergunta: {e}")
            db.session.rollback()
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    # Rotas de progresso
    @app.route('/api/progress', methods=['GET'])
    @jwt_required()
    def get_progress():
        """Obter progresso do usuário."""
        try:
            user_id = get_jwt_identity()
            progress_records = Progress.get_user_progress(user_id)
            
            return jsonify({
                'progress': [p.to_dict() for p in progress_records]
            }), 200
            
        except Exception as e:
            logger.error(f"Erro ao obter progresso: {e}")
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/api/progress', methods=['POST'])
    @jwt_required()
    def update_progress():
        """Atualizar progresso do usuário."""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data or not data.get('topic') or 'score' not in data:
                return jsonify({'error': 'topic e score são obrigatórios'}), 400
            
            progress = Progress.get_or_create_progress(user_id, data['topic'])
            progress.update_score(data['score'])
            db.session.commit()
            
            return jsonify({
                'message': 'Progresso atualizado com sucesso',
                'progress': progress.to_dict()
            }), 200
            
        except Exception as e:
            logger.error(f"Erro ao atualizar progresso: {e}")
            db.session.rollback()
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    # Rotas de IA
    @app.route('/api/chat', methods=['POST'])
    @jwt_required()
    def chat_with_ai():
        """Chat com IA."""
        try:
            data = request.get_json()
            
            if not data or not data.get('message'):
                return jsonify({'error': 'Message é obrigatório'}), 400
            
            # Obter resposta da IA
            ai_response = get_ai_response(data['message'])
            
            return jsonify({
                'response': ai_response['response'],
                'service_used': ai_response['service_used'],
                'success': ai_response['success']
            }), 200
            
        except Exception as e:
            logger.error(f"Erro no chat com IA: {e}")
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    @app.route('/api/ai/status', methods=['GET'])
    def ai_status():
        """Status dos serviços de IA."""
        try:
            status = get_ai_service_status()
            return jsonify({'services': status}), 200
            
        except Exception as e:
            logger.error(f"Erro ao obter status da IA: {e}")
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    # Rotas de dashboard
    @app.route('/api/dashboard', methods=['GET'])
    @jwt_required()
    def dashboard():
        """Dados do dashboard do usuário."""
        try:
            user_id = get_jwt_identity()
            
            # Estatísticas gerais
            total_sessions = StudySession.query.filter_by(user_id=user_id).count()
            total_questions = db.session.query(Question).join(StudySession).filter(StudySession.user_id == user_id).count()
            
            # Sessões recentes
            recent_sessions = StudySession.query.filter_by(user_id=user_id).order_by(StudySession.start_time.desc()).limit(5).all()
            
            # Progresso por tópico
            progress_records = Progress.get_user_progress(user_id)
            
            return jsonify({
                'stats': {
                    'total_sessions': total_sessions,
                    'total_questions': total_questions
                },
                'recent_sessions': [s.to_dict() for s in recent_sessions],
                'progress': [p.to_dict() for p in progress_records]
            }), 200
            
        except Exception as e:
            logger.error(f"Erro ao obter dados do dashboard: {e}")
            return jsonify({'error': 'Erro interno do servidor'}), 500
    
    # Tratamento de erros
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint não encontrado'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    # Executar aplicação
    app.run(host='0.0.0.0', port=5000, debug=True)

from services.ai import get_ai_response, get_ai_service_status
