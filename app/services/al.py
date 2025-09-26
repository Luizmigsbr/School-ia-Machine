import os
from typing import Optional, Dict, Any
import requests

# Configurações da API - você precisará definir essas variáveis de ambiente
EL_API_KEY = os.getenv('EL_API_KEY', 'sua_chave_api_aqui')
EL_API_URL = os.getenv('EL_API_URL', 'https://api.example.com/el')
EL_SERVICE_STATUS_URL = os.getenv('EL_SERVICE_STATUS_URL', 'https://api.example.com/status')

class Educational:
    """Classe para serviços educacionais"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or EL_API_KEY
        self.base_url = EL_API_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_response(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Obtém resposta do serviço EL baseado no prompt
        
        Args:
            prompt: Texto de entrada para a IA
            context: Contexto adicional (opcional)
        
        Returns:
            Resposta da API
        """
        try:
            payload = {
                'prompt': prompt,
                'context': context or {}
            }
            
            response = requests.post(
                f"{self.base_url}/generate",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'Erro na API: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {
                'error': f'Erro na requisição: {str(e)}'
            }


def get_el_response(prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Função principal para obter resposta do serviço EL
    
    Args:
        prompt: Texto de entrada
        context: Contexto adicional
        
    Returns:
        Resposta formatada
    """
    el_service = Educational()
    return el_service.get_response(prompt, context)


def get_el_service_status() -> Dict[str, Any]:
    """
    Verifica o status do serviço EL
    
    Returns:
        Status do serviço
    """
    try:
        response = requests.get(
            EL_SERVICE_STATUS_URL,
            timeout=10
        )
        
        return {
            'status': 'online' if response.status_code == 200 else 'offline',
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds()
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'status': 'offline',
            'error': str(e)
        }


# Exemplo de uso (opcional - para testes)
if __name__ == "__main__":
    # Teste do status
    status = get_el_service_status()
    print("Status do serviço:", status)
    
    # Teste de resposta
    response = get_el_response("Olá, como você está?")
    print("Resposta:", response)
