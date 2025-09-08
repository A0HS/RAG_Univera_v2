# 🌿 유니베라 RAG 챗봇

유니베라 회사의 모든 정보를 AI와 함께 알아보는 지능형 질의응답 시스템입니다.

## ✨ 주요 기능

- **🤖 AI 기반 질의응답**: GPT-4o-mini를 활용한 자연스러운 대화
- **🔍 하이브리드 검색**: 벡터 검색(E5) + 키워드 검색(BM25) 결합
- **📚 대규모 문서 처리**: 63개 유니베라 관련 문서 인덱싱
- **🎨 현대적 UI**: ChatGPT 스타일의 직관적인 인터페이스
- **🌙 다크모드 지원**: 사용자 선호에 따른 테마 변경
- **⚡ 실시간 검색**: 빠르고 정확한 정보 검색

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   RAG System    │    │   Vector DB     │
│                 │    │                 │    │   (Pinecone)    │
│ • 채팅 인터페이스  │◄──►│ • E5 임베딩      │◄──►│ • 63개 문서      │
│ • 다크모드       │    │ • 하이브리드 검색  │    │ • 768차원 벡터   │
│ • 빠른 질문      │    │ • GPT-4o-mini   │    │ • 코사인 유사도   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone <repository-url>
cd univera-rag-chatbot
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# API 키 설정
PINECONE_API_KEY=your_pinecone_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# 문서 경로 설정 (선택사항)
RAG_DATABASE_PATH=/path/to/your/documents
```

### 4. 애플리케이션 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

## 📋 사용 방법

### 기본 사용법
1. **질문 입력**: 하단 입력창에 자연스러운 한국어로 질문하세요
2. **빠른 질문**: 사이드바의 빠른 질문 버튼을 클릭하세요
3. **검색 설정**: 우측 패널에서 검색 가중치를 조정하세요

### 예시 질문
- "유니베라의 미션과 비전은 무엇인가요?"
- "주요 제품들을 알려주세요"
- "회사 역사를 설명해주세요"
- "브랜드 전략은 어떻게 되나요?"
- "ESG 경영 현황은?"

## ⚙️ 설정

### 검색 설정
- **벡터 검색 가중치**: 0.0 ~ 1.0 (기본값: 0.6)
- **BM25 검색 가중치**: 0.0 ~ 1.0 (기본값: 0.4)
- **검색 후보 수**: 벡터 15개, BM25 10개, 최종 5개

### 모델 설정
- **임베딩 모델**: `intfloat/multilingual-e5-base`
- **생성 모델**: `gpt-4o-mini`
- **최대 토큰**: 1000
- **온도**: 0.1 (일관된 답변)

## 🛠️ 기술 스택

### 프론트엔드
- **Streamlit**: 웹 애플리케이션 프레임워크
- **CSS3**: 커스텀 스타일링
- **JavaScript**: 인터랙티브 기능

### 백엔드
- **Python 3.8+**: 메인 프로그래밍 언어
- **Sentence Transformers**: E5 임베딩 모델
- **Pinecone**: 벡터 데이터베이스
- **OpenAI API**: GPT-4o-mini 모델
- **BM25**: 키워드 검색 알고리즘

### 데이터 처리
- **Markdown**: 문서 형식
- **YAML**: 메타데이터
- **JSON**: 설정 및 로그

## 📁 프로젝트 구조

```
univera-rag-chatbot/
├── app.py                 # 메인 Streamlit 애플리케이션
├── rag_system.py          # RAG 시스템 핵심 로직
├── ui_components.py       # UI 컴포넌트
├── config.py             # 설정 관리
├── requirements.txt      # Python 의존성
├── README.md            # 프로젝트 문서
└── .env                 # 환경 변수 (생성 필요)
```

## 🔧 개발

### 코드 스타일
```bash
# 코드 포맷팅
black .

# 린팅
flake8 .
```

### 테스트
```bash
# 단위 테스트
pytest tests/
```

### 로깅
- 로그 레벨: INFO
- 로그 형식: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## 🚀 배포

### Streamlit Cloud 배포 (권장)

1. **GitHub 저장소 생성**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Univera RAG Chatbot"
   git branch -M main
   git remote add origin https://github.com/yourusername/univera-rag-chatbot.git
   git push -u origin main
   ```

2. **Streamlit Cloud 연결**
   - [share.streamlit.io](https://share.streamlit.io) 접속
   - GitHub 계정으로 로그인
   - "New app" 클릭
   - 저장소 선택: `yourusername/univera-rag-chatbot`
   - Main file path: `app.py`
   - "Deploy!" 클릭

3. **환경 변수 설정**
   Streamlit Cloud 대시보드에서 다음 환경 변수 설정:
   ```
   PINECONE_API_KEY=your_pinecone_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

### 로컬 배포
```bash
streamlit run app.py --server.port 8501
```

### Docker 배포
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🔒 보안

- API 키는 환경 변수로 관리
- 입력 검증 및 길이 제한
- HTTPS 사용 권장
- 정기적인 의존성 업데이트

## 📊 성능

- **검색 속도**: 평균 2-3초
- **정확도**: 벡터 검색 0.8+ 유사도
- **동시 사용자**: 10-50명 (하드웨어에 따라)
- **메모리 사용량**: 약 2-4GB

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

- **이슈 리포트**: GitHub Issues
- **문서**: README.md
- **이메일**: support@example.com

## 🙏 감사의 말

- **OpenAI**: GPT-4o-mini 모델 제공
- **Pinecone**: 벡터 데이터베이스 서비스
- **Hugging Face**: E5 임베딩 모델
- **Streamlit**: 웹 애플리케이션 프레임워크

---

**유니베라 RAG 챗봇**으로 더 스마트한 정보 검색을 경험해보세요! 🌿✨
