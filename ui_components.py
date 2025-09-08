import streamlit as st
import time
from datetime import datetime
from typing import List, Dict, Any
import json

class ChatUI:
    """채팅 UI 컴포넌트 클래스"""
    
    def __init__(self):
        self.placeholder = None
    
    def display_chat_history(self):
        """채팅 히스토리 표시"""
        # 채팅 컨테이너
        chat_container = st.container()
        
        with chat_container:
            if not st.session_state.messages:
                # 환영 메시지
                st.markdown("""
                <div class="assistant-message">
                    <h4>🌿 유니베라 RAG 챗봇에 오신 것을 환영합니다!</h4>
                    <p>유니베라 회사에 대한 모든 정보를 AI와 함께 알아보세요.</p>
                    <p><strong>예시 질문:</strong></p>
                    <ul>
                        <li>유니베라의 미션과 비전은 무엇인가요?</li>
                        <li>주요 제품들은 무엇인가요?</li>
                        <li>회사 역사를 알려주세요</li>
                        <li>브랜드 전략은 어떻게 되나요?</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                # 채팅 메시지들 표시
                for message in st.session_state.messages:
                    if message["role"] == "user":
                        st.markdown(f"""
                        <div class="user-message">
                            <strong>👤 사용자</strong><br>
                            {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # AI 답변 표시
                        self._display_assistant_message(message)
    
    def _display_assistant_message(self, message: Dict[str, Any]):
        """어시스턴트 메시지 표시"""
        with st.expander(f"🤖 AI 답변 (점수: {message.get('search_score', 'N/A')})", expanded=True):
            st.markdown(message["content"])
            
            # 검색 결과 정보 표시
            if "search_results" in message:
                st.markdown("**📋 참고 문서:**")
                for i, result in enumerate(message["search_results"][:3], 1):
                    st.markdown(f"{i}. **{result['filename']}** (점수: {result['hybrid_score']:.3f})")
    
    def render_input_area(self):
        """입력 영역 렌더링"""
        st.markdown("---")
        
        # 입력 폼
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                user_input = st.text_input(
                    "질문을 입력하세요:",
                    placeholder="예: 유니베라의 미션과 비전은 무엇인가요?",
                    label_visibility="collapsed"
                )
            
            with col2:
                submit_button = st.form_submit_button("전송", use_container_width=True)
        
        # 전송 버튼 클릭 시 처리
        if submit_button and user_input:
            self._handle_user_input(user_input)
    
    def _handle_user_input(self, user_input: str):
        """사용자 입력 처리"""
        # 사용자 메시지 추가
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # AI 답변 생성
        if st.session_state.rag_system:
            with st.spinner("AI가 답변을 생성하는 중..."):
                try:
                    # RAG 시스템으로 답변 생성
                    result = st.session_state.rag_system.rag_query(user_input)
                    
                    # AI 메시지 추가
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "search_results": result["search_results"],
                        "search_score": f"{result['search_results'][0]['hybrid_score']:.3f}" if result["search_results"] else "N/A",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # 페이지 새로고침
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"답변 생성 중 오류가 발생했습니다: {str(e)}")
        else:
            st.error("RAG 시스템이 초기화되지 않았습니다.")
    
    def render_info_panel(self):
        """정보 패널 렌더링"""
        # 레이아웃 설정
        st.markdown("### 🖥️ 레이아웃 설정")
        layout_mode = st.selectbox(
            "화면 레이아웃",
            ["wide", "centered"],
            index=0,
            format_func=lambda x: "넓은 화면" if x == "wide" else "일반 화면"
        )
        st.session_state.layout_mode = layout_mode
        
        # 검색 설정
        st.markdown("### ⚙️ 검색 설정")
        
        # 가중치 슬라이더를 좌우 배치
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown("**벡터 검색**")
            st.markdown("<div style='text-align: center; font-size: 0.8em; color: #666;'>의미적 검색</div>", unsafe_allow_html=True)
        
        with col2:
            vector_weight = st.slider(
                "검색 가중치",
                0.0, 1.0, 0.6, 0.1,
                key="weight_slider",
                label_visibility="collapsed"
            )
            bm25_weight = 1.0 - vector_weight
            
            # 가중치 표시
            st.markdown(f"""
            <div style='text-align: center; font-size: 0.9em; margin-top: -10px;'>
                <span style='color: #667eea; font-weight: bold;'>{vector_weight:.1f}</span> | 
                <span style='color: #764ba2; font-weight: bold;'>{bm25_weight:.1f}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("**BM25 검색**")
            st.markdown("<div style='text-align: center; font-size: 0.8em; color: #666;'>키워드 검색</div>", unsafe_allow_html=True)
        
        # 설정 저장
        if st.button("설정 적용", type="primary", use_container_width=True):
            st.session_state.vector_weight = vector_weight
            st.session_state.bm25_weight = bm25_weight
            st.success("검색 설정이 적용되었습니다!")
        
        # 채팅 히스토리 관리
        st.markdown("### 💬 채팅 관리")
        if st.button("채팅 초기화", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # 히스토리 다운로드
        if st.session_state.messages:
            chat_data = {
                "timestamp": datetime.now().isoformat(),
                "messages": st.session_state.messages
            }
            
            st.download_button(
                label="채팅 내역 다운로드",
                data=json.dumps(chat_data, ensure_ascii=False, indent=2),
                file_name=f"univera_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

class SidebarUI:
    """사이드바 UI 컴포넌트 클래스"""
    
    def render(self):
        """사이드바 렌더링"""
        with st.sidebar:
            # 로고 및 제목
            st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <h2>🌿 유니베라</h2>
                <p>RAG 챗봇 시스템</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 다크모드 토글
            self._render_theme_toggle()
            
            # 시스템 상태
            self._render_system_status()
            
            # 빠른 질문 버튼들
            self._render_quick_questions()
            
            # 도움말
            self._render_help_section()
            
            # 시스템 정보 (하단)
            self._render_system_info()
    
    def _render_theme_toggle(self):
        """테마 토글 렌더링"""
        st.markdown("### 🎨 테마 설정")
        
        # 테마 선택 라디오 버튼
        theme = st.radio(
            "테마 선택",
            ["☀️ 라이트모드", "🌙 다크모드"],
            index=0 if not st.session_state.dark_mode else 1,
            key="theme_selector"
        )
        
        # 테마 변경 감지
        new_dark_mode = theme == "🌙 다크모드"
        if new_dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = new_dark_mode
            st.rerun()
        
        # 현재 테마 표시
        current_theme = "다크모드" if st.session_state.dark_mode else "라이트모드"
        st.info(f"현재 테마: {current_theme}")
    
    def _render_system_status(self):
        """시스템 상태 렌더링"""
        st.markdown("### 🔧 시스템 상태")
        
        if st.session_state.rag_system:
            st.success("✅ RAG 시스템 활성화")
            
            # 연결 상태 확인
            try:
                system_info = st.session_state.rag_system.get_system_info()
                st.info(f"📚 문서: {system_info['total_documents']}개")
                st.info(f"🔍 벡터: {system_info['pinecone_index'].get('total_vector_count', 0)}개")
            except:
                st.warning("⚠️ 시스템 정보 로드 중...")
        else:
            st.error("❌ RAG 시스템 비활성화")
    
    def _render_quick_questions(self):
        """빠른 질문 버튼들 렌더링"""
        st.markdown("### ⚡ 빠른 질문")
        
        quick_questions = [
            "유니베라의 미션과 비전은?",
            "주요 제품들을 알려주세요",
            "회사 역사를 설명해주세요",
            "브랜드 전략은 어떻게 되나요?",
            "ESG 경영 현황은?",
            "글로벌 진출 현황은?"
        ]
        
        for question in quick_questions:
            if st.button(question, use_container_width=True, key=f"quick_{question}"):
                # 질문을 메시지에 추가
                st.session_state.messages.append({
                    "role": "user",
                    "content": question,
                    "timestamp": datetime.now().isoformat()
                })
                
                # AI 답변 생성
                if st.session_state.rag_system:
                    with st.spinner("답변 생성 중..."):
                        try:
                            result = st.session_state.rag_system.rag_query(question)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": result["answer"],
                                "search_results": result["search_results"],
                                "search_score": f"{result['search_results'][0]['hybrid_score']:.3f}" if result["search_results"] else "N/A",
                                "timestamp": datetime.now().isoformat()
                            })
                            st.rerun()
                        except Exception as e:
                            st.error(f"답변 생성 실패: {str(e)}")
    
    def _render_help_section(self):
        """도움말 섹션 렌더링"""
        st.markdown("### ❓ 도움말")
        
        with st.expander("사용 방법"):
            st.markdown("""
            **1. 질문 입력**
            - 하단 입력창에 질문을 입력하세요
            - 자연스러운 한국어로 질문하세요
            
            **2. 빠른 질문**
            - 사이드바의 빠른 질문 버튼을 클릭하세요
            - 자주 묻는 질문들을 빠르게 확인할 수 있습니다
            
            **3. 검색 설정**
            - 우측 패널에서 검색 가중치를 조정할 수 있습니다
            - 벡터 검색과 키워드 검색의 비율을 조정하세요
            """)
        
        with st.expander("기술 정보"):
            st.markdown("""
            **RAG 시스템 구성:**
            - **임베딩 모델**: E5 (multilingual-e5-base)
            - **벡터 DB**: Pinecone
            - **검색 방식**: 하이브리드 (벡터 + BM25)
            - **생성 모델**: GPT-4o-mini
            
            **특징:**
            - 63개 유니베라 관련 문서 인덱싱
            - 실시간 의미적 검색
            - 다국어 지원 (한국어/영어)
            """)
        
        with st.expander("문제 해결"):
            st.markdown("""
            **자주 발생하는 문제:**
            
            **Q: 답변이 생성되지 않아요**
            A: RAG 시스템 초기화를 기다려주세요. 처음 로드 시 시간이 걸릴 수 있습니다.
            
            **Q: 답변이 부정확해요**
            A: 검색 가중치를 조정하거나 질문을 더 구체적으로 해보세요.
            
            **Q: 시스템이 느려요**
            A: 네트워크 상태를 확인하고 잠시 후 다시 시도해주세요.
            """)
    
    def _render_system_info(self):
        """시스템 정보 렌더링 (사이드바 하단)"""
        st.markdown("---")
        st.markdown("### 📊 시스템 정보")
        
        if st.session_state.rag_system:
            try:
                system_info = st.session_state.rag_system.get_system_info()
                
                # 작은 글씨로 정보 표시
                st.markdown(f"""
                <div style='font-size: 0.8em; color: #666;'>
                    <p><strong>📚 문서:</strong> {system_info['total_documents']}개</p>
                    <p><strong>🔍 임베딩:</strong> {system_info['embedding_dimension']}차원</p>
                    <p><strong>📊 벡터:</strong> {system_info['pinecone_index'].get('total_vector_count', 0)}개</p>
                    <p><strong>🤖 모델:</strong> E5-base</p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.markdown(f"""
                <div style='font-size: 0.8em; color: #ff6b6b;'>
                    <p>⚠️ 시스템 정보 로드 실패</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='font-size: 0.8em; color: #ff6b6b;'>
                <p>❌ RAG 시스템 비활성화</p>
            </div>
            """, unsafe_allow_html=True)

class LoadingAnimation:
    """로딩 애니메이션 컴포넌트"""
    
    @staticmethod
    def show_typing_indicator():
        """타이핑 인디케이터 표시"""
        st.markdown("""
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def show_loading_spinner(message: str = "처리 중..."):
        """로딩 스피너 표시"""
        with st.spinner(message):
            time.sleep(0.1)  # 최소한의 지연
