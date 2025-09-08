import os
from typing import Optional

class Config:
    """애플리케이션 설정 클래스"""
    
    # === API 키 설정 ===
    # 환경변수에서 API 키를 가져오거나 직접 설정
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # === Pinecone 설정 ===
    PINECONE_INDEX_NAME = "rag-univera-pinecone-db"
    PINECONE_DIMENSION = 768  # E5-base 모델 차원
    PINECONE_METRIC = "cosine"
    PINECONE_CLOUD = "aws"
    PINECONE_REGION = "us-east-1"
    
    # === 문서 경로 설정 ===
    # Pinecone 기반으로 변경되어 로컬 문서 경로 불필요
    # FOLDER_PATH = None  # 더 이상 사용하지 않음
    
    # === 모델 설정 ===
    EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
    GPT_MODEL = "gpt-4o-mini"
    MAX_TOKENS = 1000
    TEMPERATURE = 0.1
    TOP_P = 0.9
    
    # === 검색 설정 ===
    VECTOR_TOP_K = 15          # 벡터 검색 후보 개수
    BM25_TOP_K = 10           # BM25 검색 후보 개수
    FINAL_TOP_K = 5           # 최종 선정 개수
    VECTOR_WEIGHT = 0.6       # 벡터 검색 가중치
    BM25_WEIGHT = 0.4         # BM25 검색 가중치
    
    # === UI 설정 ===
    PAGE_TITLE = "유니베라 RAG 챗봇"
    PAGE_ICON = "🌿"
    LAYOUT = "wide"
    INITIAL_SIDEBAR_STATE = "expanded"
    
    # === 스트림릿 설정 ===
    STREAMLIT_CONFIG = {
        "theme": {
            "primaryColor": "#667eea",
            "backgroundColor": "#ffffff",
            "secondaryBackgroundColor": "#f0f2f6",
            "textColor": "#262730"
        },
        "server": {
            "port": 8501,
            "enableCORS": False,
            "enableXsrfProtection": False
        }
    }
    
    # === 로깅 설정 ===
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # === 캐시 설정 ===
    CACHE_TTL = 3600  # 1시간 (초)
    MAX_CACHE_SIZE = 100
    
    # === 보안 설정 ===
    ENABLE_API_KEY_VALIDATION = True
    MAX_QUERY_LENGTH = 500
    MAX_MESSAGES_HISTORY = 50
    
    @classmethod
    def validate_config(cls) -> bool:
        """설정 유효성 검사"""
        errors = []
        
        # API 키 검사
        if not cls.PINECONE_API_KEY or cls.PINECONE_API_KEY == "your_pinecone_api_key_here":
            errors.append("Pinecone API 키가 설정되지 않았습니다.")
        
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY == "your_openai_api_key_here":
            errors.append("OpenAI API 키가 설정되지 않았습니다.")
        
        # 문서 경로 검사 (Pinecone 기반으로 변경되어 불필요)
        # if not os.path.exists(cls.FOLDER_PATH):
        #     errors.append(f"문서 폴더 경로가 존재하지 않습니다: {cls.FOLDER_PATH}")
        
        # 검색 설정 검사
        if cls.VECTOR_WEIGHT + cls.BM25_WEIGHT != 1.0:
            errors.append("벡터 가중치와 BM25 가중치의 합이 1.0이어야 합니다.")
        
        if errors:
            print("설정 오류:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    @classmethod
    def get_model_config(cls) -> dict:
        """모델 설정 반환"""
        return {
            "embedding_model": cls.EMBEDDING_MODEL,
            "gpt_model": cls.GPT_MODEL,
            "max_tokens": cls.MAX_TOKENS,
            "temperature": cls.TEMPERATURE,
            "top_p": cls.TOP_P
        }
    
    @classmethod
    def get_search_config(cls) -> dict:
        """검색 설정 반환"""
        return {
            "vector_top_k": cls.VECTOR_TOP_K,
            "bm25_top_k": cls.BM25_TOP_K,
            "final_top_k": cls.FINAL_TOP_K,
            "vector_weight": cls.VECTOR_WEIGHT,
            "bm25_weight": cls.BM25_WEIGHT
        }
    
    @classmethod
    def get_pinecone_config(cls) -> dict:
        """Pinecone 설정 반환"""
        return {
            "api_key": cls.PINECONE_API_KEY,
            "index_name": cls.PINECONE_INDEX_NAME,
            "dimension": cls.PINECONE_DIMENSION,
            "metric": cls.PINECONE_METRIC,
            "cloud": cls.PINECONE_CLOUD,
            "region": cls.PINECONE_REGION
        }
    
    @classmethod
    def update_search_weights(cls, vector_weight: float, bm25_weight: float):
        """검색 가중치 업데이트"""
        if abs((vector_weight + bm25_weight) - 1.0) > 0.01:
            raise ValueError("벡터 가중치와 BM25 가중치의 합이 1.0이어야 합니다.")
        
        cls.VECTOR_WEIGHT = vector_weight
        cls.BM25_WEIGHT = bm25_weight
    
    @classmethod
    def get_quick_questions(cls) -> list:
        """빠른 질문 목록 반환"""
        return [
            "유니베라의 미션과 비전은 무엇인가요?",
            "주요 제품들을 알려주세요",
            "회사 역사를 설명해주세요",
            "브랜드 전략은 어떻게 되나요?",
            "ESG 경영 현황은?",
            "글로벌 진출 현황은?",
            "제품 개발 과정은?",
            "품질 관리 시스템은?",
            "고객 서비스는 어떻게 되나요?",
            "미래 계획은 무엇인가요?"
        ]
    
    @classmethod
    def get_system_prompts(cls) -> dict:
        """시스템 프롬프트 반환"""
        return {
            "default": """당신은 유니베라 회사에 대한 전문 어시스턴트입니다. 
주어진 문서들을 바탕으로 사용자의 질문에 정확하고 유용한 답변을 제공하세요.

답변 작성 가이드라인:
1. 주어진 문서 내용만을 바탕으로 답변하세요
2. 구체적이고 정확한 정보를 제공하세요
3. 출처가 되는 문서명을 답변 끝에 명시하세요
4. 문서에 없는 내용은 추측하지 마세요
5. 한국어로 자연스럽게 답변하세요
6. 답변을 구조화하여 가독성을 높이세요""",
            
            "detailed": """당신은 유니베라 회사에 대한 상세한 정보를 제공하는 전문 어시스턴트입니다.
사용자의 질문에 대해 가능한 한 상세하고 구체적인 답변을 제공하세요.

답변 요구사항:
1. 문서의 모든 관련 정보를 종합하여 답변하세요
2. 구체적인 수치, 날짜, 이름 등을 포함하세요
3. 관련된 다른 정보도 함께 제공하세요
4. 답변을 섹션별로 구조화하세요
5. 출처 문서를 명확히 표시하세요""",
            
            "concise": """당신은 유니베라 회사에 대한 간결한 정보를 제공하는 어시스턴트입니다.
핵심 정보만을 간단명료하게 답변하세요.

답변 원칙:
1. 핵심 정보만을 간단히 답변하세요
2. 불필요한 세부사항은 생략하세요
3. 3-5개의 주요 포인트로 정리하세요
4. 출처는 간단히 표시하세요"""
        }

# 설정 검증
if __name__ == "__main__":
    if Config.validate_config():
        print("✅ 설정이 올바르게 구성되었습니다.")
    else:
        print("❌ 설정에 오류가 있습니다.")
