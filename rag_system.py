import os
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from rank_bm25 import BM25Okapi
import openai
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSystem:
    """유니베라 RAG 시스템 클래스"""
    
    def __init__(self, pinecone_api_key: str, pinecone_index_name: str, openai_api_key: str):
        """
        RAG 시스템 초기화
        
        Args:
            pinecone_api_key: Pinecone API 키
            pinecone_index_name: Pinecone 인덱스 이름
            openai_api_key: OpenAI API 키
        """
        # OpenAI 클라이언트 초기화
        logger.info("OpenAI 클라이언트 초기화 중...")
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        
        # E5 벡터 모델 로드
        logger.info("E5 모델 로딩 중...")
        self.model = SentenceTransformer("intfloat/multilingual-e5-base")
        
        # Pinecone 연결
        logger.info("Pinecone 연결 중...")
        self.pc = Pinecone(api_key=pinecone_api_key)
        self.pinecone_index = self.pc.Index(pinecone_index_name)
        
        # Pinecone에서 문서 정보 가져오기
        self.documents = []
        self.filenames = []
        self.load_documents_from_pinecone()
        
        # BM25 인덱스 구축
        self.build_bm25()
        
        logger.info(f"RAG 시스템 준비 완료: {len(self.documents)}개 문서 (Pinecone 기반)")
    
    def load_documents_from_pinecone(self):
        """Pinecone에서 문서 정보 로드"""
        logger.info("Pinecone에서 문서 정보 로딩 중...")
        try:
            # Pinecone 인덱스 통계 가져오기
            stats = self.pinecone_index.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            
            if total_vectors == 0:
                logger.warning("Pinecone 인덱스에 벡터가 없습니다.")
                return
            
            # 모든 벡터의 메타데이터 가져오기 (샘플링)
            # 실제로는 모든 벡터를 가져오는 대신 샘플링하거나 필요한 것만 가져옴
            query_result = self.pinecone_index.query(
                vector=[0.0] * self.model.get_sentence_embedding_dimension(),  # 더미 벡터
                top_k=min(100, total_vectors),  # 최대 100개 또는 전체 벡터 수
                include_metadata=True
            )
            
            for match in query_result["matches"]:
                if 'metadata' in match and 'filename' in match['metadata']:
                    filename = match['metadata']['filename']
                    text = match['metadata'].get('text', '')
                    
                    if filename not in self.filenames:  # 중복 방지
                        self.filenames.append(filename)
                        self.documents.append(text)
            
            logger.info(f"Pinecone에서 {len(self.documents)}개 문서 정보 로드 완료")
            
        except Exception as e:
            logger.error(f"Pinecone에서 문서 로드 실패: {e}")
            # 실패 시 빈 리스트로 초기화
            self.documents = []
            self.filenames = []
    
    def tokenize(self, text: str) -> List[str]:
        """BM25용 토크나이징"""
        # 마크다운 제거
        text = re.sub(r'---.*?---', '', text, flags=re.DOTALL)
        text = re.sub(r'#+ ', '', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # 토크나이징
        tokens = text.lower().split()
        cleaned = []
        for token in tokens:
            clean = re.sub(r'[^\w가-힣]', '', token)
            if len(clean) > 1:
                cleaned.append(clean)
        return cleaned
    
    def build_bm25(self):
        """BM25 인덱스 구축"""
        if not self.documents:
            logger.warning("문서가 없어 BM25 인덱스를 구축할 수 없습니다.")
            self.bm25 = None
            return
            
        logger.info("BM25 인덱스 구축 중...")
        tokenized_docs = [self.tokenize(doc) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)
    
    def embed(self, text: str, is_query: bool = False) -> np.ndarray:
        """E5 임베딩"""
        prefix = "query: " if is_query else "passage: "
        return self.model.encode(prefix + text, normalize_embeddings=True)
    
    def vector_search(self, query: str, top_k: int = 15) -> Dict[str, float]:
        """벡터 검색"""
        try:
            query_vec = self.embed(query, is_query=True)
            results = self.pinecone_index.query(
                vector=query_vec.tolist(), 
                top_k=top_k, 
                include_metadata=True
            )
            
            vector_results = {}
            for match in results["matches"]:
                filename = match['metadata']['filename']
                score = float(match['score'])
                vector_results[filename] = score
            
            return vector_results
        except Exception as e:
            logger.error(f"벡터 검색 오류: {e}")
            return {}
    
    def bm25_search(self, query: str, top_k: int = 10) -> Dict[str, float]:
        """BM25 검색"""
        if self.bm25 is None:
            logger.warning("BM25 인덱스가 없어 키워드 검색을 수행할 수 없습니다.")
            return {}
            
        try:
            tokenized_query = self.tokenize(query)
            if not tokenized_query:
                return {}
            
            scores = self.bm25.get_scores(tokenized_query)
            
            # 상위 top_k개만 선택
            doc_scores = [(i, score) for i, score in enumerate(scores)]
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            
            bm25_results = {}
            for i, score in doc_scores[:top_k]:
                if score > 0:
                    filename = self.filenames[i]
                    bm25_results[filename] = float(score)
            
            return bm25_results
        except Exception as e:
            logger.error(f"BM25 검색 오류: {e}")
            return {}
    
    def normalize_scores(self, scores_dict: Dict[str, float]) -> Dict[str, float]:
        """점수 0-1 정규화"""
        if not scores_dict:
            return {}
        
        values = list(scores_dict.values())
        min_val, max_val = min(values), max(values)
        
        if max_val == min_val:
            return {k: 1.0 for k in scores_dict}
        
        normalized = {}
        for filename, score in scores_dict.items():
            normalized[filename] = (score - min_val) / (max_val - min_val)
        
        return normalized
    
    def hybrid_search(self, query: str, vector_top_k: int = 15, 
                     bm25_top_k: int = 10, vector_weight: float = 0.6, 
                     bm25_weight: float = 0.4, final_top_k: int = 5) -> List[Dict[str, Any]]:
        """하이브리드 검색 실행"""
        logger.info(f"검색어: '{query}'")
        logger.info(f"가중치: 벡터({vector_weight}) + BM25({bm25_weight})")
        
        # 1. 개별 검색 수행
        vector_results = self.vector_search(query, top_k=vector_top_k)
        bm25_results = self.bm25_search(query, top_k=bm25_top_k)
        
        logger.info(f"벡터 검색: {len(vector_results)}개 / BM25 검색: {len(bm25_results)}개")
        
        # 2. 점수 정규화
        vector_norm = self.normalize_scores(vector_results)
        bm25_norm = self.normalize_scores(bm25_results)
        
        # 3. 모든 후보 문서 수집
        all_files = set(vector_norm.keys()) | set(bm25_norm.keys())
        
        # 4. 하이브리드 점수 계산
        hybrid_scores = {}
        for filename in all_files:
            vector_score = vector_norm.get(filename, 0.0)
            bm25_score = bm25_norm.get(filename, 0.0)
            
            hybrid_score = (vector_weight * vector_score) + (bm25_weight * bm25_score)
            hybrid_scores[filename] = hybrid_score
        
        # 5. 상위 결과 정렬
        sorted_results = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:final_top_k]
        
        # 6. 결과 포맷팅 (전체 문서 내용 포함)
        results = []
        for rank, (filename, hybrid_score) in enumerate(sorted_results, 1):
            # 전체 문서 내용 찾기
            full_content = ""
            for i, fname in enumerate(self.filenames):
                if fname == filename:
                    full_content = self.documents[i]
                    break
            
            results.append({
                'rank': rank,
                'filename': filename,
                'hybrid_score': hybrid_score,
                'vector_score': vector_results.get(filename, 0.0),
                'bm25_score': bm25_results.get(filename, 0.0),
                'content': full_content
            })
        
        return results
    
    def create_context(self, search_results: List[Dict[str, Any]]) -> str:
        """검색 결과를 GPT 입력용 컨텍스트로 변환"""
        context_parts = []
        for result in search_results:
            # 마크다운 메타데이터 제거하고 본문만 추출
            content = result['content']
            # YAML front matter 제거
            content = re.sub(r'---.*?---', '', content, flags=re.DOTALL).strip()
            
            context_parts.append(f"## 문서: {result['filename']}\n{content}\n")
        
        return "\n".join(context_parts)
    
    def generate_answer(self, query: str, search_results: List[Dict[str, Any]], 
                       model: str = "gpt-4o-mini", max_tokens: int = 1000) -> str:
        """GPT-4o-mini로 답변 생성"""
        try:
            # 검색 결과를 컨텍스트로 변환
            context = self.create_context(search_results)
            
            # 프롬프트 구성
            system_prompt = """당신은 유니베라 회사에 대한 전문 어시스턴트입니다. 
주어진 문서들을 바탕으로 사용자의 질문에 정확하고 유용한 답변을 제공하세요.

답변 작성 가이드라인:
1. 주어진 문서 내용만을 바탕으로 답변하세요
2. 구체적이고 정확한 정보를 제공하세요
3. 출처가 되는 문서명을 답변 끝에 명시하세요
4. 문서에 없는 내용은 추측하지 마세요
5. 한국어로 자연스럽게 답변하세요
6. 답변을 구조화하여 가독성을 높이세요"""
            
            user_prompt = f"""다음 문서들을 참고하여 질문에 답변해주세요.

질문: {query}

참고 문서들:
{context}

위 문서들을 바탕으로 질문에 대해 정확하고 상세한 답변을 제공해주세요."""
            
            logger.info("GPT-4o-mini 답변 생성 중...")
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.1,  # 일관된 답변을 위해 낮은 temperature
                top_p=0.9
            )
            
            answer = response.choices[0].message.content
            
            # 토큰 사용량 정보
            usage = response.usage
            logger.info(f"토큰 사용량 - 입력: {usage.prompt_tokens}, 출력: {usage.completion_tokens}, 총: {usage.total_tokens}")
            
            return answer
            
        except Exception as e:
            logger.error(f"GPT 답변 생성 오류: {e}")
            return "죄송합니다. 답변 생성 중 오류가 발생했습니다."
    
    def rag_query(self, query: str, vector_weight: float = 0.6, 
                  bm25_weight: float = 0.4, final_top_k: int = 5) -> Dict[str, Any]:
        """전체 RAG 파이프라인 실행"""
        logger.info(f"RAG 질의응답: '{query}'")
        
        # 1. 하이브리드 검색
        search_results = self.hybrid_search(
            query=query,
            vector_weight=vector_weight,
            bm25_weight=bm25_weight,
            final_top_k=final_top_k
        )
        
        # 2. GPT 답변 생성
        answer = self.generate_answer(query, search_results)
        
        return {
            'query': query,
            'search_results': search_results,
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """시스템 정보 반환"""
        return {
            'total_documents': len(self.documents),
            'model_name': 'intfloat/multilingual-e5-base',
            'embedding_dimension': self.model.get_sentence_embedding_dimension(),
            'pinecone_index': self.pinecone_index.describe_index_stats()
        }
