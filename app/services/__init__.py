# Exemplo de como seu __init__.py deve ficar:

# Mantenha todas as outras importações que você já tinha:
from .get_ai_response import get_ai_response # Se você corrigiu este erro
from .status import get_ai_service_status

# IMPORTAÇÃO NECESSÁRIA PARA CORRIGIR O NOVO ERRO:
from .pipelines import EducationalMLPipeline 

# Isso "expõe" a classe EducationalMLPipeline, permitindo que o 'app.py' a encontre.
