# services/__init__.py

# IMPORTANTE: A importação deve ser relativa (usando o ponto .)
# Se todas as funções estiverem em ai.py:
from .ai import get_ai_response, get_ai_service_status, EducationalMLPipeline 

# Se estiverem em arquivos diferentes, você importa de cada um:
# from .ai_utils import get_ai_response, get_ai_service_status
# from .ml import EducationalMLPipeline
