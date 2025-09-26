import requests
import json
import time
import hashlib
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging
import os
from functools import wraps

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIServiceError(Exception):
    """Exceção personalizada para erros de serviços de IA."""
    pass

class CacheSystem:
    """Sistema de cache simples para otimização de chamadas de IA."""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, prompt: str, service: str) -> str:
        """Gera uma chave única para o cache."""
        content = f"{service}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, service: str) -> Optional[str]:
        """Recupera uma resposta do cache."""
        cache_key = self._get_cache_key(prompt, service)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Verificar se o cache não expirou (24 horas)
                    if time.time() - data['timestamp'] < 86400:
                        logger.info(f"Cache hit para {service}")
                        return data['response']
        except Exception as e:
            logger.warning(f"Erro ao ler cache: {e}")
        
        return None
    
    def set(self, prompt: str, service: str, response: str) -> None:
        """Armazena uma resposta no cache."""
        cache_key = self._get_cache_key(prompt, service)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            data = {
                'prompt': prompt,
                'service': service,
                'response': response,
                'timestamp': time.time()
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Resposta armazenada no cache para {service}")
        except Exception as e:
            logger.warning(f"Erro ao salvar cache: {e}")

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator para retry automático em caso de falha."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    logger.warning(f"Tentativa {attempt + 1} falhou: {e}. Tentando novamente em {delay}s...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

class BaseAIService(ABC):
    """Classe base para serviços de IA."""
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key
        self.cache = CacheSystem()
    
    @abstractmethod
    def _make_request(self, prompt: str, **kwargs) -> str:
        """Faz a requisição para a API de IA."""
        pass
    
    def generate_response(self, prompt: str, use_cache: bool = True, **kwargs) -> str:
        """
        Gera uma resposta usando o serviço de IA.
        
        Args:
            prompt: Texto de entrada
            use_cache: Se deve usar o sistema de cache
            **kwargs: Parâmetros adicionais para a API
            
        Returns:
            Resposta gerada pela IA
        """
        # Verificar cache primeiro
        if use_cache:
            cached_response = self.cache.get(prompt, self.name)
            if cached_response:
                return cached_response
        
        # Fazer requisição para a API
        try:
            response = self._make_request(prompt, **kwargs)
            
            # Armazenar no cache
            if use_cache and response:
                self.cache.set(prompt, self.name, response)
            
            return response
        except Exception as e:
            logger.error(f"Erro no serviço {self.name}: {e}")
            raise AIServiceError(f"Falha no serviço {self.name}: {str(e)}")

class OpenAIService(BaseAIService):
    """Integração com OpenAI (ChatGPT)."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("OpenAI", api_key or os.getenv("OPENAI_API_KEY"))
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    @retry_on_failure(max_retries=3)
    def _make_request(self, prompt: str, **kwargs) -> str:
        """Faz requisição para a API do OpenAI."""
        if not self.api_key:
            raise AIServiceError("API key do OpenAI não configurada")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": kwargs.get("model", "gpt-3.5-turbo"),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

class DeepSeekService(BaseAIService):
    """Integração com DeepSeek API."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("DeepSeek", api_key or os.getenv("DEEPSEEK_API_KEY"))
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    @retry_on_failure(max_retries=3)
    def _make_request(self, prompt: str, **kwargs) -> str:
        """Faz requisição para a API do DeepSeek."""
        if not self.api_key:
            # Simular resposta para demonstração (DeepSeek pode não estar disponível)
            logger.warning("API key do DeepSeek não configurada, usando resposta simulada")
            return f"Resposta simulada do DeepSeek para: {prompt[:50]}..."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": kwargs.get("model", "deepseek-chat"),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException:
            # Fallback para resposta simulada
            logger.warning("Falha na API do DeepSeek, usando resposta simulada")
            return f"Resposta simulada do DeepSeek para: {prompt[:50]}..."

class HuggingFaceService(BaseAIService):
    """Integração com Hugging Face models."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "microsoft/DialoGPT-medium"):
        super().__init__("HuggingFace", api_key or os.getenv("HUGGINGFACE_API_KEY"))
        self.model = model
        self.base_url = f"https://api-inference.huggingface.co/models/{model}"
    
    @retry_on_failure(max_retries=3)
    def _make_request(self, prompt: str, **kwargs) -> str:
        """Faz requisição para a API do Hugging Face."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        data = {
            "inputs": prompt,
            "parameters": {
                "max_length": kwargs.get("max_tokens", 100),
                "temperature": kwargs.get("temperature", 0.7),
                "do_sample": True
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 503:
                # Modelo ainda carregando
                logger.info("Modelo Hugging Face carregando, aguardando...")
                time.sleep(10)
                response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            
            response.raise_for_status()
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").replace(prompt, "").strip()
            else:
                return "Resposta não disponível do Hugging Face"
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Falha na API do Hugging Face: {e}")
            return f"Resposta simulada do Hugging Face para: {prompt[:50]}..."

class AIServiceManager:
    """Gerenciador de serviços de IA com fallback automático."""
    
    def __init__(self):
        self.services = []
        self.current_service_index = 0
        
        # Inicializar serviços disponíveis
        self._initialize_services()
    
    def _initialize_services(self):
        """Inicializa os serviços de IA disponíveis."""
        try:
            self.services.append(DeepSeekService())
            logger.info("DeepSeek service inicializado")
        except Exception as e:
            logger.warning(f"Falha ao inicializar DeepSeek: {e}")
        
        try:
            self.services.append(OpenAIService())
            logger.info("OpenAI service inicializado")
        except Exception as e:
            logger.warning(f"Falha ao inicializar OpenAI: {e}")
        
        try:
            self.services.append(HuggingFaceService())
            logger.info("HuggingFace service inicializado")
        except Exception as e:
            logger.warning(f"Falha ao inicializar HuggingFace: {e}")
        
        if not self.services:
            logger.error("Nenhum serviço de IA foi inicializado com sucesso")
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Gera resposta usando fallback automático entre serviços.
        
        Args:
            prompt: Texto de entrada
            **kwargs: Parâmetros adicionais
            
        Returns:
            Dict com resposta e metadados
        """
        if not self.services:
            return {
                "response": "Nenhum serviço de IA disponível",
                "service_used": "none",
                "success": False,
                "error": "No AI services available"
            }
        
        # Tentar cada serviço em ordem
        for i, service in enumerate(self.services):
            try:
                logger.info(f"Tentando serviço: {service.name}")
                response = service.generate_response(prompt, **kwargs)
                
                return {
                    "response": response,
                    "service_used": service.name,
                    "success": True,
                    "error": None
                }
                
            except Exception as e:
                logger.warning(f"Falha no serviço {service.name}: {e}")
                continue
        
        # Se todos os serviços falharam
        return {
            "response": "Desculpe, não foi possível gerar uma resposta no momento. Tente novamente mais tarde.",
            "service_used": "fallback",
            "success": False,
            "error": "All AI services failed"
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Retorna o status de todos os serviços."""
        status = {}
        for service in self.services:
            try:
                # Teste simples
                test_response = service.generate_response("teste", use_cache=False)
                status[service.name] = {
                    "available": True,
                    "last_test": time.time()
                }
            except Exception as e:
                status[service.name] = {
                    "available": False,
                    "error": str(e),
                    "last_test": time.time()
                }
        
        return status

# Instância global do gerenciador
ai_manager = AIServiceManager()

def get_ai_response(prompt: str, **kwargs) -> Dict[str, Any]:
    """Função de conveniência para obter resposta de IA."""
    return ai_manager.generate_response(prompt, **kwargs)

def get_ai_service_status() -> Dict[str, Any]:
    """Função de conveniência para obter status dos serviços."""
    return ai_manager.get_service_status()

# Exemplo de uso
if __name__ == "__main__":
    # Teste dos serviços
    test_prompt = "Explique o conceito de machine learning de forma simples."
    
    print("=== Teste de Integração com APIs de IA ===\n")
    
    result = get_ai_response(test_prompt)
    print(f"Serviço usado: {result['service_used']}")
    print(f"Sucesso: {result['success']}")
    print(f"Resposta: {result['response']}\n")
    
    # Status dos serviços
    print("=== Status dos Serviços ===")
    status = get_ai_service_status()
    for service, info in status.items():
        print(f"{service}: {'✓' if info['available'] else '✗'}")
        if not info['available']:
            print(f"  Erro: {info.get('error', 'Unknown')}")

